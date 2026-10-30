"""Opt-in real-API profiler for gameplay command submissions.

The cold probes must run in separate pytest processes so import/URL-resolution
cost is not assigned to whichever gameplay mode happens to execute first. The
steady-state probe warms both endpoints before measuring fresh, equivalent runs.

Run from ``backend`` (PowerShell)::

    $env:COMMAND_LATENCY_SAMPLES='15'
    python -m pytest scripts/profile_command_latency.py::test_profile_adventure_cold -q -s
    python -m pytest scripts/profile_command_latency.py::test_profile_challenge_cold -q -s
    python -m pytest scripts/profile_command_latency.py::test_profile_steady_state -q -s

Set ``COMMAND_LATENCY_REVERSE_LANES=true`` to reverse the warm-lane order while
keeping the same explicit warm-up. This file is intentionally outside the normal
test suite: wall-time evidence is machine-local and should never be a CI gate.
"""

from __future__ import annotations

import gc
import hashlib
import json
import math
import os
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierProgress,
    AdventureLevelTierRun,
    AdventureLevelTierScenario,
    AdventureLevelTierScenarioVariant,
)
from challenges.models import ChallengeLevel, ChallengeRun, ChallengeTrial, ChallengeTrialVariant
from common.constants import DIFFICULTY_EASY, SESSION_STATUS_COMPLETED, SESSION_STATUS_STARTED
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from testing.frontend_execution import frontend_execution_payload
from testing.runtime_factories import api_client_for, make_user, stage_readme_states

COMMAND = "git add README.md"
DIAGNOSTIC_COMMAND = "git status"
DEFAULT_SAMPLE_COUNT = 15
STRESS_LEVELS = 10
STRESS_SCENARIOS_PER_LEVEL = 4
STRESS_VARIANTS_PER_SCENARIO = 3
STRESS_VARIANT_BYTES = 16 * 1024


@dataclass(frozen=True)
class BenchmarkCatalog:
    adventure_tier: AdventureLevelTier
    first_scenario: AdventureLevelTierScenario
    final_scenario: AdventureLevelTierScenario
    first_variant: AdventureLevelTierScenarioVariant
    final_variant: AdventureLevelTierScenarioVariant
    challenge_trial: ChallengeTrial
    challenge_variant: ChallengeTrialVariant


@dataclass(frozen=True)
class PreparedRequest:
    client: object
    url: str
    body: dict
    precondition_fingerprint: str
    validate: Callable[[object], None]


@dataclass(frozen=True)
class LatencySample:
    elapsed_ms: float
    query_count: int
    response_bytes: int
    precondition_fingerprint: str


def _sample_count() -> int:
    raw = os.environ.get("COMMAND_LATENCY_SAMPLES", str(DEFAULT_SAMPLE_COUNT))
    try:
        count = int(raw)
    except ValueError:
        pytest.fail("COMMAND_LATENCY_SAMPLES must be an integer")
    if count < 3:
        pytest.fail("COMMAND_LATENCY_SAMPLES must be at least 3")
    return count


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _percentile(values: list[float | int], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * fraction) - 1)
    return float(ordered[index])


def _fingerprint(*, lane: str, state: dict, revision: int, variant_key: str) -> str:
    payload = json.dumps(
        {
            "lane": lane,
            "repository_state": state,
            "revision": revision,
            "variant_key": variant_key,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _result_payload(lane: str, samples: list[LatencySample], *, cold: bool) -> dict:
    elapsed = [sample.elapsed_ms for sample in samples]
    queries = [sample.query_count for sample in samples]
    response_bytes = [sample.response_bytes for sample in samples]
    fingerprints = {sample.precondition_fingerprint for sample in samples}
    assert len(fingerprints) == 1, f"{lane} samples did not start from equivalent state"
    return {
        "lane": lane,
        "cold": cold,
        "samples": len(samples),
        "request_ms": {
            "p50": round(statistics.median(elapsed), 2),
            "p95": round(_percentile(elapsed, 0.95), 2),
            "max": round(max(elapsed), 2),
        },
        "queries": {
            "p50": round(statistics.median(queries), 2),
            "p95": round(_percentile(queries, 0.95), 2),
            "max": max(queries),
        },
        "response_bytes": {
            "p50": round(statistics.median(response_bytes), 2),
            "p95": round(_percentile(response_bytes, 0.95), 2),
            "max": max(response_bytes),
        },
        "precondition_fingerprint": next(iter(fingerprints)),
    }


def _emit(result: dict) -> None:
    print(f"COMMAND_LATENCY_RESULT {json.dumps(result, sort_keys=True)}")


def _timed_post(prepared: PreparedRequest) -> LatencySample:
    # Fixture/catalog construction intentionally happens outside the timed
    # boundary and can leave a large generation ready for collection. Collect it
    # now so a harness-created pause is not attributed to one arbitrary request;
    # allocations made by the request itself remain part of the measurement.
    gc.collect()
    with CaptureQueriesContext(connection) as queries:
        started = time.perf_counter()
        response = prepared.client.post(prepared.url, prepared.body, format="json")
        elapsed_ms = (time.perf_counter() - started) * 1_000
    assert response.status_code == 200, response.content
    prepared.validate(response)
    return LatencySample(
        elapsed_ms=elapsed_ms,
        query_count=len(queries.captured_queries),
        response_bytes=len(response.content),
        precondition_fingerprint=prepared.precondition_fingerprint,
    )


def _measure_lane(
    lane: str,
    prepare: Callable[[], PreparedRequest],
    *,
    samples: int,
) -> dict:
    measured = [_timed_post(prepare()) for _ in range(samples)]
    return _result_payload(lane, measured, cold=False)


def _build_catalog() -> BenchmarkCatalog:
    suffix = uuid4().hex[:10]
    story = Story.objects.create(
        slug=f"latency-story-{suffix}",
        title="Command latency benchmark",
        sort_order=990_000,
    )
    chapter = Chapter.objects.create(
        story=story,
        slug=f"latency-chapter-{suffix}",
        number=990_000,
        sort_order=990_000,
        title="Command latency benchmark",
        description="Disposable profiler data",
    )
    states = stage_readme_states()

    adventure_level = AdventureLevel.objects.create(
        chapter=chapter,
        slug="measured-adventure",
        title="Measured Adventure",
        sort_order=0,
        is_required=True,
        is_published=True,
    )
    adventure_tier = AdventureLevelTier.objects.create(
        adventure_level=adventure_level,
        difficulty=DIFFICULTY_EASY,
        is_published=True,
    )
    first_scenario = AdventureLevelTierScenario.objects.create(
        tier=adventure_tier,
        slug="measured-first",
        title="Measured first scenario",
        sort_order=0,
        min_counted_commands=1,
        max_counted_commands=3,
    )
    final_scenario = AdventureLevelTierScenario.objects.create(
        tier=adventure_tier,
        slug="measured-final",
        title="Measured final scenario",
        sort_order=1,
        min_counted_commands=1,
        max_counted_commands=3,
    )
    first_variant = _create_adventure_variant(
        scenario=first_scenario,
        slug="measured-first",
        semantic_key="latency:first",
        initial_state=states.initial,
        target_state=states.target,
    )
    final_variant = _create_adventure_variant(
        scenario=final_scenario,
        slug="measured-final",
        semantic_key="latency:final",
        initial_state=states.initial,
        target_state=states.target,
    )

    _create_adventure_payload_stress(
        chapter=chapter,
        initial_state=states.initial,
        target_state=states.target,
        suffix=suffix,
    )

    challenge_level = ChallengeLevel.objects.create(
        chapter=chapter,
        slug="measured-challenge",
        title="Measured Challenge",
        sort_order=0,
        is_published=True,
    )
    challenge_trial = ChallengeTrial.objects.create(
        challenge_level=challenge_level,
        difficulty=DIFFICULTY_EASY,
        min_counted_commands=1,
        max_counted_commands=3,
        is_published=True,
    )
    challenge_variant = ChallengeTrialVariant.objects.create(
        trial=challenge_trial,
        slug="measured-challenge",
        label="Measured challenge",
        initial_state=states.initial,
        target_state=states.target,
        evaluation_spec={"completion_policy": {"mode": "state_hash"}},
        solution_commands=[COMMAND],
        semantic_key="latency:challenge",
        is_published=True,
    )
    return BenchmarkCatalog(
        adventure_tier=adventure_tier,
        first_scenario=first_scenario,
        final_scenario=final_scenario,
        first_variant=first_variant,
        final_variant=final_variant,
        challenge_trial=challenge_trial,
        challenge_variant=challenge_variant,
    )


def _create_adventure_variant(
    *,
    scenario: AdventureLevelTierScenario,
    slug: str,
    semantic_key: str,
    initial_state: dict,
    target_state: dict,
) -> AdventureLevelTierScenarioVariant:
    return AdventureLevelTierScenarioVariant.objects.create(
        scenario=scenario,
        slug=slug,
        label=slug.replace("-", " ").title(),
        initial_state=initial_state,
        target_state=target_state,
        evaluation_spec={"completion_policy": {"mode": "state_hash"}},
        solution_commands=[COMMAND],
        semantic_key=semantic_key,
        is_published=True,
    )


def _create_adventure_payload_stress(
    *,
    chapter: Chapter,
    initial_state: dict,
    target_state: dict,
    suffix: str,
) -> None:
    """Create sibling payload data that the displaced broad prefetch hydrates."""

    levels = AdventureLevel.objects.bulk_create(
        [
            AdventureLevel(
                chapter=chapter,
                slug=f"stress-level-{index}",
                title=f"Stress level {index}",
                sort_order=index + 1,
                is_required=True,
                is_published=True,
            )
            for index in range(STRESS_LEVELS)
        ]
    )
    tiers = AdventureLevelTier.objects.bulk_create(
        [AdventureLevelTier(adventure_level=level, difficulty=DIFFICULTY_EASY) for level in levels]
    )
    scenarios = AdventureLevelTierScenario.objects.bulk_create(
        [
            AdventureLevelTierScenario(
                tier=tier,
                slug=f"stress-scenario-{scenario_index}",
                title=f"Stress scenario {scenario_index}",
                sort_order=scenario_index,
                min_counted_commands=1,
                max_counted_commands=3,
                is_published=True,
            )
            for tier in tiers
            for scenario_index in range(STRESS_SCENARIOS_PER_LEVEL)
        ]
    )
    padding = "x" * STRESS_VARIANT_BYTES
    AdventureLevelTierScenarioVariant.objects.bulk_create(
        [
            AdventureLevelTierScenarioVariant(
                scenario=scenario,
                slug=f"stress-variant-{variant_index}",
                label=f"Stress variant {variant_index}",
                initial_state=initial_state,
                target_state=target_state,
                evaluation_spec={"completion_policy": {"mode": "state_hash"}},
                solution_commands=[COMMAND],
                semantic_key=f"latency:stress:{suffix}:{scenario.id}:{variant_index}",
                scenario_context={"benchmark_padding": padding},
                is_published=True,
            )
            for scenario in scenarios
            for variant_index in range(STRESS_VARIANTS_PER_SCENARIO)
        ],
        batch_size=100,
    )


def _prepare_adventure(
    django_user_model,
    catalog: BenchmarkCatalog,
    *,
    lane: str,
    final_scenario: bool,
    diagnostic: bool,
) -> PreparedRequest:
    user = make_user(django_user_model, username=f"latency-{lane}")
    player = get_or_create_player(user)
    scenario = catalog.final_scenario if final_scenario else catalog.first_scenario
    variant = catalog.final_variant if final_scenario else catalog.first_variant
    if final_scenario:
        # The final scenario completes the tier only once the first is cleared.
        AdventureLevelTierProgress.objects.create(
            player=player,
            tier=catalog.adventure_tier,
            successful_clears=1,
            cleared_scenario_slugs=[catalog.first_scenario.slug],
        )
    run = AdventureLevelTierRun.objects.create(
        player=player,
        tier=catalog.adventure_tier,
        current_scenario=scenario,
        selected_variant=variant,
        source_entry_point="latency_profiler",
        min_counted_commands=scenario.min_counted_commands,
        max_counted_commands=scenario.max_counted_commands,
        repository_state=variant.initial_state,
    )
    assert run.total_attempts == 0
    assert run.counted_action_total == 0

    command = DIAGNOSTIC_COMMAND if diagnostic else COMMAND
    next_state = variant.initial_state if diagnostic else variant.target_state
    execution = frontend_execution_payload(
        command,
        next_state,
        diagnostic=diagnostic,
        output="On branch main" if diagnostic else "",
        command_family="status" if diagnostic else "add",
        diagnostic_metadata=["inspected_status"] if diagnostic else [],
        client_run_revision=0,
    )

    def validate(response) -> None:
        payload = response.json()
        run.refresh_from_db()
        if diagnostic:
            assert run.status == SESSION_STATUS_STARTED
            assert payload["run"]["status"] == SESSION_STATUS_STARTED
        elif final_scenario:
            assert run.status == SESSION_STATUS_COMPLETED
            assert payload["run"]["status"] == SESSION_STATUS_COMPLETED
            assert payload["run"]["completion"] is not None
        else:
            # Clearing the first scenario ends this run; the tier stays open.
            assert run.status == SESSION_STATUS_COMPLETED
            assert payload["run"]["completion"] is None
            assert payload["run"]["progress"]["completed"] == 1

    return PreparedRequest(
        client=api_client_for(user),
        url=f"/api/adventure-tier-runs/{run.id}/submit-command/",
        body={"command": command, "execution": execution},
        precondition_fingerprint=_fingerprint(
            lane=lane,
            state=run.repository_state,
            revision=run.total_attempts,
            variant_key=variant.semantic_key,
        ),
        validate=validate,
    )


def _prepare_challenge(
    django_user_model,
    catalog: BenchmarkCatalog,
    *,
    lane: str,
    diagnostic: bool,
) -> PreparedRequest:
    user = make_user(django_user_model, username=f"latency-{lane}")
    player = get_or_create_player(user)
    variant = catalog.challenge_variant
    run = ChallengeRun.objects.create(
        player=player,
        challenge_trial=catalog.challenge_trial,
        selected_variant=variant,
        source_entry_point="latency_profiler",
        min_counted_commands=catalog.challenge_trial.min_counted_commands,
        max_counted_commands=catalog.challenge_trial.max_counted_commands,
        repository_state=variant.initial_state,
    )
    assert run.total_attempts == 0
    assert run.counted_action_total == 0

    command = DIAGNOSTIC_COMMAND if diagnostic else COMMAND
    next_state = variant.initial_state if diagnostic else variant.target_state
    execution = frontend_execution_payload(
        command,
        next_state,
        diagnostic=diagnostic,
        output="On branch main" if diagnostic else "",
        command_family="status" if diagnostic else "add",
        diagnostic_metadata=["inspected_status"] if diagnostic else [],
        client_run_revision=0,
    )

    def validate(response) -> None:
        payload = response.json()
        run.refresh_from_db()
        expected = SESSION_STATUS_STARTED if diagnostic else SESSION_STATUS_COMPLETED
        assert run.status == expected
        assert payload["run"]["status"] == expected

    return PreparedRequest(
        client=api_client_for(user),
        url=f"/api/challenge-runs/{run.id}/submit-command/",
        body={"command": command, "execution": execution},
        precondition_fingerprint=_fingerprint(
            lane=lane,
            state=run.repository_state,
            revision=run.total_attempts,
            variant_key=variant.semantic_key,
        ),
        validate=validate,
    )


@pytest.mark.django_db
def test_profile_adventure_cold(django_user_model):
    catalog = _build_catalog()
    prepared = _prepare_adventure(
        django_user_model,
        catalog,
        lane="adventure_completion",
        final_scenario=True,
        diagnostic=False,
    )
    _emit(_result_payload("adventure_cold_completion", [_timed_post(prepared)], cold=True))


@pytest.mark.django_db
def test_profile_challenge_cold(django_user_model):
    catalog = _build_catalog()
    prepared = _prepare_challenge(
        django_user_model,
        catalog,
        lane="challenge_completion",
        diagnostic=False,
    )
    _emit(_result_payload("challenge_cold_completion", [_timed_post(prepared)], cold=True))


@pytest.mark.django_db
def test_profile_steady_state(django_user_model):
    catalog = _build_catalog()

    # Warm URL resolution, serializers, evaluator/spec caches, and both endpoint
    # stacks. These requests are intentionally excluded from all reported lanes.
    _timed_post(
        _prepare_adventure(
            django_user_model,
            catalog,
            lane="adventure_warmup",
            final_scenario=True,
            diagnostic=False,
        )
    )
    _timed_post(
        _prepare_challenge(
            django_user_model,
            catalog,
            lane="challenge_warmup",
            diagnostic=False,
        )
    )

    count = _sample_count()
    lanes: list[tuple[str, Callable[[], PreparedRequest]]] = [
        (
            "adventure_diagnostic",
            lambda: _prepare_adventure(
                django_user_model,
                catalog,
                lane="adventure_diagnostic",
                final_scenario=False,
                diagnostic=True,
            ),
        ),
        (
            "adventure_scenario_clear",
            lambda: _prepare_adventure(
                django_user_model,
                catalog,
                lane="adventure_scenario_clear",
                final_scenario=False,
                diagnostic=False,
            ),
        ),
        (
            "adventure_completion",
            lambda: _prepare_adventure(
                django_user_model,
                catalog,
                lane="adventure_completion",
                final_scenario=True,
                diagnostic=False,
            ),
        ),
        (
            "challenge_diagnostic",
            lambda: _prepare_challenge(
                django_user_model,
                catalog,
                lane="challenge_diagnostic",
                diagnostic=True,
            ),
        ),
        (
            "challenge_completion",
            lambda: _prepare_challenge(
                django_user_model,
                catalog,
                lane="challenge_completion",
                diagnostic=False,
            ),
        ),
    ]
    if _truthy_env("COMMAND_LATENCY_REVERSE_LANES"):
        lanes.reverse()

    for lane, prepare in lanes:
        _emit(_measure_lane(lane, prepare, samples=count))
