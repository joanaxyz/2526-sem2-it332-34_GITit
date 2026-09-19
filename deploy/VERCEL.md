# Deploy the GIT it! frontend on Vercel

Vercel hosts the Vite SPA. The Django API stays on Render, and Vercel proxies
`/api` to it, so the browser still sees a single origin.

```text
browser ──► Vercel ──┬── React/Vite app
                     ├── images, audio, video
                     ├── JS/CSS
                     └── /api/*
                            └──► Render: git-it-app, backend only
                                         Django/Gunicorn
                                         ├──► Supabase Postgres
                                         └──► Redis (Render Key Value)
```

Render builds and serves the Django API only. It contains no Node build stage
and no Nginx, and it does not serve the SPA or any media.

## Why the proxy instead of calling Render directly

The refresh cookie is `SameSite=Strict`, `Secure`, host-only, scoped to
`/api/auth/`. That works today only because Render's Nginx serves the app and
the API from one origin. Pointing the SPA straight at `*.onrender.com` would
make every auth call cross-site and force `JWT_COOKIE_SAMESITE=None`, which
browsers that block third-party cookies then drop — silent logout loops.

Keeping `/api` on the Vercel origin preserves the existing model exactly:

- `VITE_API_BASE_URL` stays `/api`.
- `JWT_COOKIE_SAMESITE` stays `Strict`.
- No CORS entries, and no CSRF trusted origins, for the Vercel domain.
- Preview deployments work with no extra backend configuration, because each
  preview is same-origin with its own proxy.

## What is checked in

| File | Purpose |
| --- | --- |
| [`frontend/vercel.json`](../frontend/vercel.json) | Rewrites, security headers, cache policy |
| [`frontend/.env.production`](../frontend/.env.production) | Pins `VITE_API_BASE_URL=/api` |
| [`frontend/.vercelignore`](../frontend/.vercelignore) | Keeps local-only files out of the upload |

On the Render side:

| File | Purpose |
| --- | --- |
| [`render.yaml`](../render.yaml) | Blueprint, now backend-only |
| [`deploy/render-api/`](render-api/) | API-only image: Gunicorn, no Node, no Nginx |

`deploy/render-free/` is the superseded combined image. Nothing references it
any more and it can be deleted.

`scripts/check_render_blueprint.py` enforces the split: it fails if the
Blueprint rebuilds on `frontend/**` changes, or if the Render Dockerfile
mentions `FROM node`, `npm ci`, or `nginx`.

## 1. Confirm the backend URL

`frontend/vercel.json` ships with `https://git-it-app.onrender.com`. Confirm
the real URL in the Render dashboard, and edit it if it differs:

```bash
curl -i https://git-it-app.onrender.com/api/health/live/
```

A free Render instance that has spun down takes roughly 50 seconds to answer
the first request. That is within Vercel's 120-second proxy timeout, so a cold
start is slow but not an error.

Update **both** occurrences if the host changes — the rewrite destination is
the only place the backend URL appears.

## 2. Create the Vercel project

Import the GitHub repository at <https://vercel.com/new>, then set:

| Setting | Value |
| --- | --- |
| Root Directory | `frontend` |
| Framework Preset | Vite |
| Node.js Version | 22.x |

**Root Directory is the one that matters.** This is a monorepo; pointing
Vercel at the repository root makes the build fail to find `package.json`.

Build command, install command, and output directory come from `vercel.json`.
No environment variables need to be set in the dashboard.

Use the Git integration rather than `vercel --prod` from your laptop. The CLI
caps Hobby source uploads at 100 MB, and `frontend/public` alone is about
87 MB of tracked sprites and audio before the rest of the tree. A Git
deployment builds from the repository and is not subject to that limit.

## 3. Verify the deployment

Substitute your deployment URL. All four checks should pass before you send
anyone the link.

```bash
APP=https://your-project.vercel.app

# 1. The API reaches Django through the proxy, and Django's trailing slash
#    survives the rewrite. Prints the status and any redirect target.
#      "200" with an empty redirect -> correct.
#      "301 https://...onrender.com/..." -> the rewrite dropped the trailing
#        slash, so APPEND_SLASH is bouncing to the backend host. That leaks
#        the origin and breaks POSTs. Fix below.
#      "400" -> DJANGO_ALLOWED_HOSTS on Render is missing the Vercel
#        hostname. See section 4.
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' "$APP/api/health/live/"

# 2. Authenticated API responses are never cached on the shared CDN.
curl -sI "$APP/api/health/live/" | grep -i '^x-vercel-cache'           # MISS or BYPASS

# 3. SPA deep links resolve to the app, not a 404.
curl -s -o /dev/null -w '%{http_code}\n' "$APP/home"                   # 200

# 4. A missing asset is a real 404, not index.html with a 200.
curl -s -o /dev/null -w '%{http_code}\n' "$APP/cosmetics/nope.png"     # 404
```

The same checks in Windows PowerShell. Use `curl.exe`, because bare `curl` is
an alias for `Invoke-WebRequest`, and `NUL` rather than `/dev/null`:

```powershell
$APP = "https://your-project.vercel.app"

curl.exe -s -o NUL -w '1 api      %{http_code} %{redirect_url}\n' "$APP/api/health/live/"
curl.exe -sI "$APP/api/health/live/" | Select-String '^x-vercel-cache'
curl.exe -s -o NUL -w '3 deeplink %{http_code}\n' "$APP/home"
curl.exe -s -o NUL -w '4 missing  %{http_code}\n' "$APP/cosmetics/nope.png"
```

Then log in through the browser and confirm in DevTools -> Application ->
Cookies that `git_it_refresh` is set on the **Vercel** domain with
`SameSite=Strict`, `Secure`, `HttpOnly`, and path `/api/auth/`.

If check 1 returns 301, change the rewrite in `frontend/vercel.json` to an
anchored regular expression, which cannot drop the slash:

```json
{ "source": "^/api/(.*)$", "destination": "https://git-it-app.onrender.com/api/$1" }
```

## 4. Required Render environment values

Four `git-it-app` values are Render dashboard prompts because they depend on
the Vercel origin, which the Blueprint cannot know. Set them once the Vercel
URL exists.

**`DJANGO_ALLOWED_HOSTS` is the one that will break everything if you skip
it.** It must list both hostnames, comma separated, without schemes:

```
git-it-app.onrender.com,your-project.vercel.app
```

`DJANGO_TRUST_PROXY_HEADERS=True` enables Django's `USE_X_FORWARDED_HOST`, and
Vercel forwards its own domain in `X-Forwarded-Host`. If the Vercel hostname
is missing, Django rejects every proxied request with `DisallowedHost` and the
whole app returns 400.

The other three take the full Vercel origin, scheme included, for example
`https://your-project.vercel.app`:

- `DJANGO_CORS_ALLOWED_ORIGINS` and `DJANGO_CSRF_TRUSTED_ORIGINS` are defence
  in depth. The browser never calls Render cross-origin while the rewrite is
  in place, and DRF views are `csrf_exempt` because authentication is JWT
  only, so neither is load-bearing today.
- `FRONTEND_BASE_URL` builds password-reset links. The preview runs
  `EMAIL_BACKEND=dummy`, so nothing is sent until you enable real email.

## Differences from the Render Nginx setup

- **Caching for external rewrites is explicitly disabled.** Since April 2026
  Vercel caches proxied responses by default when the upstream sends
  `cache-control`. This API is authenticated and per-user, so
  `frontend/vercel.json` sets `x-vercel-enable-rewrite-caching: 0` on
  `/api/*`. Do not remove that header.
- **HTML cache headers are Vercel's defaults** (`public, max-age=0,
  must-revalidate`) rather than Nginx's explicit `no-cache`. Equivalent in
  effect.
- **`/static/` is not proxied.** Only Django admin and the DRF schema UI use
  it, and both are reached on the Render URL directly. The SPA never requests
  `/static/`.
- **One extra network hop per API call.** Vercel's edge forwards to Render.

## Rollback

Render no longer serves the SPA, so there is no working URL to fall back to.
Rolling back means restoring the combined image: point `dockerfilePath` at
`./deploy/render-free/Dockerfile`, put `frontend/**` back in `buildFilter`,
return the four prompted variables to their `fromService RENDER_EXTERNAL_URL`
form, and revert the matching assertions in
`scripts/check_render_blueprint.py` and the `container-images` job in
`.github/workflows/ci.yml`.

Rolling back only the Vercel side is easier: revert the frontend commit and
redeploy. The Render API is unaffected by Vercel deployments.
