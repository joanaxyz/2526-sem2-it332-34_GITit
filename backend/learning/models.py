from django.db import models


class LearningModule(models.Model):
    slug = models.SlugField(unique=True)
    number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=160)
    description = models.TextField()
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "number"]

    def __str__(self) -> str:
        return f"Module {self.number}: {self.title}"


class FoundationTopic(models.Model):
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
