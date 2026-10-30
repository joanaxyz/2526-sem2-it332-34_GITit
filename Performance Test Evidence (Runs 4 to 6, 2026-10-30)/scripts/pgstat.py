"""Snapshot pg_stat_statements (what Supabase's Query Performance report reads). Run via manage.py shell -c.
PERF_SNAP=<path.json> writes queryid -> (calls, total_exec_time, query) for the current database."""
import json
import os

from django.db import connection

with connection.cursor() as cur:
    cur.execute(
        "select s.queryid::text, s.calls, s.total_exec_time, s.rows, left(s.query, 400) "
        "from pg_stat_statements s join pg_database d on d.oid = s.dbid "
        "where d.datname = current_database()"
    )
    rows = {r[0]: {"calls": r[1], "total_ms": r[2], "rows": r[3], "query": r[4]} for r in cur.fetchall()}
json.dump(rows, open(os.environ["PERF_SNAP"], "w"))
print("statements:", len(rows))
