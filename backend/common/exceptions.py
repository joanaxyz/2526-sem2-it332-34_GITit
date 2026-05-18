from rest_framework.exceptions import APIException


class Conflict(APIException):
    status_code = 409
    default_detail = "Conflict."
    default_code = "conflict"


class Locked(APIException):
    status_code = 423
    default_detail = "The requested resource is locked."
    default_code = "locked"
