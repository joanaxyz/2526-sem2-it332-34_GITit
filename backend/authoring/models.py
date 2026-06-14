from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

VISIBILITY_PRIVATE = "private"
VISIBILITY_PUBLIC = "public"
VISIBILITY_STORE = "store"
VISIBILITY_CHOICES = [
    (VISIBILITY_PRIVATE, "Private"),
    (VISIBILITY_PUBLIC, "Public"),
    (VISIBILITY_STORE, "Store"),
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
    TOME = "tome", "Tome"


def _default_chest_rewards() -> list[dict]:
    # Mirror curriculum.DEFAULT_CHEST_REWARDS without importing at module load.
    return [
        {"threshold": 25, "coins": 25},
        {"threshold": 50, "coins": 60},
        {"threshold": 75, "coins": 100},
        {"threshold": 100, "coins": 150},
    ]


class AuthoringStorey(models.Model):
    """A user-authored storey: a floor of their tower that GROUPS content.

    One storey holds at most one adventure but 1+ challenges and 1+ tomes, and
    carries the floor-level settings shared by all of them: reward checkpoints
    (GitCoin chests dropped along the storey's combined progress), the monster
    rosters its battles draw from, and the mastery pass-bar that unlocks the
    storey's Challenge. Content authored "into" a storey compiles to one shared
    runtime curriculum.Storey.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="authoring_storeys",
        on_delete=models.CASCADE,
    )
    slug = models.SlugField()
    title = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    chest_rewards = models.JSONField(default=_default_chest_rewards, blank=True)
    mob_roster = models.JSONField(default=list, blank=True)
    boss_roster = models.JSONField(default=list, blank=True)
    pass_bar_fraction = models.FloatField(default=0.6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["owner", "slug"], name="unique_authoring_storey_slug_per_owner"),
        ]

    def __str__(self) -> str:
        return f"AuthoringStorey({self.slug})"


class ContentDefinition(models.Model):
    kind = models.CharField(max_length=20, choices=ContentKind.choices)
    storey = models.ForeignKey(
        AuthoringStorey,
        null=True,
        blank=True,
        related_name="contents",
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
            )
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
        if self.visibility == VISIBILITY_STORE and self.status != STATUS_PUBLISHED:
            raise ValidationError({"visibility": "Store content must be published first."})
        if not isinstance(self.definition, dict):
            raise ValidationError({"definition": "Content definition must be an object."})
        if not isinstance(self.tags, list):
            raise ValidationError({"tags": "Tags must be a list."})


class PublishedContentRuntime(models.Model):
    content_definition = models.OneToOneField(
        ContentDefinition,
        related_name="runtime",
        on_delete=models.CASCADE,
    )
    storey = models.ForeignKey(
        "curriculum.Storey", null=True, blank=True, on_delete=models.SET_NULL
    )
    command_adventure = models.ForeignKey(
        "adventures.CommandAdventure", null=True, blank=True, on_delete=models.SET_NULL
    )
    challenge = models.ForeignKey(
        "challenges.Challenge", null=True, blank=True, on_delete=models.SET_NULL
    )
    tome = models.ForeignKey(
        "curriculum.Tome", null=True, blank=True, on_delete=models.SET_NULL
    )
    definition_signature = models.CharField(max_length=64)
    compiled_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["content_definition_id"]

    def __str__(self) -> str:
        return f"PublishedContentRuntime({self.content_definition_id})"
