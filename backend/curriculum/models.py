from django.db import models


class Story(models.Model):
    """A purchasable curriculum world containing an ordered chapter sequence."""

    DIFFICULTY_BEGINNER = "beginner"
    DIFFICULTY_INTERMEDIATE = "intermediate"
    DIFFICULTY_ADVANCED = "advanced"
    DIFFICULTY_CHOICES = (
        (DIFFICULTY_BEGINNER, "Beginner"),
        (DIFFICULTY_INTERMEDIATE, "Intermediate"),
        (DIFFICULTY_ADVANCED, "Advanced"),
    )

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    narrative_brief = models.JSONField(default=dict, blank=True)
    price = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    world_slug = models.SlugField(max_length=64, default="arcane-spire")
    difficulty = models.CharField(
        max_length=16,
        choices=DIFFICULTY_CHOICES,
        default=DIFFICULTY_BEGINNER,
    )
    prerequisite_story = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="unlocks_stories",
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return self.title


class Chapter(models.Model):
    story = models.ForeignKey(
        Story,
        null=True,
        blank=True,
        related_name="chapters",
        on_delete=models.PROTECT,
    )
    slug = models.SlugField(unique=True)
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=160)
    description = models.TextField()
    narrative_brief = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)
    # A reference chapter has the same detailed book content as a playable
    # chapter but does not claim to have simulator levels before its command
    # families are implemented and verified end-to-end.
    is_playable = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    # Authored battle-stage dressing rendered behind the actors during this
    # chapter's battles. Shape: {"parallax": "<asset-slug>"|null,
    # "landing": {"x", "y", "width", "height"}|null}. Coordinates are
    # normalized (0..1) so they render at any stage size.
    battle_stage = models.JSONField(default=dict, blank=True)
    class Meta:
        ordering = ["sort_order", "number"]
        indexes = [
            models.Index(fields=["story", "sort_order"], name="chapter_story_sort_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["story", "number"], name="unique_chapter_story_number"),
        ]

    def __str__(self) -> str:
        return f"{self.story.title if self.story_id else 'Story'} · Chapter {self.number}: {self.title}"


class ChapterLesson(models.Model):
    """A reading lesson attached directly to a chapter.

    Lessons are pure reference content: no runs, no attempts, and no locks.
    The chapter book renders them in ``sort_order``.
    """

    chapter = models.ForeignKey(Chapter, related_name="lessons", on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    # list[BookPage] - the same page/block schema the Chapter Book renders.
    pages = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    source_content_definition = models.ForeignKey(
        "authoring.ContentDefinition",
        null=True,
        blank=True,
        related_name="runtime_lessons",
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["chapter__sort_order", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["chapter", "slug"], name="unique_lesson_chapter_slug"),
        ]

    def __str__(self) -> str:
        return self.title


class LibraryEntry(models.Model):
    """Authored reference content for one command, keyed by its canonical
    library key (``library_key_for_command``). The Chapter Book resolves each
    registered CommandSkill to its entry here; commands without an entry fall
    back to a synthesized summary page."""

    command_key = models.CharField(max_length=80, unique=True)
    title = models.CharField(max_length=160, blank=True)
    summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    # list[BookPage] - the same page/block schema the Chapter Book renders.
    pages = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["command_key"]
        verbose_name_plural = "library entries"

    def __str__(self) -> str:
        return self.command_key


class CommandSkill(models.Model):
    """A git command as a global library/spellbook entry (e.g. "git add").

    Chapter-agnostic: each of its CommandForms carries its own chapter, so a single
    command can introduce basic moves in one chapter and advanced moves in a later
    one without duplicating the library entry. The skill owns the reference content
    (title, summary, mental model); the chapters it touches are derived from its
    forms.
    """

    slug = models.SlugField(unique=True)
    base_command = models.CharField(max_length=80)
    title = models.CharField(max_length=160)
    summary = models.TextField(blank=True)
    mental_model = models.JSONField(default=dict, blank=True)
    command_preview = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "base_command"]

    def __str__(self) -> str:
        return self.title


class CommandForm(models.Model):
    command_skill = models.ForeignKey(CommandSkill, related_name="command_forms", on_delete=models.CASCADE)
    # The chapter where this specific move is taught. The skill spans whatever
    # chapters its forms live in (derived), so the library entry is never duplicated.
    chapter = models.ForeignKey(
        Chapter, related_name="command_forms", on_delete=models.CASCADE, null=True
    )
    slug = models.SlugField()
    usage_form = models.CharField(max_length=140)
    label = models.CharField(max_length=180)
    summary = models.TextField(blank=True)
    command_preview = models.JSONField(default=dict, blank=True)
    is_published = models.BooleanField(default=True)
    # Reference-only forms are fully authored for the chapter book but are not
    # offered by playable levels until the deterministic simulator and backend
    # transition verifier support them. This prevents curriculum scope from
    # being silently reduced to today's engine capabilities.
    is_playable = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["command_skill__sort_order", "sort_order", "usage_form"]
        constraints = [
            models.UniqueConstraint(fields=["command_skill", "slug"], name="unique_command_form_skill_slug"),
        ]

    def __str__(self) -> str:
        return self.label
