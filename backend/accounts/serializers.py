import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,30}$")


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value: str) -> str:
        username = value.strip()
        if not USERNAME_PATTERN.fullmatch(username):
            raise serializers.ValidationError(
                "Username must be 3-30 characters and may only contain letters, numbers, dots, underscores, or hyphens."
            )
        return username

    def validate_first_name(self, value: str) -> str:
        return value.strip()

    def validate_last_name(self, value: str) -> str:
        return value.strip()

    def validate_email(self, value: str) -> str:
        return get_user_model().objects.normalize_email(value).lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        try:
            validate_password(attrs["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages})
        return attrs


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)

    def validate_identifier(self, value: str) -> str:
        identifier = value.strip()
        if not identifier:
            raise serializers.ValidationError("Username or email is required.")

        if "@" in identifier:
            email = serializers.EmailField().run_validation(identifier)
            return get_user_model().objects.normalize_email(email).lower()

        if not USERNAME_PATTERN.fullmatch(identifier):
            raise serializers.ValidationError("Use your username or a valid email address.")

        return identifier


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
