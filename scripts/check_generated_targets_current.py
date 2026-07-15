#!/usr/bin/env python3
"""Compatibility wrapper for scripts/checks/check_generated_targets_current.py."""
from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'checks' / 'check_generated_targets_current.py'
runpy.run_path(str(SCRIPT), run_name="__main__")
