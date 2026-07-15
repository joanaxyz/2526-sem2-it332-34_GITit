#!/usr/bin/env python3
"""Compatibility wrapper for scripts/checks/check_css_architecture.py."""
from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'checks' / 'check_css_architecture.py'
runpy.run_path(str(SCRIPT), run_name="__main__")
