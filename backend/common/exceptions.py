from rest_framework.exceptions import APIException


class BadRequest(APIException):
    status_code = 400
    default_detail = "Bad request."
    default_code = "bad_request"


class Conflict(APIException):
    status_code = 409
    default_detail = "Conflict."
    default_code = "conflict"


class Locked(APIException):
    status_code = 423
    default_detail = "The requested resource is locked."
    default_code = "locked"


class PayloadTooLarge(APIException):
    status_code = 413
    default_detail = "The resulting repository state is too large."
    default_code = "payload_too_large"
