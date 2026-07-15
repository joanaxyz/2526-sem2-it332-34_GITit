"""Shared command-submission response helpers."""

from common.git.repository_state import command_response_includes_project_tree


def repository_response_snapshot(
    snapshotter,
    *,
    command_result,
    previous_state: dict,
    next_state: dict,
):
    """Build the right repository snapshot for a command response.

    Commands that affect project-tree presentation return a full tree snapshot;
    other commands return the cheaper command-focused snapshot. Both Challenge
    and Adventure submissions use the same rule.
    """

    if command_response_includes_project_tree(
        command_result=command_result,
        previous_state=previous_state,
        next_state=next_state,
    ):
        return snapshotter.snapshot(next_state, already_normalized=True)
    return snapshotter.snapshot_for_command(next_state, already_normalized=True)
