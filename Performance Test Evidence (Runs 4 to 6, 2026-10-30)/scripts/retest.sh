#!/bin/sh
# Retest after the Singapore database move and 8 Gunicorn threads: Run A then Run B,
# each bracketed by pg_stat_statements snapshots of the production database.
set -u
PERF="C:/Users/Joana/AppData/Local/Temp/claude/c--Users-Joana-Documents-GIT-IT/0045e2f7-55d9-4fb7-9ec1-a060bdd170f1/scratchpad/perf"
BACKEND="C:/Users/Joana/Documents/GIT-IT/backend"
BASE=https://git-it-34.vercel.app

snap() {
  (cd "$BACKEND" && set -a && . ./newdb.env && set +a \
    && DJANGO_DEBUG=True REDIS_URL="" EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend \
       PERF_SNAP="$PERF/results/$1" .venv/Scripts/python.exe manage.py shell -c "exec(open('$PERF/pgstat.py').read())" 2>&1 \
    | grep -v 'objects imported')
  echo "$1 $(date -u +%H:%M:%S)"
}

cd "$PERF"
snap r5_pgstat_a1.json
echo "runA start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
python loadtest.py --base $BASE --users prod_users.csv --tier-id 1 --duration 600 --ramp 60 --think 10 \
  --home-every 60 --timeout 30 --out results/r5_40 > results/r5_40_console.txt 2>&1
echo "runA end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
tail -2 results/r5_40_console.txt
snap r5_pgstat_a2.json

sleep 90
snap r5_pgstat_b1.json
echo "runB start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
python loadtest.py --base $BASE --users prod_users.csv --tier-id 1 --duration 120 --ramp 600 --think 10 \
  --home-every 60 --timeout 30 --out results/r5_step > results/r5_step_console.txt 2>&1
echo "runB end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
tail -2 results/r5_step_console.txt
snap r5_pgstat_b2.json
echo done
