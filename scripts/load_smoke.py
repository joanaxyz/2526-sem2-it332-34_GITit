#!/usr/bin/env python3
"""Dependency-free concurrent HTTP smoke test for a deployed environment."""

from __future__ import annotations

import argparse
import http.client
import os
import ssl
import statistics
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from urllib.parse import SplitResult, urlsplit


@dataclass
class Results:
    latencies_ms: list[float] = field(default_factory=list)
    status_counts: Counter[int] = field(default_factory=Counter)
    errors: Counter[str] = field(default_factory=Counter)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def record_response(self, status: int, latency_ms: float, expected_status: int) -> None:
        with self.lock:
            self.latencies_ms.append(latency_ms)
            self.status_counts[status] += 1
            if status != expected_status:
                self.errors[f"HTTP {status}"] += 1

    def record_exception(self, error: Exception, latency_ms: float) -> None:
        with self.lock:
            self.latencies_ms.append(latency_ms)
            self.errors[type(error).__name__] += 1


def parse_target(value: str) -> SplitResult:
    target = urlsplit(value)
    if target.scheme not in {"http", "https"} or not target.hostname:
        raise argparse.ArgumentTypeError("target must be an http:// or https:// URL")
    if target.query or target.fragment:
        raise argparse.ArgumentTypeError("put query strings in --path, not in the target URL")
    return target


def request_path(target: SplitResult, path: str) -> str:
    if not path.startswith("/"):
        raise ValueError(f"request path must start with '/': {path!r}")
    prefix = target.path.rstrip("/")
    return f"{prefix}{path}" if prefix else path


def new_connection(target: SplitResult, timeout: float) -> http.client.HTTPConnection:
    port = target.port or (443 if target.scheme == "https" else 80)
    if target.scheme == "https":
        return http.client.HTTPSConnection(
            target.hostname,
            port,
            timeout=timeout,
            context=ssl.create_default_context(),
        )
    return http.client.HTTPConnection(target.hostname, port, timeout=timeout)


def run_user(
    user_number: int,
    *,
    target: SplitResult,
    paths: tuple[str, ...],
    headers: dict[str, str],
    timeout: float,
    deadline: float,
    expected_status: int,
    start: threading.Barrier,
    results: Results,
) -> None:
    connection = new_connection(target, timeout)
    start.wait()
    request_number = user_number

    while time.monotonic() < deadline:
        path = request_path(target, paths[request_number % len(paths)])
        request_started = time.perf_counter()
        try:
            connection.request("GET", path, headers=headers)
            response = connection.getresponse()
            response.read()
            elapsed_ms = (time.perf_counter() - request_started) * 1_000
            results.record_response(response.status, elapsed_ms, expected_status)
        except Exception as error:  # noqa: BLE001 - every failed request belongs in the report
            elapsed_ms = (time.perf_counter() - request_started) * 1_000
            results.record_exception(error, elapsed_ms)
            connection.close()
            connection = new_connection(target, timeout)
        request_number += 1

    connection.close()


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[index]


def parser() -> argparse.ArgumentParser:
    load_parser = argparse.ArgumentParser(
        description="Run a bounded concurrent GET smoke test against a deployed GIT-IT environment.",
    )
    load_parser.add_argument(
        "target",
        type=parse_target,
        help="deployment origin, for example https://git-it.example.com",
    )
    load_parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        default=[],
        help="path to exercise; repeat for a round-robin mix (default: /api/health/ready/)",
    )
    load_parser.add_argument(
        "--users", type=int, default=100, help="concurrent virtual users (default: 100)"
    )
    load_parser.add_argument(
        "--duration",
        type=float,
        default=60,
        help="test duration in seconds (default: 60)",
    )
    load_parser.add_argument(
        "--timeout",
        type=float,
        default=10,
        help="per-request timeout in seconds (default: 10)",
    )
    load_parser.add_argument("--expected-status", type=int, default=200)
    load_parser.add_argument(
        "--max-error-rate",
        type=float,
        default=0.01,
        help="failure threshold as a fraction",
    )
    load_parser.add_argument(
        "--max-p95-ms", type=float, default=750, help="p95 latency failure threshold"
    )
    return load_parser


def main() -> int:
    args = parser().parse_args()
    if args.users < 1 or args.duration <= 0 or args.timeout <= 0:
        parser().error("--users, --duration, and --timeout must be positive")
    if not 0 <= args.max_error_rate <= 1 or args.max_p95_ms <= 0:
        parser().error("--max-error-rate must be 0..1 and --max-p95-ms must be positive")

    paths = tuple(args.paths or ["/api/health/ready/"])
    try:
        for path in paths:
            request_path(args.target, path)
    except ValueError as error:
        parser().error(str(error))

    headers = {"Accept": "application/json", "User-Agent": "git-it-load-smoke/1.0"}
    bearer_token = os.environ.get("LOAD_TEST_BEARER_TOKEN")
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    results = Results()
    started = time.monotonic()
    deadline = started + args.duration
    start = threading.Barrier(args.users)
    with ThreadPoolExecutor(max_workers=args.users, thread_name_prefix="load-user") as executor:
        futures = [
            executor.submit(
                run_user,
                user_number,
                target=args.target,
                paths=paths,
                headers=headers,
                timeout=args.timeout,
                deadline=deadline,
                expected_status=args.expected_status,
                start=start,
                results=results,
            )
            for user_number in range(args.users)
        ]
        for future in futures:
            future.result()

    elapsed = time.monotonic() - started
    total = len(results.latencies_ms)
    failures = sum(results.errors.values())
    error_rate = failures / total if total else 1.0
    p95_ms = percentile(results.latencies_ms, 0.95)

    print(
        f"target={args.target.geturl()} users={args.users} duration={elapsed:.1f}s requests={total}"
    )
    print(
        f"throughput={total / elapsed:.1f} req/s errors={failures} ({error_rate:.2%}) "
        f"latency_ms p50={statistics.median(results.latencies_ms) if total else 0:.1f} "
        f"p95={p95_ms:.1f} p99={percentile(results.latencies_ms, 0.99):.1f}"
    )
    print(f"statuses={dict(sorted(results.status_counts.items()))} errors={dict(results.errors)}")

    failed = total == 0 or error_rate > args.max_error_rate or p95_ms > args.max_p95_ms
    if failed:
        print(
            f"FAILED thresholds: error_rate<={args.max_error_rate:.2%}, p95<={args.max_p95_ms:.1f}ms",
            file=sys.stderr,
        )
        return 1
    print("PASSED load-smoke thresholds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
