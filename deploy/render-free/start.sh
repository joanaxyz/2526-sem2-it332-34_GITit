#!/bin/sh
set -eu

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

boolean_enabled() {
  case "$1" in
    true|True|TRUE|1|yes|Yes|YES|on|On|ON)
      return 0
      ;;
    false|False|FALSE|0|no|No|NO|off|Off|OFF)
      return 1
      ;;
    *)
      echo "$2 must be a boolean value." >&2
      exit 1
      ;;
  esac
}

cd /app/backend
python manage.py check_runtime_config

if boolean_enabled "${DJANGO_MIGRATE_ON_STARTUP:-true}" DJANGO_MIGRATE_ON_STARTUP; then
  python manage.py migrate --noinput
fi

if boolean_enabled "${DJANGO_SEED_ON_STARTUP:-true}" DJANGO_SEED_ON_STARTUP; then
  python manage.py seed_all
fi

python manage.py bootstrap_superuser
python manage.py collectstatic --noinput

gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers "${GUNICORN_WORKERS:-1}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile - &
gunicorn_pid=$!

nginx -g 'daemon off;' &
nginx_pid=$!

shutdown() {
  trap - TERM INT
  kill -TERM "$nginx_pid" "$gunicorn_pid" 2>/dev/null || true
  wait "$nginx_pid" 2>/dev/null || true
  wait "$gunicorn_pid" 2>/dev/null || true
  exit 0
}

trap shutdown TERM INT

while kill -0 "$gunicorn_pid" 2>/dev/null && kill -0 "$nginx_pid" 2>/dev/null; do
  sleep 1
done

status=0
if ! kill -0 "$gunicorn_pid" 2>/dev/null; then
  wait "$gunicorn_pid" || status=$?
  kill -TERM "$nginx_pid" 2>/dev/null || true
  wait "$nginx_pid" 2>/dev/null || true
else
  wait "$nginx_pid" || status=$?
  kill -TERM "$gunicorn_pid" 2>/dev/null || true
  wait "$gunicorn_pid" 2>/dev/null || true
fi

exit "$status"
