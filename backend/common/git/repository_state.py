"""Shared repository-state helpers for command-response services."""

from collections import OrderedDict

from simulator.services import RepositoryStateSimulator


class VariantTargetStateHashCache:
    _cache: OrderedDict[tuple[int, str], str] = OrderedDict()
    _max_entries = 512

    def hash_for(self, *, variant, state_tools: RepositoryStateSimulator) -> str:
        key = (variant.id, variant.semantic_key or "")
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return cached

        state_hash = state_tools.state_hash(variant.target_state)
        self._cache[key] = state_hash
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_entries:
            self._cache.popitem(last=False)
        return state_hash


def state_affects_visible_tree(previous_state: dict, next_state: dict) -> bool:
    for key in ("commits", "staging", "working_tree", "conflicts", "branches", "head"):
        if previous_state.get(key) != next_state.get(key):
            return True
    return False


def command_response_includes_project_tree(
    *, command_result, previous_state: dict, next_state: dict
) -> bool:
    if not command_result.processed or command_result.diagnostic:
        return False
    return state_affects_visible_tree(previous_state, next_state)
