from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value: str) -> str:
        email = get_user_model().objects.normalize_email(value).lower()
        return email

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


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    student_id = serializers.SerializerMethodField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def get_student_id(self, obj) -> str:
        profile = getattr(obj, "studentprofile", None)
        return profile.student_id if profile else ""
