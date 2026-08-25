FROM node:22-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=10000

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates git nginx tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist /app/frontend-dist
COPY deploy/render-free/nginx.conf /etc/nginx/nginx.conf
COPY deploy/render-free/start.sh /app/start-render-free.sh

RUN sed -i 's/\r$//' /app/start-render-free.sh \
    && chmod +x /app/start-render-free.sh \
    && sh -n /app/start-render-free.sh \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir -p \
        /app/backend/staticfiles \
        /tmp/nginx-client \
        /tmp/nginx-proxy \
        /tmp/nginx-fastcgi \
        /tmp/nginx-uwsgi \
        /tmp/nginx-scgi \
    && chown -R app:app \
        /app \
        /tmp/nginx-client \
        /tmp/nginx-proxy \
        /tmp/nginx-fastcgi \
        /tmp/nginx-uwsgi \
        /tmp/nginx-scgi

USER app
EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:10000/nginx-health', timeout=3)" || exit 1

ENTRYPOINT ["/usr/bin/tini", "-g", "--", "/app/start-render-free.sh"]
