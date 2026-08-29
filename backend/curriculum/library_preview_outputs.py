"""Realistic, data-driven terminal transcripts for command-library pages."""

from __future__ import annotations

from curriculum.library_commands import normalize_command_text
from curriculum.terminal_examples import (
    TERMINAL_EXAMPLE_RENDERERS,
    example_command,
    prompt,
    sample_directory_for,
    syntax_title,
    transcript,
)


def _sample_output_for_syntax(command: str) -> str:
    raw = " ".join(str(command).strip().split())
    normalized = normalize_command_text(raw)
    display_command = example_command(raw)
    prompt_text = prompt(display_command)
    for renderer in TERMINAL_EXAMPLE_RENDERERS:
        output = renderer(raw, normalized, display_command, prompt_text)
        if output is not None:
            return output
    return transcript(display_command, "")


_sample_directory_for = sample_directory_for
_syntax_title = syntax_title
