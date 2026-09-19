# Backend-only Render image. The Vite SPA is hosted on Vercel, which rewrites
# /api to this service, so there is no Node build stage and no Nginx here:
# Gunicorn binds Render's public port directly and WhiteNoise serves the small
# Django admin / DRF schema static bundle.
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=10000

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates git tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY deploy/render-api/start.sh /app/start-render-api.sh

RUN sed -i 's/\r$//' /app/start-render-api.sh \
    && chmod +x /app/start-render-api.sh \
    && sh -n /app/start-render-api.sh \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir -p /app/backend/staticfiles \
    && chown -R app:app /app

USER app
EXPOSE 10000

# Gunicorn is reached directly now, so the probe has to present a Host header
# that satisfies ALLOWED_HOSTS. Nginx used to absorb this with its own
# unauthenticated /nginx-health location.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import os, urllib.request; port = os.environ.get('PORT', '10000'); host = (os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')[0].strip() or 'localhost'); request = urllib.request.Request(f'http://127.0.0.1:{port}/api/health/live/', headers={'Host': host}); urllib.request.urlopen(request, timeout=3)" || exit 1

ENTRYPOINT ["/usr/bin/tini", "-g", "--", "/app/start-render-api.sh"]
