#!/usr/bin/env python3
"""Generate smaller delivery copies while preserving PNG and WAV originals.

Requires Pillow and ffmpeg locally; deployment builds use the generated files
and do not need the encoders. Preview by default; use --apply to write copies
and update literal frontend references. Dynamic URLs use optimizedPublicMedia.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
PUBLIC = FRONTEND / "public"
SOURCE = FRONTEND / "src"
MANIFEST = SOURCE / "shared" / "media" / "optimizedPublicMedia.json"
FINGERPRINTS = FRONTEND / "media-sources.json"
SKIPPED = {"raw", "_raw", "_shift_raw", "pose", "references", "samples"}
PUBLIC_ROOTS = (
    "cosmetics/companion",
    "cosmetics/story-worlds/arcane-spire",
    "mascot",
)
ASSET_IMPORT = re.compile(r"@/assets/[^\s\"'`]+?(?:\.png|\.lossless\.webp)")


def source_files() -> list[Path]:
    return sorted(
        p
        for p in SOURCE.rglob("*")
        if p.is_file()
        and p.suffix in {".ts", ".tsx", ".css", ".json"}
        and "raw" not in p.relative_to(SOURCE).parts
        and p != MANIFEST
    )


def image_candidates(files: list[Path]) -> list[Path]:
    candidates = {
        p
        for folder in PUBLIC_ROOTS
        for p in (PUBLIC / folder).rglob("*.png")
        if not SKIPPED.intersection(p.relative_to(PUBLIC).parts) and not p.name.startswith("_")
    }
    for source in files:
        if ".test." in source.name:
            continue
        for reference in ASSET_IMPORT.findall(source.read_text(encoding="utf-8")):
            original = reference.replace(".lossless.webp", ".png")
            candidates.add(SOURCE / original.removeprefix("@/"))
    return sorted(candidates)


def lossless_copy(source: Path) -> tuple[Path, bytes | None]:
    with Image.open(source) as opened:
        image = opened.convert("RGBA")
        output = io.BytesIO()
        image.save(output, format="WEBP", lossless=True, exact=True, method=4)
        payload = output.getvalue()
        if len(payload) >= source.stat().st_size:
            return source, None
        with Image.open(io.BytesIO(payload)) as decoded:
            if image.size != decoded.size or image.tobytes() != decoded.convert("RGBA").tobytes():
                raise RuntimeError(f"Lossless pixel verification failed: {source}")
    return source, payload


def audio_copy(source: Path, target: Path) -> None:
    # Seekable files preserve encoder delay/padding metadata for gapless loops.
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(source),
            "-map_metadata",
            "-1",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "128k",
            "-write_xing",
            "1",
            str(target),
        ],
        check=True,
    )


def media_fingerprint(source: Path, target: Path) -> dict[str, str]:
    return {
        "target": target.relative_to(FRONTEND).as_posix(),
        "sourceSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "targetSha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    files = source_files()
    previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    public_mapping: dict[str, str] = {}
    source_mapping: dict[str, str] = {}
    fingerprints: dict[str, dict[str, str]] = {}
    before = after = 0
    count = 0
    with ThreadPoolExecutor(max_workers=2) as workers:
        for original, payload in workers.map(lossless_copy, image_candidates(files)):
            if payload is None:
                continue
            optimized = original.with_suffix(".lossless.webp")
            if original.is_relative_to(PUBLIC):
                public_mapping["/" + original.relative_to(PUBLIC).as_posix()] = (
                    "/" + optimized.relative_to(PUBLIC).as_posix()
                )
            else:
                source_mapping["@/" + original.relative_to(SOURCE).as_posix()] = (
                    "@/" + optimized.relative_to(SOURCE).as_posix()
                )
            if args.apply:
                optimized.write_bytes(payload)
                fingerprints[original.relative_to(FRONTEND).as_posix()] = media_fingerprint(
                    original, optimized
                )
            before += original.stat().st_size
            after += len(payload)
            count += 1

    if args.apply:
        for name in ("inside-battle-loop", "outside-battle-loop"):
            original = PUBLIC / "audio" / "battle" / "background" / f"{name}.wav"
            optimized = original.with_suffix(".mp3")
            audio_copy(original, optimized)
            fingerprints[original.relative_to(FRONTEND).as_posix()] = media_fingerprint(
                original, optimized
            )
            public_mapping["/" + original.relative_to(PUBLIC).as_posix()] = (
                "/" + optimized.relative_to(PUBLIC).as_posix()
            )

        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(
            json.dumps(public_mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        FINGERPRINTS.write_text(
            json.dumps(fingerprints, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        replacements = {**public_mapping, **source_mapping}
        for source in files:
            original_text = source.read_text(encoding="utf-8")
            updated = original_text
            # Revert earlier generated paths before applying the new mapping;
            # an edited PNG may no longer benefit from conversion on a rerun.
            for original, optimized in previous.items():
                updated = updated.replace(optimized, original)
            updated = ASSET_IMPORT.sub(
                lambda match: match.group(0).replace(".lossless.webp", ".png"), updated
            )
            for original, optimized in replacements.items():
                updated = updated.replace(original, optimized)
            if updated != original_text:
                source.write_text(updated, encoding="utf-8", newline="\n")

    print(
        json.dumps(
            {
                "applied": args.apply,
                "pixel_verified_images": count,
                "PNG_MB": round(before / 1e6, 2),
                "WebP_MB": round(after / 1e6, 2),
                "image_savings_MB": round((before - after) / 1e6, 2),
                "public_image_copies": len(public_mapping) - (2 if args.apply else 0),
                "imported_image_copies": len(source_mapping),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
