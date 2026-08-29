from __future__ import annotations

import logging
import re
from time import perf_counter
from uuid import uuid4

from common.logging import reset_request_id, set_request_id

logger = logging.getLogger("git_it.request")
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


class RequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        supplied = request.headers.get("X-Request-ID", "").strip()
        request_id = supplied if _REQUEST_ID_PATTERN.fullmatch(supplied) else uuid4().hex
        request.request_id = request_id
        token = set_request_id(request_id)
        started = perf_counter()
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            logger.info(
                "request_completed",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                },
            )
            return response
        except Exception:
            logger.exception(
                "request_failed",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                },
            )
            raise
        finally:
            reset_request_id(token)
