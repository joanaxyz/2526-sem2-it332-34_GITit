from unittest import mock

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


@mock.patch("common.management.commands.seed_all.call_command")
def test_seed_all_is_non_destructive_by_default(mock_call_command):
    call_command("seed_all", verbosity=0)

    assert mock_call_command.call_args_list == [
        mock.call("seed_legacy_modules", verbosity=0),
        mock.call("seed_command_library", verbosity=0),
        mock.call("seed_drills", verbosity=0),
    ]


def test_seed_all_reset_requires_explicit_confirmation():
    with pytest.raises(CommandError, match="both --reset and --confirm-reset"):
        call_command("seed_all", reset=True, verbosity=0)


def test_seed_all_confirmed_reset_is_retired():
    with pytest.raises(CommandError, match="reset is retired"):
        call_command("seed_all", reset=True, confirm_reset=True, verbosity=0)
