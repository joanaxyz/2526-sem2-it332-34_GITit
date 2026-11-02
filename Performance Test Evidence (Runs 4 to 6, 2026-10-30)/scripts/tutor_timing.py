"""NFR-PERF-09: AI tutor response time on Home (general questions), sequential, under the rate limit.

Usage: python tutor_timing.py <base> <username> <password> <out.json>
"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE, USER, PASSWORD, OUT = sys.argv[1:5]
QUESTIONS = [
    "What is a branch in Git?",
    "What does git status show?",
    "What is the difference between git fetch and git pull?",
    "Why do merge conflicts happen?",
    "What does the staging area do?",
    "What is a remote in Git?",
]


def call(path, body, token=None, timeout=60):
    headers = {"X-Git-It-Client": "web", "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), headers=headers, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read() or b"null")
            status = resp.status
    except urllib.error.HTTPError as exc:
        status, payload = exc.code, None
    except Exception as exc:  # timeout etc.
        status, payload = 0, {"error": type(exc).__name__}
    return status, payload, (time.perf_counter() - t0) * 1000


status, login, _ = call("/api/auth/login/", {"identifier": USER, "password": PASSWORD})
token = login["access"]
samples = []
for question in QUESTIONS:
    status, body, ms = call("/api/tutoring/chat/", {"message": question, "context": {"surface": "home"}, "history": []},
                            token, timeout=45)
    reply = (body or {}).get("reply") or (body or {}).get("message") or ""
    samples.append({"question": question, "status": status, "ms": round(ms), "reply_chars": len(str(reply)),
                    "keys": sorted((body or {}).keys())[:8]})
    print(samples[-1])
    time.sleep(6)
json.dump(samples, open(OUT, "w"), indent=2)
