from django.conf import settings
from django.db import models


class LearningUnit(models.Model):
    slug = models.SlugField(unique=True)
    number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=160)
    description = models.TextField()
    is_orientation = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "number"]

    def __str__(self) -> str:
        return f"Unit {self.number}: {self.title}"


class Lesson(models.Model):
    class LessonKind(models.TextChoices):
        ORIENTATION = "orientation", "Orientation"
        CONTENT = "content", "Content"
        SCENARIO = "scenario", "Scenario-bearing"

    unit = models.ForeignKey(LearningUnit, related_name="lessons", on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    subtitle = models.CharField(max_length=240, blank=True)
    kind = models.CharField(max_length=24, choices=LessonKind.choices)
    content_html = models.TextField()
    scoped_css = models.TextField(blank=True)
    interaction_steps = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["unit__sort_order", "sort_order"]
        unique_together = [("unit", "slug")]

    def __str__(self) -> str:
        return self.title


class OrientationProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(null=True, blank=True)
    highest_step_seen = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("user", "lesson")]

    @property
    def is_complete(self) -> bool:
        return self.completed_at is not None
