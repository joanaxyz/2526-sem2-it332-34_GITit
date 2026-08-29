"""Project-wide pytest fixtures that keep each test hermetic.

The suite runs in one process and several tests seed official data (via
``seed_curriculum`` / ``seed_all``). One shared side effect leaked between tests
and made the suite order-dependent / flaky:

**Caches.** The asset *descriptor* cache keys only on asset kind and lives in the
process-global LocMemCache, so seed data published by one test leaks into the
next. Clearing every configured cache before each test restores isolation.
"""

import pytest
from django.core.cache import caches


@pytest.fixture(autouse=True)
def _isolate_test_side_effects(settings):
    for alias in settings.CACHES:
        caches[alias].clear()
    yield
