"""Project-wide pytest fixtures that keep each test hermetic.

The suite runs in one process and several tests seed official data (via
``seed_curriculum`` / ``seed_all``). Shared side effects leaked between tests
and made the suite order-dependent / flaky:

**Caches.** The asset *descriptor* cache keys only on asset kind and lives in the
process-global LocMemCache, so seed data published by one test leaks into the
next. Clearing every configured cache before each test restores isolation.

**Per-variant evaluation caches.** ``CompiledEvaluationSpecCache`` and
``VariantTargetStateHashCache`` are class-level dicts keyed on
``(variant.id, semantic_key)``. Each test's transaction rolls back, so the
database reuses row ids, and fixtures often leave ``semantic_key`` empty: a
later test's different variant can then hit an earlier test's compiled spec or
target hash. Clearing both before and after every test restores isolation.
"""

import pytest
from django.core.cache import caches


def _clear_variant_evaluation_caches() -> None:
    # Imported here: the root conftest loads before Django apps are ready.
    from common.git.repository_state import VariantTargetStateHashCache
    from evaluation.compiler import CompiledEvaluationSpecCache

    CompiledEvaluationSpecCache._cache.clear()
    VariantTargetStateHashCache._cache.clear()


@pytest.fixture(autouse=True)
def _isolate_test_side_effects(settings):
    # The former production curriculum command now exists only as an isolated
    # engine fixture. Normal Django settings intentionally leave it disabled.
    settings.ALLOW_RETIRED_CURRICULUM_FIXTURE_SEED = True
    for alias in settings.CACHES:
        caches[alias].clear()
    _clear_variant_evaluation_caches()
    yield
    _clear_variant_evaluation_caches()
