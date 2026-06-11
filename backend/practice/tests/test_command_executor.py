"""Unit tests for the shared command-execution primitives in practice/services.

CommandExecutor and CommandCountClassifier sit under every challenge and
adventure submit; they run the in-memory simulator only, so no DB is needed.
"""

import pytest

from common.constants import COMMAND_COUNTED, COMMAND_DIAGNOSTIC, COMMAND_UNPROCESSABLE
from common.exceptions import PayloadTooLarge
from practice import services as practice_services
from practice.services import CommandCountClassifier, CommandExecutor


class TestCommandCountClassifier:
    def classify(self, **kwargs):
        return CommandCountClassifier().classify(**kwargs)

    def test_unprocessable_git_command_still_counts(self):
        # A git command the engine can't parse must still burn budget, or
        # learners could fish for syntax for free.
        assert self.classify(command="git frobnicate", processed=False) == (COMMAND_COUNTED, 1)

    def test_unprocessable_non_git_input_is_free(self):
        assert self.classify(command="ls -la", processed=False) == (COMMAND_UNPROCESSABLE, 0)

    def test_diagnostic_command_is_uncounted(self):
        assert self.classify(command="git status", processed=True, diagnostic=True) == (
            COMMAND_DIAGNOSTIC,
            0,
        )

    def test_mutating_command_counts(self):
        assert self.classify(command="git commit -m x", processed=True, diagnostic=False) == (
            COMMAND_COUNTED,
            1,
        )


class TestCommandExecutor:
    def execute(self, state, command):
        return CommandExecutor().execute(repository_state=state, command=command)

    def test_git_init_initializes_repository(self):
        execution = self.execute({}, "git init")
        assert execution.result.processed
        assert execution.state_mutated
        assert execution.next_state["repository_initialized"] is True
        assert execution.classification == COMMAND_COUNTED

    def test_diagnostic_command_does_not_mutate_state(self):
        initialized = self.execute({}, "git init").next_state
        execution = self.execute(initialized, "git status")
        assert execution.result.processed
        assert execution.state_mutated is False
        assert execution.classification == COMMAND_DIAGNOSTIC

    def test_caller_state_is_never_mutated_in_place(self):
        state = self.execute({}, "git init").next_state
        before = repr(state)
        self.execute(state, "git switch -c feature")
        assert repr(state) == before

    def test_unknown_command_reports_unprocessed(self):
        execution = self.execute({}, "echo hello")
        assert execution.result.processed is False
        assert execution.state_mutated is False

    def test_state_size_guard_rejects_oversized_state(self, monkeypatch):
        monkeypatch.setattr(practice_services, "MAX_REPOSITORY_STATE_BYTES", 10)
        with pytest.raises(PayloadTooLarge):
            self.execute({}, "git init")

    def test_state_size_guard_ignores_diagnostic_commands(self, monkeypatch):
        initialized = self.execute({}, "git init").next_state
        monkeypatch.setattr(practice_services, "MAX_REPOSITORY_STATE_BYTES", 10)
        execution = self.execute(initialized, "git status")  # must not raise
        assert execution.result.processed
