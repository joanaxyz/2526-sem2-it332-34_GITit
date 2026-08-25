FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh \
    && chmod +x /app/docker-entrypoint.sh \
    && sh -n /app/docker-entrypoint.sh \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir -p /app/staticfiles \
    && chown -R app:app /app

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os, urllib.request; port = os.environ.get('PORT', '8000'); host = (os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')[0].strip() or 'localhost'); request = urllib.request.Request(f'http://127.0.0.1:{port}/api/health/live/', headers={'Host': host}); urllib.request.urlopen(request, timeout=3)" || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
