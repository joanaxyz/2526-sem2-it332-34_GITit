from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime

from django.conf import settings

_request_id: ContextVar[str] = ContextVar("request_id", default="-")


def set_request_id(value: str):
    return _request_id.set(value)


def reset_request_id(token) -> None:
    _request_id.reset(token)


def get_request_id() -> str:
    return _request_id.get()


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        record.deployment_version = getattr(settings, "DEPLOYMENT_VERSION", "development")
        return True


class JsonFormatter(logging.Formatter):
    """Small dependency-free JSON formatter for container stdout logs."""

    _reserved = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime"}

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "deployment_version": getattr(record, "deployment_version", "development"),
        }
        for key, value in record.__dict__.items():
            if key in self._reserved or key.startswith("_"):
                continue
            if key in payload or key in {"args", "exc_info", "exc_text", "stack_info"}:
                continue
            if isinstance(value, (str, int, float, bool, type(None))):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)
