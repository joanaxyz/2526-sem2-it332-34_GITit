#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))
from api_contract import generate_contract  # noqa: E402

if __name__ == "__main__":
    generate_contract()
    print("Wrote frontend/src/shared/api/generated/openapi.json and apiTypes.ts")
