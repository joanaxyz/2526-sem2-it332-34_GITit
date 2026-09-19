#!/bin/sh
set -eu

# Render pre-deploy commands and one-off jobs arrive as container arguments.
# Honour them without starting the long-lived web process.
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

# Defaults to off. Seeding runs for several minutes and everything here happens
# before Gunicorn binds the port, so an accidental seed would make Render fail
# the deploy for not binding in time. Enable it deliberately for a first
# deploy, then turn it back off.
if boolean_enabled "${DJANGO_SEED_ON_STARTUP:-false}" DJANGO_SEED_ON_STARTUP; then
  python manage.py seed_all
fi

python manage.py bootstrap_superuser
python manage.py collectstatic --noinput

# Gunicorn is the public listener now, so it binds 0.0.0.0 rather than the
# loopback address Nginx used to proxy to, and it replaces this shell so it
# receives Render's SIGTERM directly.
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers "${GUNICORN_WORKERS:-1}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile -
