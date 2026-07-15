#!/usr/bin/env python3
"""Compatibility wrapper for scripts/assets/shift_monster_raw.py."""
from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'assets' / 'shift_monster_raw.py'
runpy.run_path(str(SCRIPT), run_name="__main__")
