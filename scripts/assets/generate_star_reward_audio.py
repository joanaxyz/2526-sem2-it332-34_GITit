"""Generate the soft-magic star-reward cues with the configured ElevenLabs key.

Run from the repository root: python scripts/assets/generate_star_reward_audio.py
Existing assets are preserved unless --force is passed. Original API responses
and the exact prompts are kept alongside the other raw source assets.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from elevenlabs.client import ElevenLabs
from elevenlabs.core.api_error import ApiError

from generate_battle_audio import ROOT, load_api_key


RAW_ROOT = ROOT / "frontend/src/assets/raw/audio/star-rewards/soft-magic-v2"
OUTPUT_ROOT = ROOT / "frontend/public/audio/battle/rewards"
MODEL = "eleven_text_to_sound_v2"
OUTPUT_FORMAT = "mp3_44100_128"

STYLE = (
    "Soft magical UI reward: airy fairy shimmer and a rounded glass chime, velvety attack, "
    "delicate sparkles, natural fading tail. Clean stereo SFX. "
    "No click, impact, beep, harsh metal ringing, voice, percussion or music bed. "
)

CUES = {
    0: (1.4, "No stars: a tiny breath of soft enchanted air gently settles and fades. "
        "Warm and understanding, almost a whisper of fairy dust. No bell note, sad melody, alarm or reward flourish."),
    1: (1.8, "First star: one gentle mid-register chime near D5 appears immediately inside a tiny rising cloud "
        "of sparkling air. Intimate, warm, weightless wonder. Single rounded note with a smooth unhurried decay."),
    2: (2.0, "Second star: one gentle mid-register chime near F sharp 5 appears immediately, a little higher "
        "than the first, wrapped in floating fairy dust. Silky and warm, with a smooth softly sparkling decay."),
    3: (2.4, "Third star: one gentle chime near A5 appears immediately and blooms into a soft luminous "
        "D-major glass harmony, then dissolves into airy sparkles. A tender magical completion, no loud fanfare or extra strikes."),
}


def generate(grade: int, *, client: ElevenLabs, force: bool, render_only: bool) -> None:
    output = OUTPUT_ROOT / f"star-{grade}-soft.wav"
    if output.exists() and not force and not render_only:
        print(f"skip {output.relative_to(ROOT)}", flush=True)
        return

    duration, description = CUES[grade]
    if len(STYLE + description) > 450:
        raise ValueError(f"Star {grade}: ElevenLabs prompts must fit within 450 characters")
    source = RAW_ROOT / f"star-{grade}.mp3"
    if render_only and not source.exists():
        raise RuntimeError(f"Missing original audio: {source.relative_to(ROOT)}")
    if not render_only and (force or not source.exists()):
        chunks = client.text_to_sound_effects.convert(
            text=STYLE + description,
            model_id=MODEL,
            output_format=OUTPUT_FORMAT,
            duration_seconds=duration,
            prompt_influence=0.65,
            loop=False,
        )
        data = b"".join(chunks)
        if len(data) < 1024:
            raise RuntimeError(f"Star {grade}: empty or incomplete audio response")
        source.write_bytes(data)

    # Preserve the longer natural tails. Round the attack and tame bright
    # overtones so the three overlapping reveals remain gentle.
    filters = (
        "silenceremove=start_periods=1:start_duration=0.015:start_threshold=-52dB,"
        "highpass=f=140,lowpass=f=6200,"
        "loudnorm=I=-20:TP=-4:LRA=7,"
        f"apad,atrim=duration={duration},"
        "afade=t=in:st=0:d=0.035,"
        f"afade=t=out:st={duration - 0.65:.2f}:d=0.65"
    )
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
         "-af", filters, "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(output)],
        check=True,
    )
    print(f"wrote {output.relative_to(ROOT)} ({output.stat().st_size} bytes)", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Regenerate existing cues (uses API credits).")
    parser.add_argument("--render-only", action="store_true", help="Remix existing originals without API calls.")
    args = parser.parse_args()
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for grade, (_, description) in CUES.items():
        if len(STYLE + description) > 450:
            raise ValueError(f"Star {grade}: ElevenLabs prompts must fit within 450 characters")
    manifest = {
        "provider": "ElevenLabs", "style": "Soft magic: airy shimmer and gentle chimes",
        "model": MODEL, "output_format": OUTPUT_FORMAT,
        "prompt_influence": 0.65,
        "api_reference": "https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert",
        "cues": {str(grade): {"duration_seconds": duration, "prompt": STYLE + description}
                 for grade, (duration, description) in CUES.items()},
    }
    (RAW_ROOT / "generation.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    client = ElevenLabs(api_key=load_api_key())
    for grade in CUES:
        try:
            generate(grade, client=client, force=args.force, render_only=args.render_only)
        except ApiError as exc:
            # Do not print request objects, headers, or credential values.
            raise SystemExit(f"ElevenLabs rejected star {grade} (HTTP {exc.status_code}).") from None


if __name__ == "__main__":
    main()
