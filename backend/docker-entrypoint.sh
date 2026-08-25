#!/bin/sh
set -eu

python manage.py check_runtime_config

case "${DJANGO_MIGRATE_ON_STARTUP:-true}" in
  true|True|TRUE|1|yes|Yes|YES|on|On|ON)
    python manage.py migrate --noinput
    ;;
  false|False|FALSE|0|no|No|NO|off|Off|OFF)
    ;;
  *)
    echo "DJANGO_MIGRATE_ON_STARTUP must be a boolean value." >&2
    exit 1
    ;;
esac

python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile -
