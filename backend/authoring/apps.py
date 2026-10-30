from django.apps import AppConfig


<<<<<<<< HEAD:backend/authoring/apps.py
class AuthoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authoring"
========
class ChallengesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "challenges"
>>>>>>>> 6d6d1f2c82626421a9b55206e2e4ede87a07480a:backend/challenges/apps.py
