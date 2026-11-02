"""Per-minute view of the stepped test: learner i joins at i*ramp/n seconds.
Usage: python analyze_step.py results/prod_step 40 600 [bucket]"""
import csv, json, sys
sys.path.insert(0, ".")
from loadtest import pct
base, n, ramp = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
bucket = float(sys.argv[4]) if len(sys.argv) > 4 else 60
rows = [(float(r[0]), r[1], int(r[2]), float(r[3]), r[4]) for r in list(csv.reader(open(base + "_requests.csv")))[1:]]
t0 = json.load(open(base + "_summary.json"))
from calendar import timegm; import time
t0 = timegm(time.strptime(t0["started_utc"], "%Y-%m-%dT%H:%M:%SZ"))
out = []
end = max(r[0] for r in rows)
b = 0.0
while t0 + b <= end:
    rs = [r for r in rows if t0 + b <= r[0] < t0 + b + bucket]
    sub = [r[3] for r in rs if r[1] == "submit_command" and r[2] == 200]
    err = [r for r in rs if r[4] or not (200 <= r[2] < 300) and r[2] != 423]
    span = min(bucket, end - (t0 + b))
    joined = min(n, -(-(b + span) // (ramp / n)))
    joined = int(joined)
    out.append({"minute": int(b // 60) + 1, "learners_joined": joined, "requests": len(rs),
                "seconds": round(span), "rps": round(len(rs) / span, 2), "submits_ok": len(sub),
                "submit_p50_ms": round(pct(sub, 50)) if sub else None,
                "submit_p95_ms": round(pct(sub, 95)) if sub else None,
                "errors": len(err), "error_kinds": sorted({(r[1], r[4] or r[2]) for r in err}, key=str)[:6]})
    print(out[-1])
    b += bucket
json.dump(out, open(base + "_per_minute.json", "w"), indent=1)
