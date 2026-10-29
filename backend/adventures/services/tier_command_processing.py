from common.constants import (
    COMMAND_COUNTED,
    DIFFICULTY_EASY,
    RESULT_INVALID,
    RESULT_TARGET_MATCHED,
    RESULT_UNPROCESSABLE,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_FAILED,
    SESSION_STATUS_STARTED,
)
from common.exceptions import Locked
from common.git.client_command_execution import ClientCommandExecutionService
from common.git.command_outcomes import command_outcome_payload
from common.git.repository_state import VariantTargetStateHashCache
from common.runtime import (
    apply_command_accounting,
    command_budget_exhausted,
    progress_rule_counts,
    repository_response_snapshot,
    update_fields_for_execution,
)
from common.services.performance import timing
from curriculum.services import ChapterChestService
from curriculum.services.techniques import record_verified_techniques
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from practice.models import CommandStep
from practice.services.scaffolding import FeedbackGenerationService, ScaffoldingService
from practice.services.visualization import RepositoryVisualizationService
from progress.models import AdventureLevelTierCompletion
from progress.services.scored_completions import update_best_score
from simulator.services import (
    RepositorySnapshotService,
    RepositoryStateSimulator,
)
from tutoring.services.commands import (
    current_feedback,
    record_command_feedback,
    stored_feedback,
)
from tutoring.services.forms import forms_used_by
from tutoring.services.planner import PlannerReads, plan_introduction

from adventures.models import AdventureLevelTierProgress, AdventureLevelTierRun, SkillMastery
from adventures.rewards import award_tier_reward
from adventures.tier_scenarios import cleared_slugs, next_scenario, published_scenarios

from .selectors import form_solve_targets
from .skill_learning import learn_from_command
from .tier_history import TierCommandHistoryCache


class AdventureLevelTierCommandProcessingService:
    """Mirrors challenges.services.command_processing.ChallengeCommandProcessingService.

    The single behavioral divergence is completion: a ChallengeTrial needs
    one successful attempt, but an AdventureLevelTier is an ordered set of
    scenarios, each cleared by its own run. See _complete_run below - it always
    ends the run on solve (mirroring ChallengeRun: one row per attempt, never
    a long-lived looping run), but only writes AdventureLevelTierCompletion
    once AdventureLevelTierProgress holds every published scenario.
    """

    def __init__(self) -> None:
        self.state_tools = RepositoryStateSimulator()
        self.snapshotter = RepositorySnapshotService()
        self.visualizer = RepositoryVisualizationService()
        self.executor = ClientCommandExecutionService()

    # savepoint=False: the submit view already opened the transaction (to hold
    # the run-row lock), so join it directly instead of paying a nested
    # SAVEPOINT/RELEASE round trip. Standalone callers still get their own.
    @transaction.atomic(savepoint=False)
    def submit_command(self, *, run: AdventureLevelTierRun, command: str, execution: dict) -> dict:
        if run.status != SESSION_STATUS_STARTED:
            raise Locked("This adventure tier run has already ended.")

        state_tools = self.state_tools

        def span(stage: str):
            return timing(f"adventure_tier.command.{stage}", run_id=run.id)

        execution = self.executor.from_payload(
            repository_state=run.repository_state,
            command=command,
            execution=execution,
            timing_label="adventure_tier.command",
            run_id=run.id,
            expected_client_revision=run.total_attempts,
            scoring_policy_version=run.scoring_policy_version,
        )
        previous_state = execution.previous_state
        # Both tutor plans (before the command and for its response) share one
        # read of the player's history and the form catalog.
        tutor_reads = PlannerReads(run.player_id)
        previous_history = tutor_reads.history(run)
        introduction = None if run.is_transfer else plan_introduction(run, tutor_reads)
        stored_introduction_feedback = stored_feedback(run)
        previous_introduction_feedback = current_feedback(run, stored_introduction_feedback)
        next_state = execution.next_state
        command_result = execution.result
        classification, increment = execution.classification, execution.increment
        result_category = RESULT_UNPROCESSABLE
        feedback = ""
        executed_commands: list[str] = []
        state_hash = ""
        previous_rules_passing = 0
        rules_passing = 0
        total_rules = max(1, run.max_counted_commands)
        evaluator = PracticeCompletionEvaluator()
        expected_state_hash = VariantTargetStateHashCache().hash_for(
            variant=run.selected_variant,
            state_tools=state_tools,
        )
        initial_state = run.selected_variant.initial_state
        initial_evaluation = evaluator.evaluate(
            CompletionEvaluationContext(
                variant=run.selected_variant,
                required_techniques=run.required_techniques,
                verified_techniques=[],
                next_state=initial_state,
                executed_commands=[],
                next_state_hash=state_tools.state_hash(initial_state),
                expected_state_hash=expected_state_hash,
            )
        )
        previous_evaluation = evaluator.evaluate(
            CompletionEvaluationContext(
                variant=run.selected_variant,
                required_techniques=run.required_techniques,
                verified_techniques=run.verified_techniques,
                next_state=previous_state,
                executed_commands=previous_history,
                next_state_hash=state_tools.state_hash_for_normalized(previous_state),
                expected_state_hash=expected_state_hash,
                next_state_already_normalized=True,
            )
        )
        previous_rules_passing, total_rules = progress_rule_counts(
            previous_evaluation,
            initial_evaluation,
        )
        rules_passing = previous_rules_passing

        record_verified_techniques(run, execution)
        if command_result.processed:
            with span("evaluate"):
                state_hash = state_tools.state_hash_for_normalized(next_state)
                executed_commands = [*previous_history, command_result.normalized_command]
                evaluation = evaluator.evaluate(
                    CompletionEvaluationContext(
                        variant=run.selected_variant,
                        required_techniques=run.required_techniques,
                        verified_techniques=run.verified_techniques,
                        next_state=next_state,
                        executed_commands=executed_commands,
                        next_state_hash=state_hash,
                        expected_state_hash=expected_state_hash,
                        next_state_already_normalized=True,
                    )
                )
                result_category = evaluation.result_category
                rules_passing, total_rules = progress_rule_counts(
                    evaluation,
                    initial_evaluation,
                )
                if _uses_contextual_feedback(run) and classification == COMMAND_COUNTED:
                    feedback = FeedbackGenerationService().describe(previous_state, next_state)
        else:
            result_category = (
                RESULT_INVALID
                if command.strip().lower().startswith("git")
                else RESULT_UNPROCESSABLE
            )
            state_hash = state_tools.state_hash_for_normalized(next_state)

        accounting = apply_command_accounting(
            run,
            classification=classification,
            increment=increment,
            total_field="total_attempts",
            counted_field="counted_action_total",
            diagnostic_field="non_counted_diagnostic_total",
        )

        solved = result_category == RESULT_TARGET_MATCHED
        failed = command_budget_exhausted(
            solved=solved,
            classification=classification,
            counted_total=run.counted_action_total,
            max_counted_commands=run.max_counted_commands,
        )

        with span("visualization"):
            visualization_snapshot = self.visualizer.snapshot(
                next_state,
                previous_state=previous_state,
                target_state=_visible_target_state(run),
                already_normalized=True,
            )
        with span("step_create"):
            step = CommandStep.objects.create(
                adventure_tier_run=run,
                player=run.player,
                command_text=command,
                terminal_output=command_result.output,
                result_category=result_category,
                command_classification=classification,
                counted_increment=increment,
                attempt_number=run.total_attempts,
                counted_total_after=run.counted_action_total,
                state_hash=state_hash,
                expected_state_hash=expected_state_hash,
                contextual_feedback=feedback,
                visualization_snapshot=visualization_snapshot,
                normalized_command=command_result.normalized_command,
                was_processable=command_result.processed,
            )
        if command_result.processed:
            TierCommandHistoryCache().remember_after_append(
                run=run,
                previous_history=executed_commands[:-1],
                normalized_command=command_result.normalized_command,
            )
            tutor_reads.remember_history(run, executed_commands)
        else:
            # Unprocessable input is not history, but it still advances the
            # attempt count the history is keyed by.
            TierCommandHistoryCache().remember(run=run, history=previous_history)
            tutor_reads.remember_history(run, previous_history)

        if execution.state_mutated:
            run.repository_state = next_state
        update_fields = set(
            update_fields_for_execution(
                accounting.changed_fields,
                state_mutated=execution.state_mutated,
            )
        )
        # An editor may revise the variant while a learner has it open. Such a
        # run cannot claim an old validated benchmark for the changed objective.
        if run.ref_hash:
            from progress.services.references import ref_hash

            if run.current_scenario_id == run.selected_variant.scenario_id:
                run.selected_variant.scenario = run.current_scenario
            if run.ref_hash != ref_hash(run.selected_variant):
                run.ref_count, run.ref_hash = None, ""
                update_fields.update({"ref_count", "ref_hash"})
        rewards = None
        learned_skills = learn_from_command(player=run.player, result=command_result)
        if solved:
            completed_fields, rewards = self._complete_run(
                run, tutor_reads.scenario_forms(run.current_scenario)
            )
            update_fields.update(completed_fields)
        elif failed:
            run.status = SESSION_STATUS_FAILED
            run.ended_at = timezone.now()
            run.failure_reason = (
                "You ran out of counted commands before reaching the target repository state."
            )
            update_fields.update({"status", "ended_at", "failure_reason"})

        update_fields.add("verified_techniques")
        with span("run_save"):
            run.save(update_fields=sorted(update_fields))
        if run.is_transfer and (solved or failed):
            from progress.services.checkpoints import finish_transfer

            finish_transfer(run)
        introduction_feedback = record_command_feedback(
            run,
            introduction,
            execution,
            previous_introduction_feedback,
            stored=stored_introduction_feedback,
        )
        with span("response_snapshot"):
            repository_snapshot = repository_response_snapshot(
                self.snapshotter,
                command_result=command_result,
                previous_state=previous_state,
                next_state=next_state,
            )
        return {
            "run": run,
            "step": step,
            "terminal_output": command_result.output,
            "stdout": command_result.stdout,
            "stderr": command_result.stderr,
            "exit_code": command_result.exit_code,
            "command_family": command_result.command_family,
            "diagnostic_metadata": command_result.diagnostic_metadata,
            "repository_state": repository_snapshot,
            "visualization": visualization_snapshot,
            "evaluation_result": result_category,
            "command_classification": classification,
            "contextual_feedback": feedback,
            "command_outcome": command_outcome_payload(
                processed=command_result.processed,
                counted=classification == COMMAND_COUNTED,
                solved=solved,
                failed=failed,
                command_family=command_result.command_family or "default",
                previous_rules_passing=previous_rules_passing,
                rules_passing=rules_passing,
                total_rules=total_rules,
                max_counted_commands=run.max_counted_commands,
                counted_command_count=run.counted_action_total,
            ),
            "rewards": rewards,
            "learned_skills": learned_skills,
            "tutor_context": {"reads": tutor_reads, "pending": introduction_feedback},
        }

    def _complete_run(
        self, run: AdventureLevelTierRun, scenario_forms
    ) -> tuple[set[str], dict | None]:
        """Mark the run completed, clear its scenario, and complete the tier once
        every published scenario is cleared. Returns the saved field names.

        A tier is an ordered set of scenarios (see ``tier_scenarios``). A graded solve
        clears its scenario and credits the forms the learner typed. The run that
        clears the last scenario writes
        AdventureLevelTierCompletion and pays the tier's reward. Progress
        lives on AdventureLevelTierProgress because each run is one attempt;
        every solved run ends as COMPLETED, mirroring ChallengeRun."""
        from adventures.scoring import stars as compute_stars

        run.status = SESSION_STATUS_COMPLETED
        run.completed_at = timezone.now()
        run.ended_at = run.completed_at
        run.stars = (
            0
            if run.is_transfer
            else compute_stars(
                solved=True,
                counted_commands=run.counted_action_total,
                budget=run.min_counted_commands,
                retry_count=run.retry_index,
                generous_budget=run.generous_counted_commands,
                policy_version=run.scoring_policy_version,
            )
        )
        rewards = None
        if run.is_transfer:
            completion = None
        elif not run.is_replay:
            progress, _ = AdventureLevelTierProgress.objects.select_for_update().get_or_create(
                player=run.player, tier=run.tier
            )
            progress.successful_clears += 1
            scenarios = published_scenarios(run.tier)
            scenario = run.current_scenario
            if not scenario.is_published:
                # A run started before a reseed superseded its scenario still
                # counts: it clears the learner's next uncleared scenario.
                scenario = next_scenario(scenarios, progress) or scenario
            cleared = cleared_slugs(progress)
            mastery_advanced: list[dict] = []
            scenario_cleared = scenario.slug not in cleared
            if scenario_cleared:
                cleared.append(scenario.slug)
                progress.cleared_scenario_slugs = cleared
                mastery_advanced = self._credit_mastery(run, scenario_forms)
            progress.save(
                update_fields=["successful_clears", "cleared_scenario_slugs", "updated_at"]
            )
            run._prefetched_progress = progress

            completion = None
            tier_cleared = {w.slug for w in scenarios} <= set(cleared)
            if scenario_cleared and not tier_cleared:
                rewards = {
                    "first_level_clear": False,
                    "coins_awarded": 0,
                    "chapter_chests_awarded": [],
                    "mastery_advanced": mastery_advanced,
                }
            elif tier_cleared:
                completion, created = AdventureLevelTierCompletion.objects.get_or_create(
                    player=run.player,
                    tier=run.tier,
                    defaults={
                        "tier_run": run,
                        "stars": tier_stars(run=run, scenarios=scenarios, scenario=scenario),
                        "counted_action_total": run.counted_action_total,
                    },
                )
                if not created:
                    update_best_score(completion, run=run, run_field="tier_run")
                if created:
                    from progress.services.checkpoints import record_mastery

                    record_mastery(run)
                    level = run.tier.adventure_level
                    first_level_clear = run.tier.difficulty == DIFFICULTY_EASY
                    coins_awarded = award_tier_reward(player=run.player, tier=run.tier)
                    chapter_chests_awarded: list[dict] = []
                    if first_level_clear:
                        chapter_chests_awarded = ChapterChestService().award_chests(
                            player=run.player,
                            chapter=level.chapter,
                        )
                    rewards = {
                        "first_level_clear": first_level_clear,
                        "coins_awarded": coins_awarded,
                        "chapter_chests_awarded": chapter_chests_awarded,
                        "mastery_advanced": mastery_advanced,
                    }
        else:
            completion = (
                AdventureLevelTierCompletion.objects.select_for_update()
                .filter(player=run.player, tier=run.tier)
                .first()
            )
            scenarios = published_scenarios(run.tier)
            if len(scenarios) > 1 and completion is not None:
                # Several scenarios: the tier is graded by its weakest scenario, so a
                # replay raises the tier only when it lifts that minimum.
                best = tier_stars(run=run, scenarios=scenarios)
                if best > completion.stars:
                    completion.stars = best
                    completion.save(update_fields=["stars"])
            else:
                update_best_score(completion, run=run, run_field="tier_run")
        # The response reports this completion; do not read it back.
        run._prefetched_completion = completion
        run._payload_context_loaded = True
        return {"status", "completed_at", "ended_at", "stars"}, rewards

    def _credit_mastery(self, run: AdventureLevelTierRun, scenario_forms) -> list[dict]:
        """One solve for every published form the scenario's clears actually used.

        Called once per cleared scenario, with the clearing run's commands: it
        credits each form the learner typed - and nothing they did not type,
        which would otherwise suppress that form's guide later.
        ``scenario_forms`` (the scenario's published forms) only break resolver ties.
        """
        forms = forms_used_by(_processed_commands(run), preferred=scenario_forms)
        if not forms:
            return []
        targets = form_solve_targets({form.id for form in forms})
        advanced = []
        for form in forms:
            row, _ = SkillMastery.objects.get_or_create(player=run.player, command_form=form)
            row.solves += 1
            row.mastered = row.solves >= targets.get(form.id, 1)
            row.save(update_fields=["solves", "mastered", "updated_at"])
            advanced.append(
                {
                    "skill_slug": form.command_skill.slug,
                    "form_slug": form.slug,
                    "solves": row.solves,
                    "target": targets.get(form.id, 1),
                    "mastered": row.mastered,
                }
            )
        return advanced


def tier_stars(*, run: AdventureLevelTierRun, scenarios, scenario=None) -> int:
    """A tier's grade: its weakest scenario's best stars (decision D3).

    A single-scenario tier keeps today's grade - the stars of the run that
    completed it. ``run`` is the solving run, not yet saved as completed;
    ``scenario`` is the scenario it clears (its own unless that scenario was superseded).
    """
    if len(scenarios) <= 1:
        return run.stars
    best = dict(
        AdventureLevelTierRun.objects.filter(
            player=run.player,
            current_scenario__in=scenarios,
            status=SESSION_STATUS_COMPLETED,
            is_transfer=False,
        )
        .values("current_scenario_id")
        .annotate(best=Max("stars"))
        .values_list("current_scenario_id", "best")
    )
    scenario_id = scenario.id if scenario is not None else run.current_scenario_id
    best[scenario_id] = max(best.get(scenario_id, 0), run.stars)
    return min(best.get(scenario.id, 0) for scenario in scenarios)


def _processed_commands(run: AdventureLevelTierRun) -> list[str]:
    """The run's processed commands, in submission order."""
    steps = (
        CommandStep.objects.filter(adventure_tier_run=run, was_processable=True)
        .order_by("id")
        .values_list("normalized_command", "command_text")
    )
    return [normalized or text for normalized, text in steps]


def _uses_contextual_feedback(run: AdventureLevelTierRun) -> bool:
    return (
        not run.is_transfer
        and ScaffoldingService().supports_for_tier(run.tier.difficulty)["contextual_feedback"]
    )


def _visible_target_state(run: AdventureLevelTierRun) -> dict | None:
    if (
        not run.is_transfer
        and ScaffoldingService().supports_for_tier(run.tier.difficulty)["expected_state"]
    ):
        return run.selected_variant.target_state
    return None
