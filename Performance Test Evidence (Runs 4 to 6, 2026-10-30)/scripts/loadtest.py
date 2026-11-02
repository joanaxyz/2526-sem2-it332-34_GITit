"""GIT it! learner workload test (NFR-PERF-01, 03, 04, 06, 07).

Each virtual learner signs in, starts (or resumes) a tier run, then until the end of the test
submits `git status` about every --think seconds and loads Home data (profile + dashboard)
about every --home-every seconds. `git status` is a free diagnostic, so it never changes the
repository or spends the command budget, but it travels the full submit path: JSON schema
validation, transition verification, step logging and the run payload.

Usage:
  python loadtest.py --base https://git-it-34.vercel.app --users users.csv --tier-id 12 \
      --duration 600 --ramp 60 --out results/prod
users.csv: one "username,password" per line.
"""
import argparse
import csv
import http.client
import json
import random
import ssl
import statistics
import threading
import time
from urllib.parse import urlsplit

LOCK = threading.Lock()
RECORDS = []  # (t_start, name, status, latency_ms, error)
ABORT = threading.Event()
ABORT_ERRORS_PER_MIN = 30


class Client:
    def __init__(self, base, timeout):
        self.u = urlsplit(base)
        self.timeout = timeout
        self.conn = None
        self.token = None
        self.refresh_cookie = None  # HttpOnly refresh cookie, sent to /api/auth/ like the browser does

    def _connect(self):
        port = self.u.port or (443 if self.u.scheme == "https" else 80)
        if self.u.scheme == "https":
            self.conn = http.client.HTTPSConnection(self.u.hostname, port, timeout=self.timeout,
                                                    context=ssl.create_default_context())
        else:
            self.conn = http.client.HTTPConnection(self.u.hostname, port, timeout=self.timeout)

    def call(self, name, method, path, body=None, allow_refresh=True):
        headers = {"X-Git-It-Client": "web", "Accept": "application/json", "User-Agent": "git-it-loadtest/1.0"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.refresh_cookie and path.startswith("/api/auth/"):
            headers["Cookie"] = self.refresh_cookie
        data = json.dumps(body).encode() if body is not None else None
        prefix = self.u.path.rstrip("/")
        started_wall = time.time()
        t0 = time.perf_counter()
        status, payload, error = 0, None, ""
        for attempt in (1, 2):
            try:
                if self.conn is None:
                    self._connect()
                self.conn.request(method, prefix + path, body=data, headers=headers)
                resp = self.conn.getresponse()
                raw = resp.read()
                status = resp.status
                for cookie in resp.msg.get_all("Set-Cookie") or []:
                    if cookie.startswith("git_it_refresh="):
                        self.refresh_cookie = cookie.split(";", 1)[0]
                try:
                    payload = json.loads(raw) if raw else None
                except ValueError:
                    payload = None
                break
            except (http.client.RemoteDisconnected, ConnectionResetError, BrokenPipeError) as exc:
                self.conn = None  # stale keep-alive socket: reconnect once
                if attempt == 2:
                    error = type(exc).__name__
            except Exception as exc:  # timeouts and the like count as errors
                self.conn = None
                error = type(exc).__name__
                break
        latency = (time.perf_counter() - t0) * 1000
        with LOCK:
            RECORDS.append((started_wall, name, status, latency, error))
            recent = [r for r in RECORDS[-400:] if r[0] > started_wall - 60 and (r[4] or r[2] >= 429)]
            if len(recent) > ABORT_ERRORS_PER_MIN and not ABORT.is_set():
                ABORT.set()
                print(f"ABORT at {time.strftime('%H:%M:%S', time.gmtime())}: {len(recent)} errors in 60 s", flush=True)
        if status == 401 and allow_refresh and self.refresh_cookie:
            # The 15-minute access token expired: refresh once and retry, as the app's httpClient does.
            s2, fresh = self.call("refresh", "POST", "/api/auth/refresh/", allow_refresh=False)
            if s2 == 200 and fresh:
                self.token = fresh["access"]
                return self.call(name, method, path, body, allow_refresh=False)
        return status, payload


def git_status_payload(state, revision):
    return {
        "command": "git status",
        "execution": {
            "client_run_revision": revision,
            "processed": True,
            "next_state": state,
            "output": "",
            "normalized_command": "git status",
            "exit_code": 0,
            "diagnostic": True,
            "stdout": "",
            "stderr": "",
            "command_family": "status",
            "diagnostic_metadata": [],
        },
    }


def learner(args, username, password, start_delay, stop_at, results):
    if ABORT.wait(start_delay):
        return
    c = Client(args.base, args.timeout)
    status, body = c.call("login", "POST", "/api/auth/login/", {"identifier": username, "password": password})
    if status != 200 or not body:
        results["login_failures"] += 1
        return
    c.token = body["access"]
    status, run = c.call("start_tier", "POST", f"/api/adventure-level-tiers/{args.tier_id}/runs/", {})
    if status == 423:
        # A new player must own a companion first, exactly as in the app's onboarding.
        c.call("setup_purchase", "POST", "/api/shop/catalog/purchase/", {"kind": "companion", "slug": "blue"})
        status, run = c.call("start_tier", "POST", f"/api/adventure-level-tiers/{args.tier_id}/runs/", {})
    if status not in (200, 201) or not run:
        results["start_failures"] += 1
        return
    run_id = run["id"]
    state = run["repository_state"]
    revision = (run.get("counts") or {}).get("total_attempts", 0)
    next_home = time.time() + random.uniform(0, args.home_every)
    while time.time() < stop_at and not ABORT.is_set():
        if time.time() >= next_home:
            c.call("home_me", "GET", "/api/auth/me/")
            c.call("home_dashboard", "GET", "/api/progress/dashboard/")
            next_home = time.time() + args.home_every
        status, body = c.call("submit_command", "POST", f"/api/adventure-tier-runs/{run_id}/submit-command/",
                              git_status_payload(state, revision))
        if status == 200 and body:
            state = body["run"]["repository_state"]
            revision = (body["run"].get("counts") or {}).get("total_attempts", revision)
        elif status == 400:
            # Resynchronise like the app does after a rejected submit.
            s2, fresh = c.call("refresh_run", "GET", f"/api/adventure-tier-runs/{run_id}/")
            if s2 == 200 and fresh:
                state, revision = fresh["repository_state"], (fresh.get("counts") or {}).get("total_attempts", revision)
        time.sleep(max(0.0, random.gauss(args.think, args.think * 0.2)))


def pct(values, p):
    if not values:
        return None
    values = sorted(values)
    k = (len(values) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


def summarize(records, window_start, window_end):
    """Summary over the steady-state window (after ramp-up)."""
    rows = [r for r in records if window_start <= r[0] <= window_end]
    out = {"window_seconds": round(window_end - window_start, 1), "requests": len(rows)}
    # Any request that did not succeed (timeouts, connection errors, 4xx and 5xx) is an error.
    errors = [r for r in rows if r[4] or not (200 <= r[2] < 300)]
    out["server_error_rate_pct"] = (round(100 * sum(1 for r in rows if r[4] or r[2] >= 500 or r[2] == 0) / len(rows), 3)
                                    if rows else None)
    out["error_rate_pct"] = round(100 * len(errors) / len(rows), 3) if rows else None
    out["throughput_rps"] = round(len(rows) / (window_end - window_start), 2) if rows else 0
    per = {}
    for name in sorted({r[1] for r in rows}):
        lat = [r[3] for r in rows if r[1] == name]
        st = {}
        for r in rows:
            if r[1] == name:
                key = r[4] or str(r[2])
                st[key] = st.get(key, 0) + 1
        per[name] = {
            "count": len(lat), "statuses": st,
            "p50_ms": round(pct(lat, 50), 1), "p90_ms": round(pct(lat, 90), 1),
            "p95_ms": round(pct(lat, 95), 1), "p99_ms": round(pct(lat, 99), 1),
            "mean_ms": round(statistics.mean(lat), 1), "max_ms": round(max(lat), 1),
        }
    out["endpoints"] = per
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--users", required=True)
    ap.add_argument("--tier-id", type=int, required=True)
    ap.add_argument("--duration", type=float, default=600, help="seconds of steady load after ramp-up")
    ap.add_argument("--ramp", type=float, default=60)
    ap.add_argument("--think", type=float, default=10)
    ap.add_argument("--home-every", type=float, default=60)
    ap.add_argument("--timeout", type=float, default=30)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    users = [tuple(r[:2]) for r in csv.reader(open(args.users, encoding="utf-8")) if r]
    t0 = time.time()
    ramp_end = t0 + args.ramp
    stop_at = ramp_end + args.duration
    results = {"login_failures": 0, "start_failures": 0}
    threads = []
    for i, (u, p) in enumerate(users):
        delay = args.ramp * i / max(1, len(users))
        th = threading.Thread(target=learner, args=(args, u, p, delay, stop_at, results), daemon=True)
        th.start()
        threads.append(th)
    for th in threads:
        th.join(timeout=args.ramp + args.duration + 120)

    with open(f"{args.out}_requests.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["epoch_start", "request", "status", "latency_ms", "error"])
        for r in sorted(RECORDS):
            w.writerow([f"{r[0]:.3f}", r[1], r[2], f"{r[3]:.1f}", r[4]])
    summary = {
        "base": args.base, "virtual_learners": len(users), "tier_id": args.tier_id,
        "think_seconds": args.think, "home_every_seconds": args.home_every,
        "ramp_seconds": args.ramp, "steady_seconds": args.duration,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        **results,
        "steady_state": summarize(RECORDS, ramp_end, stop_at),
        "whole_run": summarize(RECORDS, t0, stop_at + 60),
    }
    with open(f"{args.out}_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary["steady_state"], indent=2))
    print("login_failures", results["login_failures"], "start_failures", results["start_failures"])


if __name__ == "__main__":
    main()
