from django.db import models
from django.db.models import Q

from common.constants import SESSION_STATUS_ABANDONED, SESSION_STATUS_COMPLETED, SESSION_STATUS_STARTED


class LevelDrill(models.Model):
    """The seeded Squire's Drill for one adventure level.

    Drill content is seed data like every other piece of curriculum: it is
    derived once by ``manage.py seed_drills`` (which runs the composer over
    the level's command forms and authored solutions) and read back as
    rows. Deriving it per request worked, but it made the content
    invisible to the admin, impossible to override for one awkward level,
    and it paid a catalog-wide scan on every page load.
    """

    adventure_level = models.OneToOneField(
        "adventures.AdventureLevel",
        related_name="drill",
        on_delete=models.CASCADE,
    )
    # The ordering finale, when the level has a solution worth ordering.
    sequence_label = models.CharField(max_length=180, blank=True)
    sequence_task = models.TextField(blank=True)
    sequence_steps = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["adventure_level_id"]

    @property
    def has_sequence(self) -> bool:
        return bool(self.sequence_steps)

    def __str__(self) -> str:
        return f"LevelDrill(level={self.adventure_level_id})"


class LevelDrillCard(models.Model):
    """One command the drill rehearses, with its authored option pools.

    Every field here is derived from published curriculum at seed time.
    ``command_choices`` / ``intent_choices`` / ``blank.options`` hold only
    *wrong* options: the client inserts the answer and shuffles, so a
    question can never render without its correct choice.
    """

    drill = models.ForeignKey(LevelDrill, related_name="cards", on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField(default=0)
    # The catalog usage key ("git-add/patch"), stable across reseeds and the
    # identifier the client reports weak spots by.
    form_key = models.CharField(max_length=160)
    command_form = models.ForeignKey(
        "curriculum.CommandForm",
        null=True,
        blank=True,
        related_name="drill_cards",
        on_delete=models.SET_NULL,
    )
    command = models.CharField(max_length=200)
    intent = models.CharField(max_length=200)
    base_command = models.CharField(max_length=80)
    summary = models.TextField(blank=True)
    tokens = models.JSONField(default=list)
    command_choices = models.JSONField(default=list, blank=True)
    intent_choices = models.JSONField(default=list, blank=True)
    # {"index", "answer", "options"} or {} when no token is worth hiding.
    blank = models.JSONField(default=dict, blank=True)
    bank = models.JSONField(default=list)

    class Meta:
        ordering = ["drill_id", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["drill", "form_key"], name="unique_drill_card_form_key"),
        ]
        indexes = [
            models.Index(fields=["drill", "sort_order"], name="drill_card_order_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.drill_id}:{self.form_key}"


class DrillRun(models.Model):
    """One in-progress or finished pass at a level's drill.

    The drill is a queue that takes several minutes and re-asks cards the
    learner missed, so losing it to a refresh, a dead battery, or a
    misclicked back button means starting the whole ladder again - the
    precise frustration the drill exists to remove. The client's queue is
    stored verbatim (validated and bounded first) so a return lands on the
    same question with the same progress.

    One active run per (player, level); finishing it records
    ``DrillProgress`` and closes this row.
    """

    class Status(models.TextChoices):
        STARTED = SESSION_STATUS_STARTED, "Started"
        COMPLETED = SESSION_STATUS_COMPLETED, "Completed"
        ABANDONED = SESSION_STATUS_ABANDONED, "Abandoned"

    player = models.ForeignKey(
        "players.Player", on_delete=models.CASCADE, related_name="drill_runs"
    )
    adventure_level = models.ForeignKey(
        "adventures.AdventureLevel", on_delete=models.CASCADE, related_name="drill_runs"
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=SESSION_STATUS_STARTED
    )
    # The client's queue: per-card ladder position, clears, misses, and the
    # pending ask order. Opaque to the backend beyond shape validation.
    queue_state = models.JSONField(default=dict, blank=True)
    answered = models.PositiveIntegerField(default=0)
    correct = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "adventure_level"],
                condition=Q(status=SESSION_STATUS_STARTED),
                name="unique_active_drill_run",
            ),
            models.CheckConstraint(
                condition=Q(correct__lte=models.F("answered")),
                name="drill_run_correct_lte_answered",
            ),
        ]
        indexes = [
            models.Index(
                fields=["player", "adventure_level", "status"], name="drill_run_lookup_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"DrillRun({self.id}, level={self.adventure_level_id}, {self.status})"


class DrillProgress(models.Model):
    """Per-(player, adventure level) record of Squire's Drill sessions.

    The drill is optional recall practice that sits before a level's tiers.
    It pays no currency and gates nothing, so this row exists only to
    (a) mark a level as drilled on the level map and (b) remember which
    command forms the player last missed - the single readout that tells
    them what is still shaky. Nothing here feeds unlock or reward
    decisions, which is why the client is trusted to report its own
    session result.
    """

    player = models.ForeignKey(
        "players.Player",
        related_name="drill_progress",
        on_delete=models.CASCADE,
    )
    adventure_level = models.ForeignKey(
        "adventures.AdventureLevel",
        related_name="drill_progress",
        on_delete=models.CASCADE,
    )
    # Sessions started-and-reported, whether or not the queue was emptied.
    sessions = models.PositiveIntegerField(default=0)
    # Sessions where every card was mastered - topped its whole ladder.
    # A session can also end by exhausting attempts; that counts toward
    # `sessions` but is not a clear.
    clears = models.PositiveIntegerField(default=0)
    # Whole percent, first-try answers over answers given.
    best_accuracy = models.PositiveSmallIntegerField(default=0)
    last_accuracy = models.PositiveSmallIntegerField(default=0)
    # Command-form keys ("git-add/patch") missed at least once in the most
    # recent session. Validated against the seeded cards before it is
    # stored, so this is authored vocabulary rather than free text.
    shaky_form_keys = models.JSONField(default=list, blank=True)
    first_cleared_at = models.DateTimeField(null=True, blank=True)
    last_played_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "drill progress"
        constraints = [
            models.UniqueConstraint(
                fields=["player", "adventure_level"],
                name="unique_drill_progress_player_level",
            ),
            models.CheckConstraint(
                condition=Q(best_accuracy__lte=100) & Q(last_accuracy__lte=100),
                name="drill_progress_accuracy_is_percent",
            ),
            models.CheckConstraint(
                condition=Q(clears__lte=models.F("sessions")),
                name="drill_progress_clears_lte_sessions",
            ),
        ]
        indexes = [
            models.Index(fields=["player", "adventure_level"], name="drill_plyr_level_idx"),
        ]

    @property
    def is_cleared(self) -> bool:
        return self.clears > 0

    def __str__(self) -> str:
        return (
            f"DrillProgress(player={self.player_id}, level={self.adventure_level_id}, "
            f"clears={self.clears})"
        )
