#!/usr/bin/env python3
"""Compatibility wrapper for scripts/assets/process_monster_skill_effect_sheets.py."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'assets' / 'process_monster_skill_effect_sheets.py'
sys.path.insert(0, str(SCRIPT.parent))
runpy.run_path(str(SCRIPT), run_name="__main__")
