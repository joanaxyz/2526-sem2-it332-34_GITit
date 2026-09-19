# Deploy GIT it! on Render for $0

The root [`render.yaml`](../render.yaml) is a disposable all-Free Render
Blueprint. It runs the Django API only: Gunicorn in one Free Docker web
service, one Free Render Key Value instance, and the existing Supabase
Postgres database supplied through a secret environment variable.

The Vite frontend is **not** built or served here. It is hosted on Vercel,
which rewrites `/api` to this service; see the
[Vercel deployment guide](VERCEL.md). Deploy this service first, because
Vercel's rewrite needs its URL.

No Render Postgres database or paid Render instance is declared.

## What the Blueprint creates

| Resource | Render type | Plan | Public? |
| --- | --- | --- | --- |
| `git-it-app` | API-only Docker web service | Free | Yes |
| `git-it-cache` | Key Value | Free | No external access |
| Existing Supabase database | External Postgres | Your Supabase plan | No new Render resource |

Single-origin auth is still intentional, but the single origin is now
Vercel's. Vercel serves the SPA and rewrites `/api` to this service, so the
browser never makes a cross-origin call and secure `SameSite=Strict` refresh
cookies keep working without cross-origin auth exceptions.

This service stays public because Vercel's rewrite has to reach it. Django
admin and the DRF schema are reached on this Render URL directly, and
WhiteNoise serves their static files.

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
6. Two more prompts may appear. Both are safe to leave blank until Vercel
   exists, then set both to the Vercel origin with its scheme, for example
   `https://your-project.vercel.app`:
   - `DJANGO_CORS_ALLOWED_ORIGINS`
   - `DJANGO_CSRF_TRUSTED_ORIGINS`

   `DJANGO_ALLOWED_HOSTS` and `FRONTEND_BASE_URL` are **not** prompted. They
   are declared in `render.yaml`, so edit them there and push rather than in
   the dashboard: a Blueprint value overwrites the dashboard on sync, so a
   dashboard edit would be silently reverted.
7. Apply the Blueprint and watch the `git-it-app` Events logs.

If the resource review shows Starter, Basic, Standard, a Render database, or
another paid resource, stop. If Render displays **Payment Information
Required** because of a paid Blueprint resource, cancel and confirm it is
reading the latest `render.yaml` commit.

## 5. First startup

Free web services do not support pre-deploy commands, one-off jobs, Dashboard
shell access, or SSH. The container therefore performs these safe steps
before accepting traffic:

1. Validate Django's production environment.
2. Apply pending migrations to Supabase.
3. Seed official curriculum and command-library data, **only when
   `DJANGO_SEED_ON_STARTUP=True`**. The Blueprint ships it as `False`.
4. Create or update the bootstrap administrator from the prompted secrets.
5. Collect Django static files.
6. Start Gunicorn on Render's public port.

Every one of those steps runs before Gunicorn binds the port, which is why
seeding is off by default: a multi-minute seed makes Render fail the deploy
for not binding in time.

**To seed on a first deploy**, set `DJANGO_SEED_ON_STARTUP=True` on the
`git-it-app` Environment page, redeploy, wait for the service to go live,
then set it back to `False`. Seed commands do not use `--reset`, and
`ALLOW_DESTRUCTIVE_SEED_RESET=False` prevents accidental production
deletion.

After the first successful administrator login, remove all three
`DJANGO_SUPERUSER_*` variables from the `git-it-app` Environment page and
redeploy. The database user remains an administrator, but the plaintext
bootstrap password no longer remains in the service environment.

## 6. Verify the deployment

Copy the public `git-it-app` URL and run:

```bash
export APP_URL=https://git-it-app-czpy.onrender.com
curl --fail --show-error "$APP_URL/api/health/live/"
curl --fail --show-error "$APP_URL/api/health/ready/"
```

Replace the example hostname with the URL assigned by Render. The first
request after an idle period can take about a minute while the Free service
wakes.

This service no longer serves the SPA or its media, so there is no
`/nginx-health`, and `/cosmetics`, `/audio` and `/assets` return 404 here by
design. Those belong to Vercel now. Exercise the application itself through
the Vercel URL, following the verification steps in the
[Vercel deployment guide](VERCEL.md).

Runtime media is committed and ships in the Vercel build. User-uploaded files
would still require external object storage.

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
- **`DisallowedHost` / Invalid HTTP Host**: `DJANGO_ALLOWED_HOSTS` is a
  prompted value now. It must list the Render hostname **and** the Vercel
  hostname, comma separated and without schemes, because trusted proxy
  headers enable `USE_X_FORWARDED_HOST` and Vercel forwards its own domain in
  `X-Forwarded-Host`.
- **Readiness returns 503**: inspect the app logs for Supabase or Key Value
  connectivity errors.
- **Startup fails at bootstrap admin**: provide all three
  `DJANGO_SUPERUSER_*` values and use a password accepted by Django's password
  validators.
- **Deploy times out without binding a port**: a startup seed is running. Set
  `DJANGO_SEED_ON_STARTUP=False` and redeploy.
- **Media returns HTML or 404**: media is served by Vercel, not Render. Check
  the Vercel deployment first, then run
  `python scripts/check_runtime_assets.py --require-tracked` on the deployed
  commit.
- **Blueprint does not redeploy**: confirm GitHub CI passed and sync the latest
  Blueprint commit manually.
