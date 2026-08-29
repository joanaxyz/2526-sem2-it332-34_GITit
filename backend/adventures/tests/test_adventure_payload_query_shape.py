from django.db import connection
from django.test.utils import CaptureQueriesContext

from adventures.models import AdventureRun, AdventureWave, AdventureWaveVariant
from adventures.payloads import (
    _level_ref,
    _published_waves_for,
    adventure_run_payload,
)
from adventures.services import ordered_levels_for
from testing.runtime_factories import create_stage_readme_adventure_run


def _add_wave(*, fixture, slug: str, sort_order: int, published: bool = True):
    wave = AdventureWave.objects.create(
        level=fixture.level,
        slug=slug,
        title=slug.replace("-", " ").title(),
        sort_order=sort_order,
        min_counted_commands=1,
        max_counted_commands=3,
        is_published=published,
    )
    AdventureWaveVariant.objects.create(
        wave=wave,
        slug=f"{slug}-variant",
        label=f"{slug} variant",
        initial_state=fixture.states.initial,
        target_state=fixture.states.target,
        evaluation_spec={"completion_policy": {"mode": "state_hash"}},
        solution_commands=["git add README.md"],
        semantic_key=f"query-shape:{slug}",
        scenario_context={"large_unused_value": "x" * (32 * 1024)},
        is_published=published,
    )
    return wave


def test_ordered_levels_for_is_one_summary_query_without_deferred_reads(db, django_user_model):
    fixture = create_stage_readme_adventure_run(django_user_model, username="level-summary")
    _add_wave(fixture=fixture, slug="unused-sibling-wave", sort_order=1)

    with CaptureQueriesContext(connection) as queries:
        levels = ordered_levels_for(fixture.level)
        refs = [_level_ref(level) for level in levels]

    assert refs == [
        {
            "id": fixture.level.id,
            "slug": fixture.level.slug,
            "title": fixture.level.title,
            "is_required": fixture.level.is_required,
            "reward_coins": fixture.level.reward_coins,
        }
    ]
    assert len(queries.captured_queries) == 1
    sql = queries.captured_queries[0]["sql"].lower()
    assert "adventures_adventurelevel" in sql
    assert "adventures_adventurelevel_command_forms" not in sql
    assert "adventures_adventurewave" not in sql
    assert "adventures_adventurewavevariant" not in sql
    assert "source_content_definition_id" not in sql


def test_published_wave_fallback_is_one_narrow_ordered_query(db, django_user_model):
    fixture = create_stage_readme_adventure_run(django_user_model, username="wave-fallback")
    later = _add_wave(fixture=fixture, slug="later-published", sort_order=2)
    _add_wave(fixture=fixture, slug="hidden-wave", sort_order=1, published=False)

    with CaptureQueriesContext(connection) as queries:
        waves = _published_waves_for(fixture.level)

    assert [wave.id for wave in waves] == [fixture.wave.id, later.id]
    assert len(queries.captured_queries) == 1
    sql = queries.captured_queries[0]["sql"].lower()
    assert "adventures_adventurewave" in sql
    assert "adventures_adventurewavevariant" not in sql
    assert "story" not in sql
    assert "task" not in sql
    assert "objective_checks" not in sql
    assert "order by" in sql


def test_full_payload_reuses_prefetched_published_waves(db, django_user_model):
    fixture = create_stage_readme_adventure_run(django_user_model, username="wave-prefetch")
    _add_wave(fixture=fixture, slug="later-published", sort_order=2)
    _add_wave(fixture=fixture, slug="hidden-wave", sort_order=1, published=False)
    run = (
        AdventureRun.objects.select_related(
            "level",
            "level__chapter",
            "level__chapter__story",
            "level__source_content_definition",
            "current_wave",
            "selected_variant",
        )
        .prefetch_related("level__command_forms", "level__waves")
        .get(pk=fixture.run.pk)
    )

    with CaptureQueriesContext(connection) as queries:
        payload = adventure_run_payload(run, include_current_steps=False)

    assert payload["current_wave"] == 1
    assert payload["total_waves"] == 2
    assert payload["current_attempt"]["wave"] == 0
    wave_queries = [
        query["sql"]
        for query in queries.captured_queries
        if 'from "adventures_adventurewave"' in query["sql"].lower()
    ]
    assert wave_queries == []
