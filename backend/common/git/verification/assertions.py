"""Cheap backend-side verification for client-submitted Git transitions.

The browser simulator still owns instant UI feedback. This verifier mirrors the
supported mutating command transitions that can affect persisted progress/rewards
without shelling out to Git, so a forged client next_state cannot silently earn
completion.
"""

from __future__ import annotations

from common.exceptions import BadRequest


class TransitionAssertionMixin:
    def _require_equivalent_expected(self, expected: dict, next_state: dict, command_name: str) -> None:
        if self.tools.state_hash_for_normalized(expected) != self.tools.state_hash_for_normalized(next_state):
            raise BadRequest(f"execution.next_state does not match the submitted {command_name} command.")
    def _require_same_key(self, key: str, previous_state: dict, next_state: dict) -> None:
        if previous_state.get(key) != next_state.get(key):
            raise BadRequest(f"execution.next_state cannot change {key} for this command.")
    def _require_same_state(self, previous_state: dict, next_state: dict, message: str) -> None:
        if self.tools.state_hash_for_normalized(previous_state) != self.tools.state_hash_for_normalized(next_state):
            raise BadRequest(message)
