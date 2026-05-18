import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

CIT_EMAIL_DOMAIN = "@cit.edu"
STUDENT_ID_PATTERN = re.compile(r"^\d{2}-\d{4}-\d{3}$")


class RegisterSerializer(serializers.Serializer):
    student_id = serializers.CharField(max_length=32)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_student_id(self, value: str) -> str:
        student_id = value.strip().upper()
        if not STUDENT_ID_PATTERN.fullmatch(student_id):
            raise serializers.ValidationError("Use the format NN-NNNN-NNN.")
        return student_id

    def validate_email(self, value: str) -> str:
        email = get_user_model().objects.normalize_email(value).lower()
        if not email.endswith(CIT_EMAIL_DOMAIN):
            raise serializers.ValidationError("Use your @cit.edu email address.")
        return email

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
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
