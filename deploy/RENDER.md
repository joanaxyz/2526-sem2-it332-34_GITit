# Deploy GIT it! on Render for $0

The root [`render.yaml`](../render.yaml) is a disposable all-Free Render
Blueprint. It runs the Vite frontend, Nginx, and Django in one Free Docker web
service, uses one Free Render Key Value instance, and connects to the existing
Supabase Postgres database supplied through a secret environment variable.

No Render Postgres database or paid Render instance is declared.

## What the Blueprint creates

| Resource | Render type | Plan | Public? |
| --- | --- | --- | --- |
| `git-it-app` | Combined Docker web service | Free | Yes |
| `git-it-cache` | Key Value | Free | No external access |
| Existing Supabase database | External Postgres | Your Supabase plan | No new Render resource |

The single-origin container is intentional. Nginx serves the frontend and
proxies `/api` to Gunicorn in the same container, so secure
`SameSite=Strict` refresh cookies continue to work without cross-origin auth
exceptions. It also consumes Free web-service hours for only one service.

## 1. Cancel the old payment dialog

Do not add a card for the previous Blueprint configuration. Select **Cancel**.
That version requested a paid private backend, PostgreSQL, and persistent Key
Value. The current Blueprint contains none of those paid plans.

If Render cached the old Blueprint draft, delete only that unprovisioned draft
or create a new Blueprint instance after the new commit reaches GitHub.

## 2. Prepare the Supabase connection

The existing ignored `backend/.env` already contains a Supabase Shared Pooler
Session-mode URL on port `5432`. This is the appropriate IPv4 connection for a
persistent Render container.

You will paste the complete value of `DATABASE_URL` into Render later. It has
the following general shape, but use the exact value from your environment:

```text
postgresql://postgres.PROJECT_REF:PASSWORD@aws-REGION.pooler.supabase.com:5432/postgres
```

Important:

- Never paste the real URL into Git, a screenshot, chat, or deployment log.
- The Blueprint separately sets `DATABASE_SSLMODE=require`.
- Prepared statements and server-side cursors remain disabled for pooler
  compatibility.
- The startup migration is non-destructive. Destructive seed reset remains
  disabled.

You can obtain a fresh URL from **Supabase Dashboard → Connect → Session
pooler** if needed. Render is IPv4-only for this connection path, so do not use
the default IPv6 direct endpoint unless the project has the appropriate IPv4
support.

## 3. Push the release

From the repository root:

```bash
git status --short
python scripts/check_runtime_assets.py --require-tracked
python scripts/check_render_blueprint.py
python scripts/check_django_deploy.py
git push origin main
```

Deploy only after GitHub Actions passes for the pushed commit. Later Render
deployments use `autoDeployTrigger: checksPass`.

## 4. Create the all-Free Blueprint

1. Open **Render Dashboard → Blueprints → New Blueprint Instance**.
2. Connect the repository and select `main`.
3. Keep the Blueprint path as `render.yaml`.
4. Confirm the resource review shows exactly:
   - `git-it-app`: **Free**
   - `git-it-cache`: **Free**
   - no Render PostgreSQL database
5. Enter the prompted secrets:
   - `DATABASE_URL`: the existing Supabase Session pooler URL
   - `DJANGO_SUPERUSER_USERNAME`: your first admin username
   - `DJANGO_SUPERUSER_EMAIL`: your admin email
   - `DJANGO_SUPERUSER_PASSWORD`: a unique strong password
6. Apply the Blueprint and watch the `git-it-app` Events logs.

If the resource review shows Starter, Basic, Standard, a Render database, or
another paid resource, stop. If Render displays **Payment Information
Required** because of a paid Blueprint resource, cancel and confirm it is
reading the latest `render.yaml` commit.

## 5. First startup

Free web services do not support pre-deploy commands, one-off jobs, Dashboard
shell access, or SSH. The combined container therefore performs these safe
steps before accepting traffic:

1. Validate Django's production environment.
2. Apply pending migrations to Supabase.
3. Idempotently upsert official curriculum and command-library data.
4. Create or update the bootstrap administrator from the prompted secrets.
5. Collect Django static files.
6. Start Gunicorn and Nginx.

The first startup can take longer than later cold starts. Seed commands do not
use `--reset`, and `ALLOW_DESTRUCTIVE_SEED_RESET=False` prevents accidental
production deletion.

After the first successful administrator login, remove all three
`DJANGO_SUPERUSER_*` variables from the `git-it-app` Environment page and
redeploy. The database user remains an administrator, but the plaintext
bootstrap password no longer remains in the service environment.

## 6. Verify the deployment

Copy the public `git-it-app` URL and run:

```bash
export APP_URL=https://git-it-app.onrender.com
curl --fail --show-error "$APP_URL/nginx-health"
curl --fail --show-error "$APP_URL/api/health/live/"
curl --fail --show-error "$APP_URL/api/health/ready/"
curl --fail --show-error \
  "$APP_URL/cosmetics/story-worlds/arcane-spire/monsters/monster-01/portrait.png" \
  --output /dev/null
```

Replace the example hostname with the URL assigned by Render. The first
request after an idle period can take about a minute while the Free service
wakes.

In a browser, verify registration, sign-in, authenticated refresh, profile
avatar, story map, one adventure, one challenge, shop, sign-out, sign-in, and
administrator access. Check the Network panel for `/api`, `/cosmetics`,
`/audio`, or `/assets` 404/5xx responses.

All current runtime media is committed and copied into the combined frontend
build. User-uploaded files would still require external object storage.

## 7. Email behavior

The Blueprint uses Django's dummy email backend. Registration and gameplay
work, but password-reset emails are discarded. No SMTP or email-provider
account is needed for this preview.

## Free-tier limitations

- The app sleeps after 15 minutes without inbound traffic and can take about a
  minute to wake.
- Free web services cannot scale beyond one instance and have no shell access.
- Free Key Value is non-persistent, so throttle counters can reset. Refresh
  session revocation still has a Supabase database source of truth.
- Free usage is subject to Render's monthly instance-hour, build-minute, and
  bandwidth allowances.
- Supabase availability, storage, and limits are governed separately by the
  existing Supabase project's plan.
- This topology is for a disposable preview, not a reliable 100-concurrent-user
  event.

If no payment method is added, Render suspends Free resources instead of
billing when applicable Free allowances are exhausted. Always review the
Billing page before adding a card.

## Troubleshooting

- **Payment dialog still appears**: make sure Render is reading the latest
  commit and lists only `git-it-app` Free plus `git-it-cache` Free.
- **Database connection fails**: use the Supabase Session pooler URL on port
  `5432`, verify its password, and keep `DATABASE_SSLMODE=require`.
- **Invalid HTTP Host or redirect loop**: confirm the app's self-referenced
  `RENDER_EXTERNAL_HOSTNAME` and proxy settings were created by the Blueprint.
- **Readiness returns 503**: inspect the app logs for Supabase or Key Value
  connectivity errors.
- **Startup fails at bootstrap admin**: provide all three
  `DJANGO_SUPERUSER_*` values and use a password accepted by Django's password
  validators.
- **Media returns HTML or 404**: run
  `python scripts/check_runtime_assets.py --require-tracked` on the deployed
  commit and confirm the combined Docker build completed.
- **Blueprint does not redeploy**: confirm GitHub CI passed and sync the latest
  Blueprint commit manually.
