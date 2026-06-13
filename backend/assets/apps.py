from django.apps import AppConfig


class AssetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "assets"

    def ready(self) -> None:
        # Wire the cache-invalidation signals for the descriptor map.
        from assets import signals  # noqa: F401
