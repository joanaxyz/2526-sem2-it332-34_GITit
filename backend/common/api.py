import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views import defaults
from rest_framework.exceptions import NotFound, Throttled
from rest_framework.views import exception_handler as drf_exception_handler

SERVER_ERROR_DETAIL = "Something went wrong on our side. Please try again."
logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    if isinstance(exc, ObjectDoesNotExist):
        exc = NotFound()
    response = drf_exception_handler(exc, context)
    if response is not None and isinstance(exc, Throttled):
        # DRF rounds wait up; use the identical value for JSON and HTTP clients.
        seconds = int(exc.wait or 1)
        response["Retry-After"] = str(seconds)
        response.data["retry_after_seconds"] = seconds
        logger.info(
            "api_request_throttled",
            extra={
                "retry_after_seconds": seconds,
                "path": getattr(context.get("request"), "path", ""),
                "view": type(context.get("view")).__name__,
            },
        )
    return response


def _is_api_request(request) -> bool:
    return request.path.startswith("/api/")


def api_not_found(request, exception=None):
    """Unknown /api/ routes answer in the API's JSON shape, not Django's HTML page."""
    if _is_api_request(request):
        return JsonResponse({"detail": str(NotFound.default_detail)}, status=404)
    return defaults.page_not_found(request, exception)


def api_server_error(request):
    """Errors no API view handled still reach the client as JSON, never a stack trace."""
    if _is_api_request(request):
        return JsonResponse({"detail": SERVER_ERROR_DETAIL}, status=500)
    return defaults.server_error(request)
