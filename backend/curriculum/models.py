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
    # Monster palette for this storey's battles: adventure encounters cycle
    # `mob_roster`, challenge bosses cycle `boss_roster`. Each level still picks
    # its species deterministically (stable hash of the level slug) from the
    # list. Empty falls back to the global cycles in battle/constants.py.
    mob_roster = models.JSONField(default=list, blank=True)
    boss_roster = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["sort_order", "number"]

    def __str__(self) -> str:
        return f"Storey {self.number}: {self.title}"


# Tower slots a tome can be authored into. The tower renders sections in a
# fixed designed sequence, so placement is a named insertion point, not a
# free ordinal.
TOME_PLACEMENT_ABOVE_ADVENTURE = "above_adventure"
TOME_PLACEMENT_BELOW_ADVENTURE = "below_adventure"
TOME_PLACEMENT_BELOW_CHALLENGES = "below_challenges"
TOME_PLACEMENTS = [
    (TOME_PLACEMENT_ABOVE_ADVENTURE, "Above the adventure"),
    (TOME_PLACEMENT_BELOW_ADVENTURE, "Below the adventure"),
    (TOME_PLACEMENT_BELOW_CHALLENGES, "Below the challenges"),
]


class Tome(models.Model):
    """A general lesson (not a command) that opens as a book in the tower.

    Tomes appear only on storeys where they are authored, at the authored
    placement slot. They are pure reading - no runs, attempts, or locking."""

    storey = models.ForeignKey(Storey, related_name="tomes", on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    # list[BookPage] - the same page/block schema the Storey Book renders.
    pages = models.JSONField(default=list, blank=True)
    placement = models.CharField(
        max_length=32, choices=TOME_PLACEMENTS, default=TOME_PLACEMENT_ABOVE_ADVENTURE
    )
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    source_content_definition = models.ForeignKey(
        "authoring.ContentDefinition",
        null=True,
        blank=True,
        related_name="runtime_tomes",
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["storey__sort_order", "sort_order", "id"]
        unique_together = [("storey", "slug")]

    def __str__(self) -> str:
        return self.title


class LibraryEntry(models.Model):
    """Authored reference content for one command, keyed by its canonical
    library key (``library_key_for_command``). The Storey Book resolves each
    registered CommandSkill to its entry here; commands without an entry fall
    back to a synthesized summary page."""

    command_key = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=160, blank=True)
    summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    # list[BookPage] - the same page/block schema the Storey Book renders.
    pages = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["command_key"]
        verbose_name_plural = "library entries"

    def __str__(self) -> str:
        return self.command_key


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
