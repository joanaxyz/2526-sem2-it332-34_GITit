from django.db import models

# Default GitCoin chests along the storey progress bar. Seeds may override
# per storey via the module spec's "chest_rewards".
DEFAULT_CHEST_REWARDS = [
    {"threshold": 25, "coins": 25},
    {"threshold": 50, "coins": 60},
    {"threshold": 75, "coins": 100},
    {"threshold": 100, "coins": 150},
]


def default_chest_rewards() -> list[dict]:
    return [dict(chest) for chest in DEFAULT_CHEST_REWARDS]


class Storey(models.Model):
    slug = models.SlugField(unique=True)
    number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=160)
    description = models.TextField()
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    # [{"threshold": <progress percent>, "coins": <GitCoins>}, ...]
    chest_rewards = models.JSONField(default=default_chest_rewards, blank=True)

    class Meta:
        ordering = ["sort_order", "number"]

    def __str__(self) -> str:
        return f"Storey {self.number}: {self.title}"


class ConceptPage(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True)
    cards = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self) -> str:
        return self.title


class CommandSkill(models.Model):
    storey = models.ForeignKey(
        Storey,
        related_name="command_skills",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    base_command = models.CharField(max_length=80)
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    mental_model = models.JSONField(default=dict, blank=True)
    command_preview = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["storey__sort_order", "sort_order", "base_command"]
        unique_together = [("storey", "slug")]

    def __str__(self) -> str:
        return self.title


class CommandForm(models.Model):
    command_skill = models.ForeignKey(CommandSkill, related_name="command_forms", on_delete=models.CASCADE)
    slug = models.SlugField()
    usage_form = models.CharField(max_length=140)
    label = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    command_preview = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["command_skill__sort_order", "sort_order", "usage_form"]
        unique_together = [("command_skill", "slug")]

    def __str__(self) -> str:
        return self.label
