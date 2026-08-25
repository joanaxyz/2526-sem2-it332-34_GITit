# Production Deployment

This guide provides two supported deployment paths:

1. A reference Linux host using Docker Compose and a TLS reverse proxy.
2. A container platform using the same backend and frontend Dockerfiles.

The application topology is:

```text
browser -> TLS proxy -> frontend Nginx -> /api -> Django/Gunicorn
                                      -> /assets, /cosmetics, /audio
                                  Django -> PostgreSQL
                                         -> Redis
```

Only the frontend service needs to be public. The backend, PostgreSQL, and
Redis should be private. The frontend and API are same-origin by default, so
the frontend is built with `VITE_API_BASE_URL=/api`.

## 1. Production prerequisites

Before starting, prepare:

- A Linux host with Docker Engine and the Docker Compose plugin, or a platform
  that can deploy Dockerfiles.
- A domain such as `app.example.com`, with its DNS A/AAAA record pointing to
  the deployment endpoint.
- PostgreSQL 16 or newer. A managed database with automated backups is
  strongly recommended.
- Redis 7 or newer. It is used for shared authentication revocation, caching,
  and throttling across workers and replicas.
- TLS termination at the host proxy or platform load balancer.
- SMTP credentials if password-reset email must work.

For an initial 100-concurrent-user staging test, a reasonable starting point is
4 vCPU and 8 GB RAM for the application host, with PostgreSQL and Redis managed
separately. This is a starting configuration, not a capacity guarantee; tune it
from the load-smoke results described below.

## 2. Prepare a clean release

Deploy a clean commit, not the current contents of a developer working tree:

```bash
git clone YOUR_REPOSITORY_URL git-it
cd git-it
git checkout YOUR_COMMIT_SHA
git status --short
```

`git status --short` must print nothing. Confirm CI passed for the same commit,
then run the deployment-specific guards:

```bash
python3 scripts/check_runtime_assets.py --require-tracked
python3 scripts/check_django_deploy.py
```

For a complete local preflight, install Node.js 22 and run:

```bash
cd frontend
npm ci
npm run lint
npm run lint:dead
npm test
npm run build
cd ..
```

The runtime-asset guard prevents local-only media from passing while its file
is absent from Git or excluded from a source archive.

### Optimize runtime art when source art changes

The checked-in runtime images are already optimized; deployment does not need
to run these commands. When an artist replaces source files under a `raw`
directory or replaces an actor animation sheet, regenerate the browser copies
before committing:

```bash
python3 scripts/assets/optimize_static_avatars.py --apply
python3 scripts/assets/compact_actor_sheets.py --apply
python3 scripts/check_runtime_assets.py --require-tracked
```

The static-image command downsizes and palette-compresses battle avatars and
profile portraits while leaving their `raw` originals untouched. The actor
command slices each 5x5 grid in memory, finds the visible-pixel union for all
animations belonging to that actor, keeps a two-pixel transparent margin,
then rebuilds the sheets and updates their frame metadata. A shared crop per
actor prevents animation scaling or position jitter. Skill-effect sheets are
excluded because their transparent bounds are part of their authored battle
placement.

Review the regenerated art in the application and run the frontend test/build
preflight above before committing it. Both tools are previews unless `--apply`
is supplied.

## 3. Configure production secrets

Create the ignored production environment file:

```bash
cp backend/.env.production.example backend/.env.production
chmod 600 backend/.env.production
```

Generate a Django secret without putting it in shell history:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Edit `backend/.env.production`. Replace every example value. For the same-origin
domain `https://app.example.com`, configure at least:

```dotenv
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=YOUR_GENERATED_SECRET
DEPLOYMENT_VERSION=YOUR_COMMIT_SHA
DJANGO_ALLOWED_HOSTS=app.example.com
DJANGO_CORS_ALLOWED_ORIGINS=https://app.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://app.example.com
FRONTEND_BASE_URL=https://app.example.com

DATABASE_URL=postgresql://USER:URL_ENCODED_PASSWORD@DATABASE_HOST:5432/DATABASE_NAME
REDIS_URL=rediss://USER:URL_ENCODED_PASSWORD@REDIS_HOST:6379/0

DJANGO_MIGRATE_ON_STARTUP=False
DJANGO_TRUST_PROXY_HEADERS=True
DJANGO_TRUSTED_PROXY_IPS=172.16.0.0/12

JWT_COOKIE_DOMAIN=app.example.com
JWT_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

Use `redis://` instead of `rediss://` only for a private Redis endpoint that
does not offer TLS. URL-encode special characters in database and Redis
passwords. Never commit `backend/.env.production`.

`DJANGO_TRUSTED_PROXY_IPS` must cover only the direct proxy network visible to
Django. `172.16.0.0/12` covers standard private Docker bridge ranges for the
reference Compose deployment; use the platform's documented proxy ranges on a
hosted platform. Do not use `0.0.0.0/0`.

The default Gunicorn capacity is 3 workers x 2 threads. The maximum normal
database connections per backend replica is therefore approximately six. Keep
the total across all replicas, administration jobs, and migrations below the
database or PgBouncer limit.

## 4. Build the images

The repository includes `compose.production.yml`, which builds each image from
the correct context:

```bash
docker compose -f compose.production.yml build --pull
```

Equivalent standalone image builds are:

```bash
docker build -f backend/Dockerfile -t git-it-backend:YOUR_COMMIT_SHA backend
docker build -f frontend/Dockerfile -t git-it-frontend:YOUR_COMMIT_SHA frontend
```

The frontend image contains all runtime media under `frontend/public` and
compiled assets under `frontend/src/assets`. The application does not accept
runtime media uploads, so no media volume or object-storage bucket is required.

## 5. Back up and migrate the database

Before every rollout, verify a current PostgreSQL backup exists and record the
currently deployed commit/image tag.

Run migrations exactly once, before starting or scaling web replicas:

```bash
docker compose -f compose.production.yml run --rm --no-deps \
  --entrypoint sh backend \
  -c 'python manage.py check_runtime_config && python manage.py migrate --noinput'
```

Keep `DJANGO_MIGRATE_ON_STARTUP=False` for this workflow. It prevents multiple
backend replicas from racing to apply migrations during a rolling deployment.

## 6. Start the application

Start one backend and the frontend:

```bash
docker compose -f compose.production.yml up -d --remove-orphans
docker compose -f compose.production.yml ps
```

The reference Compose file exposes only the frontend on
`127.0.0.1:8080`. PostgreSQL, Redis, and the backend remain unexposed. Inspect
startup and health status with:

```bash
docker compose -f compose.production.yml logs --tail=200 backend frontend
curl --fail http://127.0.0.1:8080/nginx-health
curl --fail http://127.0.0.1:8080/api/health/live/
curl --fail http://127.0.0.1:8080/api/health/ready/
```

`/api/health/live/` verifies the Django process. `/api/health/ready/` also
checks PostgreSQL and Redis and must return HTTP 200 before traffic is enabled.

## 7. Seed a new installation

Only a new database needs the initial curriculum and command-library seed.
These commands are idempotent and may also be used when a release intentionally
updates the built-in curriculum:

```bash
docker compose -f compose.production.yml exec backend \
  python manage.py seed_curriculum --validate
docker compose -f compose.production.yml exec backend \
  python manage.py seed_command_library
```

Do not use `seed_curriculum --reset` in production. It removes dependent
practice and progress rows and is disabled by the default production settings.

Create the first administrator interactively if needed:

```bash
docker compose -f compose.production.yml exec backend \
  python manage.py createsuperuser
```

## 8. Enable HTTPS

Place a TLS reverse proxy in front of `127.0.0.1:8080`. For example, a host
Caddy configuration is:

```caddyfile
app.example.com {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8080
}
```

Allow inbound TCP ports 80 and 443 in the host and cloud firewalls, then reload
the proxy. Do not expose port 8000 or the PostgreSQL/Redis ports publicly.

Verify the public path and forwarded HTTPS scheme:

```bash
curl --fail --show-error https://app.example.com/nginx-health
curl --fail --show-error https://app.example.com/api/health/ready/
curl --fail --show-error \
  https://app.example.com/cosmetics/story-worlds/arcane-spire/monsters/monster-01/portrait.png \
  --output /dev/null
curl --fail --show-error \
  https://app.example.com/audio/battle/background/outside-battle-loop.wav \
  --output /dev/null
```

Also open the browser developer tools and confirm that document, API, portrait,
sprite-sheet, and audio requests return the expected content type rather than
the SPA's `index.html` fallback.

## 9. Application smoke test

Before announcing the release, test all of the following through the public
HTTPS domain:

1. Register or sign in and refresh the page while authenticated.
2. Load the home page and verify the profile avatar.
3. Open the story map and verify companion and monster portraits.
4. Start one adventure and submit a command.
5. Start one challenge and submit a command.
6. Open the shop and verify companion/story presentation.
7. Sign out and sign back in.
8. Request a password reset if SMTP is configured.
9. Confirm there are no unexpected `/cosmetics`, `/audio`, `/assets`, or API
   404/5xx responses in the browser network panel.

## 10. Validate 100 concurrent users

Run this against a staging environment backed by production-sized PostgreSQL
and Redis:

```bash
python3 scripts/load_smoke.py https://staging.example.com \
  --users 100 \
  --duration 60 \
  --path /api/health/ready/ \
  --path /api/chapters/ \
  --max-error-rate 0.01 \
  --max-p95-ms 750
```

For authenticated read endpoints, set `LOAD_TEST_BEARER_TOKEN` in the process
environment. Use a staging-only account; the script never prints the token, and
you should unset it afterward.

The readiness-only result validates routing, PostgreSQL, Redis, and web-worker
concurrency. It does not represent gameplay by itself, so add representative
read endpoints and separately test state-changing gameplay flows using isolated
staging users. Do not load-test production without confirming the traffic
window and database headroom.

Watch during the test:

- request throughput, p95/p99 latency, and 5xx rate;
- backend CPU, memory, worker timeouts, and restarts;
- PostgreSQL connections, CPU, slow queries, lock waits, and disk I/O;
- Redis latency, connection errors, and memory;
- frontend 404 rates and host/network egress.

Scale backend replicas or Gunicorn workers only from this evidence. PgBouncer
in transaction mode is supported by the production defaults that disable
prepared statements and server-side cursors.

## 11. Deploy an update

On the host, check out the exact new commit and repeat the guards and build:

```bash
git fetch --all --prune
git checkout YOUR_NEW_COMMIT_SHA
python3 scripts/check_runtime_assets.py --require-tracked
python3 scripts/check_django_deploy.py
docker compose -f compose.production.yml build --pull
```

Back up PostgreSQL, run the single migration command from section 5, and then
replace the containers:

```bash
docker compose -f compose.production.yml up -d --remove-orphans
docker compose -f compose.production.yml ps
docker compose -f compose.production.yml logs --tail=200 backend frontend
```

Repeat the health and application smoke tests. A single-host Compose update may
have a short interruption; use a platform rolling deployment with multiple
backend replicas when zero-downtime releases are required.

## 12. Roll back

If the new application images fail but the migration remains backward
compatible:

```bash
git checkout YOUR_PREVIOUS_COMMIT_SHA
docker compose -f compose.production.yml build
docker compose -f compose.production.yml up -d --remove-orphans
```

Do not automatically reverse migrations. A database rollback requires a
migration-specific recovery decision or a tested backup restoration. Confirm
the three health endpoints and repeat the public smoke test after rollback.

## Container-platform mapping

For Render, Railway, Fly.io, ECS, Kubernetes, or another container platform:

- Build the backend from `backend/Dockerfile`; expose internal port 8000.
- Build the frontend from `frontend/Dockerfile`; expose public port 80.
- Set frontend `BACKEND_HOST` to the backend's private DNS name and
  `BACKEND_PORT=8000`.
- Attach managed PostgreSQL and Redis URLs only to the backend.
- Run the migration command as one release/pre-deploy job.
- Keep `DJANGO_MIGRATE_ON_STARTUP=False` on web replicas.
- Use `/api/health/live/` for liveness and `/api/health/ready/` for readiness.
- Point the custom domain at the frontend service.
- Set Django's trusted-proxy ranges to the platform's actual direct proxy
  addresses and keep all secure-cookie settings enabled.
- Deploy immutable images tagged with the Git commit SHA.
