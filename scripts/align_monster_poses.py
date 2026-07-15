#!/usr/bin/env python3
"""Compatibility wrapper for scripts/assets/align_monster_poses.py."""
from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'assets' / 'align_monster_poses.py'
runpy.run_path(str(SCRIPT), run_name="__main__")
