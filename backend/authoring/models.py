from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

VISIBILITY_PRIVATE = "private"
VISIBILITY_PUBLIC = "public"
VISIBILITY_CHOICES = [
    (VISIBILITY_PRIVATE, "Private"),
    (VISIBILITY_PUBLIC, "Public"),
]

STATUS_DRAFT = "draft"
STATUS_TESTABLE = "testable"
STATUS_PUBLISHED = "published"
STATUS_ARCHIVED = "archived"
CONTENT_STATUSES = [
    (STATUS_DRAFT, "Draft"),
    (STATUS_TESTABLE, "Testable"),
    (STATUS_PUBLISHED, "Published"),
    (STATUS_ARCHIVED, "Archived"),
]


class ContentKind(models.TextChoices):
    ADVENTURE = "adventure", "Adventure"
    CHALLENGE = "challenge", "Challenge"
    LESSON = "lesson", "ChapterLesson"


class AuthoringChapter(models.Model):
    """A user-authored chapter that groups related content.

    One chapter can hold one adventure, one challenge, and 1+ lessons, and
    carries the floor-level settings shared by all of them. Content authored
    "into" a chapter compiles to one shared runtime curriculum.Chapter.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="authoring_chapters",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "slug"], name="unique_authoring_chapter_slug_per_owner"
            ),
        ]

    def __str__(self) -> str:
        return f"AuthoringChapter({self.slug})"


class ContentDefinition(models.Model):
    kind = models.CharField(max_length=20, choices=ContentKind.choices)
    chapter = models.ForeignKey(
        AuthoringChapter,
        null=True,
        blank=True,
        related_name="contents",
        on_delete=models.SET_NULL,
    )
    official_chapter = models.ForeignKey(
        "curriculum.Chapter",
        null=True,
        blank=True,
        related_name="official_content_definitions",
        on_delete=models.SET_NULL,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="content_definitions",
        on_delete=models.CASCADE,
    )
    source_definition = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="remixes",
        on_delete=models.SET_NULL,
    )
    visibility = models.CharField(
        max_length=10, choices=VISIBILITY_CHOICES, default=VISIBILITY_PRIVATE
    )
    status = models.CharField(max_length=16, choices=CONTENT_STATUSES, default=STATUS_DRAFT)
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    command_family = models.CharField(max_length=80, blank=True)
    difficulty = models.CharField(max_length=12, blank=True)
    definition = models.JSONField(default=dict, blank=True)
    validation_errors = models.JSONField(default=list, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kind", "title", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "kind", "slug"],
                name="unique_content_slug_per_owner_kind",
            ),
            models.UniqueConstraint(
                fields=["kind", "slug"],
                condition=models.Q(owner__isnull=True),
                name="unique_system_content_slug_per_kind",
            ),
            models.CheckConstraint(
                condition=models.Q(visibility__in=[VISIBILITY_PRIVATE, VISIBILITY_PUBLIC]),
                name="authoring_content_valid_visibility",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(chapter__isnull=True)
                    | models.Q(official_chapter__isnull=True)
                ),
                name="authoring_content_one_chapter_type",
            ),
        ]
        indexes = [
            models.Index(fields=["owner", "kind", "status"], name="auth_content_owner_idx"),
            models.Index(fields=["visibility", "status"], name="auth_content_vis_idx"),
        ]

    def __str__(self) -> str:
        return f"ContentDefinition({self.kind}:{self.slug})"

    @property
    def is_published(self) -> bool:
        return self.status == STATUS_PUBLISHED

    def clean(self) -> None:
        super().clean()
        if not isinstance(self.definition, dict):
            raise ValidationError({"definition": "Content definition must be an object."})
        if not isinstance(self.tags, list):
            raise ValidationError({"tags": "Tags must be a list."})
        if self.chapter_id and self.official_chapter_id:
            raise ValidationError(
                {"official_chapter": "Choose an authored chapter or an official chapter, not both."}
            )


class PublishedContentRuntime(models.Model):
    content_definition = models.OneToOneField(
        ContentDefinition,
        related_name="runtime",
        on_delete=models.CASCADE,
    )
    chapter = models.ForeignKey(
        "curriculum.Chapter", null=True, blank=True, on_delete=models.SET_NULL
    )
    adventure = models.ForeignKey(
        "adventures.AdventureLevel", null=True, blank=True, on_delete=models.SET_NULL
    )
    challenge = models.ForeignKey(
        "challenges.ChallengeLevel", null=True, blank=True, on_delete=models.SET_NULL
    )
    lesson = models.ForeignKey(
        "curriculum.ChapterLesson", null=True, blank=True, on_delete=models.SET_NULL
    )
    definition_signature = models.CharField(max_length=64)
    compiled_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["content_definition_id"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    (
                        models.Q(adventure__isnull=False)
                        & models.Q(challenge__isnull=True)
                        & models.Q(lesson__isnull=True)
                    )
                    | (
                        models.Q(adventure__isnull=True)
                        & models.Q(challenge__isnull=False)
                        & models.Q(lesson__isnull=True)
                    )
                    | (
                        models.Q(adventure__isnull=True)
                        & models.Q(challenge__isnull=True)
                        & models.Q(lesson__isnull=False)
                    )
                ),
                name="published_runtime_exactly_one_target",
            ),
        ]

    def __str__(self) -> str:
        return f"PublishedContentRuntime({self.content_definition_id})"
