from django.db import models


class Storey(models.Model):
    slug = models.SlugField(unique=True)
    number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=160)
    description = models.TextField()
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

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
    module = models.ForeignKey(
        Storey,
        related_name="command_topics",
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
        ordering = ["module__sort_order", "sort_order", "base_command"]
        unique_together = [("module", "slug")]

    def __str__(self) -> str:
        return self.title


class CommandForm(models.Model):
    topic = models.ForeignKey(CommandSkill, related_name="usages", on_delete=models.CASCADE)
    slug = models.SlugField()
    usage_form = models.CharField(max_length=140)
    label = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    command_preview = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["topic__sort_order", "sort_order", "usage_form"]
        unique_together = [("topic", "slug")]

    def __str__(self) -> str:
        return self.label
