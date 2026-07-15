from __future__ import annotations

import argparse
import math
import os
import random
import struct
import wave
from pathlib import Path

from elevenlabs.core.api_error import ApiError
from elevenlabs.client import ElevenLabs


ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / "frontend" / ".env"
OUTPUT_ROOT = ROOT / "frontend" / "public" / "audio" / "battle"
OUTPUT_FORMAT = "pcm_44100"
MUSIC_OUTPUT_FORMAT = "mp3_44100_128"
OUTPUT_EXT = ".wav"
MUSIC_EXT = ".mp3"
SAMPLE_RATE = 44100


ELEMENT_PROMPTS: dict[str, str] = {
    "flame": (
        "normal high-quality flame magic, warm natural fire crackle, smooth ember whoosh, satisfying fantasy flame texture, "
        "pleasant and clean, no screams, no voices, no horror, no harsh distortion"
    ),
    "ice": (
        "crushed ice magic, packed snow crunch, brittle ice cubes grinding and cracking, sharp frosty chips, "
        "polished fantasy game audio, tactile and non-harsh"
    ),
    "lightning": (
        "futuristic neon lightning magic, cyberpunk electric arcs, glitchy digital stutters, violet plasma zaps, "
        "polished sci-fi fantasy game audio, snappy but not piercing"
    ),
}

SKILL_PHASES: dict[str, tuple[float, str]] = {
    "charge": (
        0.5,
        "animation-synced hand charge, front-loaded energy inhale and pulse in the first beat, clean tiny tail before launch",
    ),
    "projectile": (
        0.5,
        "animation-synced fast projectile flight, crisp left-to-right whoosh in the first beat, no impact, no long tail",
    ),
    "target-center": (
        0.86,
        "animation-synced target body bloom, quick attack then grow-hold-fade aura around the center, no ground rumble",
    ),
    "target-ground": (
        0.84,
        "animation-synced target ground eruption, vertical burst from beneath the enemy, rising column and final ground thump",
    ),
    "ground-run": (
        0.72,
        "animation-synced ground run, elemental energy races along the floor from caster to enemy, crawling cracks, no final impact",
    ),
    "impact": (
        0.5,
        "animation-synced compact hit impact, front-loaded snap burst with a fast dissipating particle tail",
    ),
}

UI_PROMPTS: dict[str, tuple[float, str]] = {
    "button-click": (
        0.5,
        "premium ASMR fantasy interface button click, very short tactile ceramic-and-wood tap, close-mic detail, warm and unobtrusive, no voice, no music",
    ),
    "button-click-soft": (
        0.5,
        "premium ASMR fantasy interface soft button click, tiny felt-damped tap with a warm wood body, close-mic detail, subtle and pleasant, no voice, no music",
    ),
    "button-click-bright": (
        0.5,
        "premium ASMR fantasy interface bright button click, tiny crisp crystal tap with a delicate mechanical tick, close-mic detail, not piercing, no voice, no music",
    ),
    "button-toggle": (
        0.55,
        "premium fantasy interface toggle sound, two tiny ASMR mechanical ticks, soft switch movement, close-mic, satisfying and unobtrusive, no voice, no music",
    ),
    "button-confirm": (
        0.62,
        "positive fantasy interface confirm button sound, short polished ASMR click with a tiny glass chime tail, gentle and pleasant, no voice, no music",
    ),
    "button-dismiss": (
        0.52,
        "premium fantasy interface dismiss button sound, soft lower ASMR click, gentle closing tick, close-mic and restrained, no voice, no music",
    ),
    "button-danger": (
        0.55,
        "premium fantasy interface destructive action button sound, short low tactile warning click, muted metal and wood, serious but not harsh, no alarm, no voice, no music",
    ),
}

BACKGROUND_PROMPTS: dict[str, tuple[float, str]] = {
    "outside-battle-loop": (
        20.0,
        "Instrumental medieval fantasy RPG outside-of-battle music loop. Cozy world-map and village menu music, "
        "clear memorable melody with lute, harp, warm strings, soft flute, and gentle frame drum. Pleasant game music, "
        "not ambience, not background noise, no sound effects, no vocals, no final cadence, no fade out, designed to loop seamlessly.",
    ),
    "inside-battle-loop": (
        20.0,
        "Instrumental medieval fantasy RPG inside-battle music loop. Adventurous combat music with a clear melody, "
        "low strings, lute ostinato, heroic brass, hand drums, and steady rhythmic drive. Pleasant and exciting, "
        "not ambience, not background noise, no sound effects, no vocals, no final cadence, no fade out, designed to loop seamlessly.",
    ),
}

OUTCOME_MUSIC_PROMPTS: dict[str, tuple[float, str]] = {
    "victory": (
        4.8,
        "Short instrumental fantasy RPG victory music stinger. Clear triumphant melody, warm strings, bell-like chimes, "
        "light hand drum lift, satisfying final major cadence. Music only, no sound effects, no vocals.",
    ),
    "game-over": (
        5.2,
        "Short instrumental fantasy RPG game over music stinger. Gentle minor-key lament, low strings, soft bell melody, "
        "slow fading final cadence. Sad but pleasant, music only, no sound effects, no vocals.",
    ),
}

COMPANION_SOUND_PROMPTS: dict[str, dict[str, tuple[float, str]]] = {
    "blue": {
        "hurt": (
            0.55,
            "Non-human game sound effect only: infernal blue hellfire is struck, brief sulfur ember crack and cursed fire puff, "
            "no voice, no breath, no gasp, no moan, no scream, no animal, no human, clean pleasant fantasy SFX.",
        ),
        "death": (
            0.95,
            "Non-human game sound effect only: infernal blue hellfire collapses into hot ash, cursed embers, and a tiny magical fade, "
            "no voice, no breath, no gasp, no moan, no scream, no animal, no human, clean pleasant fantasy SFX.",
        ),
    },
    "white": {
        "hurt": (
            0.55,
            "Non-human game sound effect only: crushed ice companion is struck, packed ice crunch and brittle frosty chips, "
            "no voice, no breath, no gasp, no moan, no scream, no animal, no human, clean pleasant fantasy SFX.",
        ),
        "death": (
            0.95,
            "Non-human game sound effect only: crushed ice companion breaks apart, icy gravel crunch and soft frost shimmer fade, "
            "no voice, no breath, no gasp, no moan, no scream, no animal, no human, clean pleasant fantasy SFX.",
        ),
    },
    "black": {
        "hurt": (
            0.55,
            "Non-human game sound effect only: neon lightning core is struck, short glitchy plasma zap and digital spark crackle, "
            "no voice, no breath, no gasp, no moan, no scream, no animal, no human, clean pleasant fantasy SFX.",
        ),
        "death": (
            0.95,
            "Non-human game sound effect only: neon lightning core powers down, glitch stutter, fading violet arcs and capacitor discharge, "
            "no voice, no breath, no gasp, no moan, no scream, no animal, no human, clean pleasant fantasy SFX.",
        ),
    },
}

SHARED_SOUND_PROMPTS: dict[str, tuple[float, str]] = {
    "monster-hurt": (
        0.6,
        "Non-human monster hurt sound effect for fantasy battle: dull armor impact, stone chips, shield clank, and magic thud. "
        "No voice, no breath, no grunt, no moan, no scream, no animal, no human, non-gory clean game SFX.",
    ),
    "wave-transition": (
        1.5,
        "battle wave transition sound, dimensional gate opens across the battlefield, low reverse swell, crystal portal snap, "
        "soft arrival shimmer, no page turn, no speech, clean fantasy game cue",
    ),
    "run": (
        0.72,
        "seamless looping run footsteps for a small fantasy companion, four even soft cloth-and-boot steps on stone, "
        "brisk animation pace, light gear rustle, no voice, no breath, no speech",
    ),
}

SYSTEM_CUE_NAMES = {"wave-transition", "run"}


def load_api_key() -> str:
    existing = os.environ.get("ELEVENLABS_API_KEY")
    if existing:
        return existing

    if not ENV_PATH.exists():
        raise RuntimeError(f"Missing env file: {ENV_PATH}")

    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.strip() == "ELEVENLABS_API_KEY":
            value = value.strip().strip('"').strip("'")
            if value:
                return value

    raise RuntimeError("ELEVENLABS_API_KEY was not found in frontend/.env or the environment")


def write_wav(path: Path, samples: list[float]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max((abs(sample) for sample in samples), default=1)
    gain = min(1, 0.96 / peak) if peak > 0 else 1
    frames = b"".join(
        struct.pack("<h", int(max(-1, min(1, sample * gain)) * 32767))
        for sample in samples
    )
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(frames)
    return path.stat().st_size


def write_stereo_wav(path: Path, samples: list[float]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    delay = int(0.012 * SAMPLE_RATE)
    widened: list[tuple[float, float]] = []
    for index, sample in enumerate(samples):
        delayed = samples[index - delay] if index >= delay else 0.0
        left = sample * 0.92 + delayed * 0.08
        right = sample * 0.78 - delayed * 0.14
        widened.append((left, right))

    peak = max((max(abs(left), abs(right)) for left, right in widened), default=1)
    gain = min(1, 0.96 / peak) if peak > 0 else 1
    frames = b"".join(
        struct.pack(
            "<hh",
            int(max(-1, min(1, left * gain)) * 32767),
            int(max(-1, min(1, right * gain)) * 32767),
        )
        for left, right in widened
    )
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(frames)
    return path.stat().st_size


def write_pcm_stream(path: Path, chunks) -> int:
    data = bytearray()
    for chunk in chunks:
        data.extend(chunk)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(data)
    return path.stat().st_size


def sound_effect(client: ElevenLabs, path: Path, prompt: str, duration: float, *, loop: bool, force: bool) -> None:
    if path.exists() and path.stat().st_size > 0 and not force:
        print(f"skip {path.relative_to(ROOT)}")
        return

    chunks = client.text_to_sound_effects.convert(
        text=prompt,
        output_format=OUTPUT_FORMAT,
        duration_seconds=duration,
        loop=loop,
        prompt_influence=0.55,
    )
    size = write_pcm_stream(path, chunks)
    print(f"wrote {path.relative_to(ROOT)} ({size} bytes)")


def music_track(client: ElevenLabs, path: Path, prompt: str, duration: float, *, force: bool) -> None:
    if path.exists() and path.stat().st_size > 0 and not force:
        print(f"skip {path.relative_to(ROOT)}")
        return

    chunks = client.music.compose(
        prompt=prompt,
        output_format=MUSIC_OUTPUT_FORMAT,
        music_length_ms=round(duration * 1000),
        model_id="music_v1",
        force_instrumental=True,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    size = 0
    with path.open("wb") as handle:
        for chunk in chunks:
            handle.write(chunk)
            size += len(chunk)
    print(f"wrote {path.relative_to(ROOT)} ({size} bytes)")


def envelope(progress: float, attack: float, release: float) -> float:
    if progress < attack:
        return progress / max(attack, 0.001)
    if progress > 1 - release:
        return max(0, (1 - progress) / max(release, 0.001))
    return 1


def tone(freq: float, t: float, shape: str = "sine") -> float:
    phase = t * freq
    if shape == "square":
        return 1 if math.sin(math.tau * phase) >= 0 else -1
    if shape == "saw":
        return 2 * (phase - math.floor(phase + 0.5))
    return math.sin(math.tau * phase)


def smooth_noise(rng: random.Random, previous: float, amount: float) -> float:
    return previous * (1 - amount) + rng.uniform(-1, 1) * amount


def synth_skill(element: str, phase: str, duration: float) -> list[float]:
    rng = random.Random(f"{element}:{phase}")
    n = int(duration * SAMPLE_RATE)
    samples: list[float] = []
    noise = 0.0
    element_base = {"flame": 170, "ice": 520, "lightning": 240}[element]
    crackle_rate = {"flame": 0.012, "ice": 0.006, "lightning": 0.02}[element]
    crackle = 0.0

    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / max(1, n - 1)
        noise = smooth_noise(rng, noise, 0.045 if element != "ice" else 0.025)
        if rng.random() < crackle_rate:
            crackle += rng.uniform(-1, 1)
        crackle *= 0.88 if element != "lightning" else 0.78

        if phase == "charge":
            amp = envelope(p, 0.08, 0.08) * (0.2 + p * 0.75)
            sweep = element_base * (1.0 + p * (2.6 if element != "ice" else 3.4))
            body = tone(sweep, t) * 0.48 + tone(sweep * 1.5, t) * 0.22
            if element == "lightning":
                body += tone(sweep * 2.02, t, "square") * 0.14
            sample = body * amp + noise * amp * (0.14 if element == "flame" else 0.07) + crackle * 0.12
        elif phase == "projectile":
            amp = envelope(p, 0.02, 0.12) * (1 - p * 0.25)
            sweep = element_base * (2.7 - p * 1.45)
            whoosh = noise * math.sin(math.pi * p) * 0.45
            body = tone(sweep, t, "saw" if element == "lightning" else "sine") * 0.32
            sample = (body + whoosh + crackle * 0.1) * amp
        elif phase == "target-center":
            amp = envelope(p, 0.04, 0.2)
            pulse = 0.55 + 0.45 * math.sin(math.tau * (4 + p * 3) * t)
            body = (
                tone(element_base * 1.2, t) * 0.28
                + tone(element_base * 1.9, t) * 0.2
                + tone(element_base * 2.7, t) * 0.12
            )
            sample = body * amp * pulse + crackle * 0.08 + noise * amp * 0.07
        elif phase == "target-ground":
            amp = envelope(p, 0.05, 0.18)
            rumble = tone(48, t) * 0.34 + tone(72, t) * 0.18
            rise = tone(element_base * (0.8 + p * 1.8), t) * 0.22
            sample = (rumble * (1 - p * 0.3) + rise + noise * 0.2 + crackle * 0.07) * amp
        elif phase == "ground-run":
            amp = envelope(p, 0.02, 0.16)
            pulse = 0.48 + 0.52 * math.sin(math.tau * (7 + p * 4) * t) ** 2
            crawl = tone(element_base * (0.65 + p * 0.85), t, "saw" if element == "lightning" else "sine") * 0.2
            floor = tone(58, t) * 0.18 + tone(96, t) * 0.08
            sample = (floor + crawl + noise * 0.24 + crackle * 0.11) * amp * pulse
        else:
            decay = math.exp(-p * 7.5)
            hit = tone(72, t) * 0.55 * decay
            burst = tone(element_base * (2.1 - p), t, "square" if element == "lightning" else "sine") * 0.28 * decay
            sparkle = tone(element_base * 4.2, t) * 0.18 * math.exp(-p * 4.0)
            sample = hit + burst + sparkle + noise * decay * 0.32 + crackle * 0.16

        if element == "flame":
            sample += noise * 0.05 * envelope(p, 0.02, 0.2)
        elif element == "ice":
            sample += tone(element_base * 3.0, t) * 0.05 * envelope(p, 0.01, 0.35)
        else:
            sample += tone(element_base * 5.0, t, "square") * 0.025 * envelope(p, 0.01, 0.16)
        samples.append(sample * 0.72)

    return samples


def synth_ui(name: str, duration: float) -> list[float]:
    n = int(duration * SAMPLE_RATE)
    samples: list[float] = []
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / max(1, n - 1)
        if name == "button-confirm":
            first = tone(660, t) * math.exp(-p * 10)
            second = tone(880, max(0, t - 0.11)) * math.exp(-max(0, p - 0.18) * 12)
            sample = (first + second * (1 if t > 0.11 else 0)) * envelope(p, 0.01, 0.35)
        else:
            click = tone(920, t) * math.exp(-p * 22)
            wood = tone(220, t) * math.exp(-p * 18)
            sample = (click * 0.45 + wood * 0.22) * envelope(p, 0.005, 0.55)
        samples.append(sample * 0.6)
    return samples


def midi_freq(note: int) -> float:
    return 440 * (2 ** ((note - 69) / 12))


def add_note(
    samples: list[float],
    start: float,
    duration: float,
    freq: float,
    amp: float,
    *,
    shape: str = "sine",
    attack: float = 0.012,
    release: float = 0.18,
    harmonic: float = 0.28,
) -> None:
    start_i = max(0, int(start * SAMPLE_RATE))
    end_i = min(len(samples), int((start + duration) * SAMPLE_RATE))
    if end_i <= start_i:
        return
    total = max(1, end_i - start_i)
    for idx, i in enumerate(range(start_i, end_i)):
        t = idx / SAMPLE_RATE
        p = idx / total
        env = envelope(p, attack, release)
        if release >= 0.35:
            env *= 0.78 + 0.22 * math.sin(math.pi * p)
        else:
            env *= math.exp(-p * 3.2)
        body = tone(freq, t, shape) + tone(freq * 2.01, t) * harmonic + tone(freq * 3.0, t) * harmonic * 0.18
        samples[i] += body * amp * env


def add_drum(samples: list[float], start: float, duration: float, freq: float, amp: float, *, noise: bool = False) -> None:
    rng = random.Random(f"drum:{start}:{freq}:{amp}")
    start_i = max(0, int(start * SAMPLE_RATE))
    end_i = min(len(samples), int((start + duration) * SAMPLE_RATE))
    for idx, i in enumerate(range(start_i, end_i)):
        t = idx / SAMPLE_RATE
        p = idx / max(1, end_i - start_i)
        env = math.exp(-p * 8.0)
        body = tone(freq * (1 - p * 0.35), t) * 0.9
        if noise:
            body += rng.uniform(-1, 1) * 0.18
        samples[i] += body * amp * env


def synth_background(name: str, duration: float) -> list[float]:
    n = int(duration * SAMPLE_RATE)
    samples = [0.0 for _ in range(n)]
    is_battle = name.startswith("inside")
    bpm = 120 if is_battle else 96
    beat = 60 / bpm

    if is_battle:
        root = 45  # A2
        scale = [0, 2, 3, 5, 7, 8, 10, 12]
        melody = [7, 6, 4, 5, 7, 9, 8, 7, 6, 4, 2, 3, 5, 7, 5, 4]
        chord_roots = [0, 5, 3, 6, 0, 5, 7, 3, 6, 5]
        bars = int(duration / (beat * 4))
        for bar in range(bars):
            base_t = bar * 4 * beat
            degree = chord_roots[bar % len(chord_roots)]
            for chord_note in (degree, degree + 2, degree + 4):
                add_note(samples, base_t, 3.9 * beat, midi_freq(root + 12 + scale[chord_note % len(scale)]), 0.035, release=0.42)
                add_note(samples, base_t, 3.9 * beat, midi_freq(root + 24 + scale[chord_note % len(scale)]), 0.015, release=0.42)
            for step in range(8):
                degree = [0, 2, 4, 5, 4, 2, 0, 5][step]
                add_note(samples, base_t + step * 0.5 * beat, 0.42 * beat, midi_freq(root + 12 + scale[degree]), 0.04, shape="saw", harmonic=0.18)
            for step in range(4):
                degree = melody[(bar * 4 + step) % len(melody)]
                add_note(samples, base_t + step * beat, 0.86 * beat, midi_freq(root + 24 + scale[degree % len(scale)]), 0.032, release=0.22)
            for drum_beat in (0, 2):
                add_drum(samples, base_t + drum_beat * beat, 0.34, 62, 0.14)
            for drum_beat in (1, 3):
                add_drum(samples, base_t + drum_beat * beat, 0.22, 145, 0.075, noise=True)
            for step in range(8):
                add_drum(samples, base_t + step * 0.5 * beat, 0.08, 260, 0.018, noise=True)
    else:
        root = 50  # D3
        scale = [0, 2, 3, 5, 7, 9, 10, 12]
        melody = [4, 5, 7, 5, 4, 2, 0, 2, 4, 7, 9, 7, 5, 4, 2, 0]
        chord_roots = [0, 3, 5, 4, 0, 5, 3, 4]
        bars = int(duration / (beat * 4))
        for bar in range(bars):
            base_t = bar * 4 * beat
            degree = chord_roots[bar % len(chord_roots)]
            for chord_note in (degree, degree + 2, degree + 4):
                add_note(samples, base_t, 3.8 * beat, midi_freq(root + scale[chord_note % len(scale)]), 0.032, release=0.5)
            for step in range(8):
                degree = [0, 2, 4, 2, 5, 4, 2, 4][step]
                add_note(samples, base_t + step * 0.5 * beat, 0.45 * beat, midi_freq(root + 12 + scale[degree]), 0.045, harmonic=0.2)
            if bar % 2 == 0:
                for step in range(4):
                    degree = melody[((bar // 2) * 4 + step) % len(melody)]
                    add_note(samples, base_t + step * beat, 0.9 * beat, midi_freq(root + 24 + scale[degree % len(scale)]), 0.032, release=0.26)
            add_drum(samples, base_t, 0.26, 74, 0.075)
            add_drum(samples, base_t + 2 * beat, 0.26, 74, 0.055)

    fade = int(0.035 * SAMPLE_RATE)
    for i in range(fade):
        scale = i / max(1, fade - 1)
        samples[i] *= scale
        samples[-i - 1] *= scale
    return samples


def synth_outcome_music(name: str, duration: float) -> list[float]:
    n = int(duration * SAMPLE_RATE)
    samples = [0.0 for _ in range(n)]

    if name == "victory":
        root = 50  # D3
        scale = [0, 2, 4, 5, 7, 9, 11, 12]
        bpm = 132
        beat = 60 / bpm
        chords = [0, 4, 5, 0]
        melody = [0, 2, 4, 7, 9, 7, 11, 12, 14, 12]

        for bar, degree in enumerate(chords):
            base_t = bar * 2 * beat
            for chord_degree in (degree, degree + 2, degree + 4):
                octave = 12 * (chord_degree // len(scale))
                note = root + 12 + scale[chord_degree % len(scale)] + octave
                add_note(samples, base_t, 1.9 * beat, midi_freq(note), 0.052, shape="saw", release=0.48, harmonic=0.16)
                add_note(samples, base_t, 1.9 * beat, midi_freq(note + 12), 0.016, release=0.5, harmonic=0.1)
            add_note(samples, base_t, 1.8 * beat, midi_freq(root - 12 + scale[degree % len(scale)]), 0.055, release=0.46)
            add_drum(samples, base_t, 0.22, 72, 0.09)
            add_drum(samples, base_t + beat, 0.16, 190, 0.04, noise=True)

        for index, degree in enumerate(melody):
            start = 0.25 + index * 0.42
            if start >= duration - 0.5:
                break
            octave = 12 * (degree // len(scale))
            note = root + 24 + scale[degree % len(scale)] + octave
            add_note(samples, start, 0.36, midi_freq(note), 0.058, release=0.18, harmonic=0.22)

        final_t = duration - 1.15
        for note in (root + 24, root + 28, root + 31, root + 38):
            add_note(samples, final_t, 1.05, midi_freq(note), 0.048, release=0.55, harmonic=0.18)
        add_drum(samples, final_t, 0.32, 58, 0.12)
    else:
        root = 45  # A2
        minor_scale = [0, 2, 3, 5, 7, 8, 10, 12]
        bpm = 78
        beat = 60 / bpm
        chords = [0, 5, 3, 4]
        melody = [7, 6, 5, 4, 2, 1, 0]

        for bar, degree in enumerate(chords):
            base_t = bar * 1.35 * beat
            for chord_degree in (degree, degree + 2, degree + 4):
                octave = 12 * (chord_degree // len(minor_scale))
                note = root + minor_scale[chord_degree % len(minor_scale)] + octave
                add_note(samples, base_t, 1.28 * beat, midi_freq(note), 0.045, release=0.62, harmonic=0.12)
                add_note(samples, base_t, 1.28 * beat, midi_freq(note + 12), 0.018, release=0.6, harmonic=0.1)
            add_note(samples, base_t, 1.25 * beat, midi_freq(root - 12 + minor_scale[degree % len(minor_scale)]), 0.05, release=0.7)
            add_drum(samples, base_t, 0.34, 52, 0.055)

        for index, degree in enumerate(melody):
            start = 0.4 + index * 0.56
            octave = 12 * (degree // len(minor_scale))
            note = root + 24 + minor_scale[degree % len(minor_scale)] + octave
            add_note(samples, start, 0.62, midi_freq(note), 0.046, release=0.35, harmonic=0.12)

        final_t = duration - 1.55
        for note in (root, root + 3, root + 7, root + 12):
            add_note(samples, final_t, 1.45, midi_freq(note), 0.04, release=0.75, harmonic=0.1)

    fade = int(0.08 * SAMPLE_RATE)
    for i in range(fade):
        scale = i / max(1, fade - 1)
        samples[i] *= scale
        samples[-i - 1] *= scale
    return samples


def synth_soft_event(duration: float, seed: str) -> list[float]:
    rng = random.Random(seed)
    n = int(duration * SAMPLE_RATE)
    base = 220 + (sum(ord(ch) for ch in seed) % 320)
    samples: list[float] = []
    noise = 0.0
    for i in range(n):
        t = i / SAMPLE_RATE
        p = i / max(1, n - 1)
        noise = smooth_noise(rng, noise, 0.035)
        decay = math.exp(-p * 4.5)
        body = tone(base * (1 + p * 0.35), t) * 0.24 + tone(base * 1.5, t) * 0.12
        sparkle = tone(base * 2.8, t) * 0.08 * math.exp(-p * 3.5)
        samples.append((body + sparkle + noise * 0.12) * decay * envelope(p, 0.02, 0.22))
    return samples


def selected_elements(element_filter: str | None) -> dict[str, str]:
    if not element_filter:
        return ELEMENT_PROMPTS
    return {element_filter: ELEMENT_PROMPTS[element_filter]}


def generate_procedural(force: bool, only: str, element_filter: str | None) -> None:
    if only in {"all", "sfx", "skills"}:
        for element in selected_elements(element_filter):
            for phase, (duration, _prompt) in SKILL_PHASES.items():
                path = OUTPUT_ROOT / "skills" / element / f"{phase}{OUTPUT_EXT}"
                if path.exists() and path.stat().st_size > 0 and not force:
                    print(f"skip {path.relative_to(ROOT)}")
                    continue
                size = write_wav(path, synth_skill(element, phase, duration))
                print(f"wrote {path.relative_to(ROOT)} ({size} bytes)")

    if only == "skills":
        return

    if only in {"all", "sfx", "ui"}:
        for name, (duration, _prompt) in UI_PROMPTS.items():
            path = OUTPUT_ROOT / "ui" / f"{name}{OUTPUT_EXT}"
            if path.exists() and path.stat().st_size > 0 and not force:
                print(f"skip {path.relative_to(ROOT)}")
                continue
            size = write_wav(path, synth_ui(name, duration))
            print(f"wrote {path.relative_to(ROOT)} ({size} bytes)")

    if only == "ui":
        return

    if only in {"all", "backgrounds"}:
        for name, (duration, _prompt) in BACKGROUND_PROMPTS.items():
            path = OUTPUT_ROOT / "background" / f"{name}{OUTPUT_EXT}"
            if path.exists() and path.stat().st_size > 0 and not force:
                print(f"skip {path.relative_to(ROOT)}")
                continue
            size = write_stereo_wav(path, synth_background(name, duration))
            print(f"wrote {path.relative_to(ROOT)} ({size} bytes)")

    if only in {"all", "outcomes"}:
        for name, (duration, _prompt) in OUTCOME_MUSIC_PROMPTS.items():
            path = OUTPUT_ROOT / "system" / f"{name}{OUTPUT_EXT}"
            if path.exists() and path.stat().st_size > 0 and not force:
                print(f"skip {path.relative_to(ROOT)}")
                continue
            size = write_stereo_wav(path, synth_outcome_music(name, duration))
            print(f"wrote {path.relative_to(ROOT)} ({size} bytes)")

    if only in {"all", "sfx"}:
        for companion, sounds in COMPANION_SOUND_PROMPTS.items():
            for name, (duration, _prompt) in sounds.items():
                path = OUTPUT_ROOT / "companions" / companion / f"{name}{OUTPUT_EXT}"
                if path.exists() and path.stat().st_size > 0 and not force:
                    print(f"skip {path.relative_to(ROOT)}")
                    continue
                size = write_wav(path, synth_soft_event(duration, f"{companion}:{name}"))
                print(f"wrote {path.relative_to(ROOT)} ({size} bytes)")

        for name, (duration, _prompt) in SHARED_SOUND_PROMPTS.items():
            folder = "monsters" if name == "monster-hurt" else "system"
            file_name = "hurt" if name == "monster-hurt" else name
            path = OUTPUT_ROOT / folder / f"{file_name}{OUTPUT_EXT}"
            if path.exists() and path.stat().st_size > 0 and not force:
                print(f"skip {path.relative_to(ROOT)}")
                continue
            size = write_wav(path, synth_soft_event(duration, name))
            print(f"wrote {path.relative_to(ROOT)} ({size} bytes)")

    if only == "system-cues":
        for name in SYSTEM_CUE_NAMES:
            duration, _prompt = SHARED_SOUND_PROMPTS[name]
            path = OUTPUT_ROOT / "system" / f"{name}{OUTPUT_EXT}"
            if path.exists() and path.stat().st_size > 0 and not force:
                print(f"skip {path.relative_to(ROOT)}")
                continue
            size = write_wav(path, synth_soft_event(duration, name))
            print(f"wrote {path.relative_to(ROOT)} ({size} bytes)")


def describe_api_error(exc: ApiError) -> str:
    detail = exc.body.get("detail", {}) if isinstance(exc.body, dict) else {}
    if isinstance(detail, dict):
        message = detail.get("message") or detail.get("status") or str(detail)
        code = detail.get("code")
        return f"{code}: {message}" if code else str(message)
    return str(exc)


def generate_elevenlabs(client: ElevenLabs, force: bool, only: str, element_filter: str | None) -> None:
    if only in {"all", "sfx", "skills"}:
        for element, element_prompt in selected_elements(element_filter).items():
            for phase, (duration, phase_prompt) in SKILL_PHASES.items():
                prompt = f"{element_prompt}; {phase_prompt}; dry game sound effect, no music, no speech"
                path = OUTPUT_ROOT / "skills" / element / f"{phase}{OUTPUT_EXT}"
                sound_effect(client, path, prompt, duration, loop=False, force=force)

    if only == "skills":
        return

    if only in {"all", "sfx", "ui"}:
        for name, (duration, prompt) in UI_PROMPTS.items():
            sound_effect(client, OUTPUT_ROOT / "ui" / f"{name}{OUTPUT_EXT}", prompt, duration, loop=False, force=force)

    if only == "ui":
        return

    if only in {"all", "sfx"}:
        for companion, sounds in COMPANION_SOUND_PROMPTS.items():
            for name, (duration, prompt) in sounds.items():
                sound_effect(
                    client,
                    OUTPUT_ROOT / "companions" / companion / f"{name}{OUTPUT_EXT}",
                    prompt,
                    duration,
                    loop=False,
                    force=force,
                )

        for name, (duration, prompt) in SHARED_SOUND_PROMPTS.items():
            folder = "monsters" if name == "monster-hurt" else "system"
            file_name = "hurt" if name == "monster-hurt" else name
            sound_effect(
                client,
                OUTPUT_ROOT / folder / f"{file_name}{OUTPUT_EXT}",
                prompt,
                duration,
                loop=name == "run",
                force=force,
            )

    if only == "system-cues":
        for name in SYSTEM_CUE_NAMES:
            duration, prompt = SHARED_SOUND_PROMPTS[name]
            sound_effect(
                client,
                OUTPUT_ROOT / "system" / f"{name}{OUTPUT_EXT}",
                prompt,
                duration,
                loop=name == "run",
                force=force,
            )

    if only in {"all", "outcomes"}:
        for name, (duration, prompt) in OUTCOME_MUSIC_PROMPTS.items():
            music_track(
                client,
                OUTPUT_ROOT / "system" / f"{name}{MUSIC_EXT}",
                prompt,
                duration,
                force=force,
            )

    if only in {"all", "backgrounds"}:
        for name, (duration, prompt) in BACKGROUND_PROMPTS.items():
            music_track(
                client,
                OUTPUT_ROOT / "background" / f"{name}{MUSIC_EXT}",
                prompt,
                duration,
                force=force,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate battle SFX with ElevenLabs.")
    parser.add_argument("--force", action="store_true", help="Regenerate files even when they already exist.")
    parser.add_argument("--procedural", action="store_true", help="Use the local procedural generator.")
    parser.add_argument(
        "--only",
        choices=["all", "sfx", "ui", "skills", "system-cues", "backgrounds", "outcomes"],
        default="all",
        help="Limit generation to one asset group.",
    )
    parser.add_argument(
        "--element",
        choices=sorted(ELEMENT_PROMPTS),
        default=None,
        help="Limit skill generation to one element.",
    )
    args = parser.parse_args()

    if args.procedural:
        generate_procedural(args.force, args.only, args.element)
        return

    client = ElevenLabs(api_key=load_api_key())

    try:
        generate_elevenlabs(client, args.force, args.only, args.element)
    except ApiError as exc:
        print(f"ElevenLabs generation failed: {describe_api_error(exc)}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
