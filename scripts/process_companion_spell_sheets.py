#!/usr/bin/env python3
"""Compatibility wrapper for scripts/assets/process_companion_spell_sheets.py."""
from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'assets' / 'process_companion_spell_sheets.py'
runpy.run_path(str(SCRIPT), run_name="__main__")
