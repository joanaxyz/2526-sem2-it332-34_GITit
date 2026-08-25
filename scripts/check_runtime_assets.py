#!/usr/bin/env python3
"""Verify that root-relative frontend media can ship in a clean Git build."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_SOURCE = ROOT / "frontend" / "src"
PUBLIC_ROOT = ROOT / "frontend" / "public"
SOURCE_SUFFIXES = {".css", ".json", ".ts", ".tsx"}
MEDIA_PATH = re.compile(
    r"/(?:audio|cosmetics)/[^\s\"'`(){}]+?"
    r"\.(?:gif|jpe?g|json|mp3|ogg|png|svg|wav|webp)",
    re.IGNORECASE,
)


def _runtime_source_files() -> Iterable[Path]:
    for path in FRONTEND_SOURCE.rglob("*"):
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if ".test." in path.name or path.name.endswith(".d.ts") or "test" in path.parts:
            continue
        yield path


def _json_strings(value: object) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _json_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _json_strings(nested)


def _asset_references() -> set[str]:
    references: set[str] = set()
    for path in _runtime_source_files():
        source = path.read_text(encoding="utf-8")
        searchable = source
        if path.suffix != ".json":
            # Documentation examples are not runtime requests. Remove block
            # comments and whole-line comments before collecting literals.
            searchable = re.sub(r"/\*.*?\*/", "", searchable, flags=re.DOTALL)
            searchable = "\n".join(
                line for line in searchable.splitlines() if not line.lstrip().startswith("//")
            )
        references.update(match.group(0) for match in MEDIA_PATH.finditer(searchable))
        if path.suffix == ".json":
            try:
                payload = json.loads(source)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Cannot parse {path.relative_to(ROOT)}: {exc}") from exc
            for value in _json_strings(payload):
                if MEDIA_PATH.fullmatch(value):
                    references.add(value)
    return references


def _git_lines(*args: str, input_text: str | None = None) -> list[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.splitlines()


def _tracked_public_files() -> set[str]:
    return {
        line.replace("\\", "/")
        for line in _git_lines("ls-files", "--cached", "--", "frontend/public")
    }


def _export_ignored(paths: list[str]) -> list[str]:
    if not paths:
        return []
    output = _git_lines("check-attr", "--stdin", "export-ignore", input_text="\n".join(paths))
    ignored: list[str] = []
    for line in output:
        path, _attribute, value = line.rsplit(": ", 2)
        if value not in {"unspecified", "unset"}:
            ignored.append(path)
    return ignored


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-tracked",
        action="store_true",
        help="Fail when a referenced file exists locally but is not in the Git index.",
    )
    args = parser.parse_args()

    references = sorted(_asset_references())
    tracked = _tracked_public_files()
    missing: list[str] = []
    untracked: list[str] = []

    for reference in references:
        relative = f"frontend/public{reference}"
        if not (PUBLIC_ROOT / reference.removeprefix("/")).is_file():
            missing.append(reference)
        elif relative not in tracked:
            untracked.append(reference)

    archive_excluded = _export_ignored([f"frontend/public{reference}" for reference in references])

    errors: list[str] = []
    if missing:
        errors.append("Missing runtime media:\n  " + "\n  ".join(missing))
    if archive_excluded:
        errors.append(
            "Runtime media excluded from git archive:\n  " + "\n  ".join(archive_excluded)
        )
    if untracked and args.require_tracked:
        errors.append("Untracked runtime media:\n  " + "\n  ".join(untracked))

    if errors:
        print("Runtime asset deployment check failed.", file=sys.stderr)
        print("\n\n".join(errors), file=sys.stderr)
        return 1

    detail = f", {len(untracked)} present but untracked" if untracked else ""
    print(f"Runtime asset deployment check passed ({len(references)} references{detail}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
