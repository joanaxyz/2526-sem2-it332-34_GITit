from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from rest_framework.views import exception_handler as drf_exception_handler


def api_exception_handler(exc, context):
    if isinstance(exc, ObjectDoesNotExist):
        exc = NotFound()
    return drf_exception_handler(exc, context)
