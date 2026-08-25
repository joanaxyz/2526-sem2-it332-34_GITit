"""Focused OpenAPI behavior shared by gameplay request views."""

from drf_spectacular.openapi import AutoSchema


class RequiredPatchBodyAutoSchema(AutoSchema):
    """Keep command-style PATCH bodies required without partializing their schema."""

    def get_operation(self, *args, **kwargs):
        operation = super().get_operation(*args, **kwargs)
        if operation is not None and self.method == "PATCH":
            request_body = operation.get("requestBody")
            if request_body is not None:
                request_body["required"] = True
        return operation
