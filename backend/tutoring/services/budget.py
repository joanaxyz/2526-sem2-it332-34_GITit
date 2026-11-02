"""Optional shared outbound-attempt budget. No prompts, keys or user data stored."""

import logging
import math
import time

from django.conf import settings
from django.core.cache import caches

logger = logging.getLogger(__name__)


class BudgetUnavailable(Exception):
    pass


def reserve_provider_call():
    """Return retry seconds when exhausted, otherwise None (reservation admitted).

    Redis add (SET NX) and incr are atomic across workers. Reserve before every
    HTTP send; failed/cancelled attempts aren't refunded. Redis restart/eviction
    can reset this allowance, so providers must enforce monetary budgets too.
    """
    limit = settings.TUTOR_PROVIDER_DAILY_LIMIT
    if not limit:
        return None
    now = time.time()
    day = int(now // 86400)
    seconds = max(1, math.ceil((day + 1) * 86400 - now))
    key = f"tutor:provider-budget:utc:{day}"
    try:
        budget = caches["provider_budget"]
        count = 1 if budget.add(key, 1, timeout=seconds) else budget.incr(key)
        if not isinstance(count, int) or isinstance(count, bool):
            raise ValueError("Budget counter unavailable")
    except Exception:
        # Do not log exception text: a cache connection error can contain a URI.
        logger.error("tutor_provider_budget_unavailable")
        raise BudgetUnavailable from None
    if count > limit:
        logger.warning("tutor_provider_budget_exhausted", extra={"retry_after_seconds": seconds})
        return seconds
    return None
