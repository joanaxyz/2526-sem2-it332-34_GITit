import json
import time
from pathlib import Path

from django.conf import settings

_LOG_PATH = settings.BASE_DIR.parent / "debug-7b498f.log"
_SESSION_ID = "7b498f"


def agent_debug_log(
    *,
    location: str,
    message: str,
    data: dict | None = None,
    hypothesis_id: str = "",
    run_id: str = "pre-fix",
) -> None:
    # #region agent log
    try:
        payload = {
            "sessionId": _SESSION_ID,
            "id": f"log_{int(time.time() * 1000)}",
            "timestamp": int(time.time() * 1000),
            "location": location,
            "message": message,
            "data": data or {},
            "runId": run_id,
            "hypothesisId": hypothesis_id,
        }
        with _LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload, default=str) + "\n")
    except Exception:
        pass
    # #endregion
