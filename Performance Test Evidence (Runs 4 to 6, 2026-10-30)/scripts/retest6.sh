#!/bin/sh
# Run 6: NFR-PERF-04 (SRS 1.4) workload - 40 learners joining one every 15 s, then a 10-minute hold,
# bracketed by pg_stat_statements snapshots of the production database.
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
snap r6_pgstat_1.json
echo "run start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
python loadtest.py --base $BASE --users prod_users.csv --tier-id 1 --duration 600 --ramp 600 --think 10 \
  --home-every 60 --timeout 30 --out results/r6_step > results/r6_step_console.txt 2>&1
echo "run end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
tail -2 results/r6_step_console.txt
snap r6_pgstat_2.json
echo done
