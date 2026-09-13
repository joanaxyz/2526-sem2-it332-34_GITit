"""Cheap backend-side verification for client-submitted Git transitions.

The browser simulator still owns instant UI feedback. This verifier mirrors the
supported mutating command transitions that can affect persisted progress/rewards
without shelling out to Git, so a forged client next_state cannot silently earn
completion.
"""

from __future__ import annotations

import copy

from common.exceptions import BadRequest

# `merge_abort_state` holds a whole repository snapshot taken before a rollback
# point (a conflicting merge, a reset). Only the *outer* state is normalized on
# either side, so that nested snapshot reaches the comparison in whatever shape
# its author left it: the browser stores a raw clone of its live state - which
# omits keys it has deleted, e.g. `git commit` drops `merge_abort_state` - while
# the backend snapshots an already-normalized previous_state that still carries
# every default. Equivalent transitions then hashed differently and the learner
# saw "Command failed" on a correct command. Normalizing the nested snapshot on
# both sides before hashing keeps the comparison about real repository
# differences instead of default-key bookkeeping.
NESTED_SNAPSHOT_KEY = "merge_abort_state"
# Snapshots can nest (reset after a conflicted merge). Chains are short in
# practice; the cap just bounds the walk on hostile input.
MAX_NESTED_SNAPSHOT_DEPTH = 8


class TransitionAssertionMixin:
    def _comparable_state(self, state: dict) -> dict:
        """Return `state` with nested rollback snapshots normalized for hashing."""

        if not isinstance(state, dict):
            return state
        payload = copy.deepcopy(state)
        node = payload
        for _ in range(MAX_NESTED_SNAPSHOT_DEPTH):
            nested = node.get(NESTED_SNAPSHOT_KEY)
            if not isinstance(nested, dict):
                # Missing or null: both sides mean "no snapshot held".
                node[NESTED_SNAPSHOT_KEY] = {}
                return payload
            if not nested:
                return payload
            self.normalizer.ensure_shape(nested)
            node = nested
        return payload

    def _require_equivalent_expected(
        self, expected: dict, next_state: dict, command_name: str
    ) -> None:
        if self.tools.state_hash_for_normalized(
            self._comparable_state(expected)
        ) != self.tools.state_hash_for_normalized(self._comparable_state(next_state)):
            raise BadRequest(
                f"execution.next_state does not match the submitted {command_name} command."
            )

    def _require_same_key(self, key: str, previous_state: dict, next_state: dict) -> None:
        if previous_state.get(key) != next_state.get(key):
            raise BadRequest(f"execution.next_state cannot change {key} for this command.")

    def _require_same_state(self, previous_state: dict, next_state: dict, message: str) -> None:
        if self.tools.state_hash_for_normalized(
            self._comparable_state(previous_state)
        ) != self.tools.state_hash_for_normalized(self._comparable_state(next_state)):
            raise BadRequest(message)
