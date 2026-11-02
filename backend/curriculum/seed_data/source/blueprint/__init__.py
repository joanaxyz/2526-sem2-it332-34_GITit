"""Composed authored blueprint seed data."""

from __future__ import annotations

from .adventure_connect_and_inspect import ADVENTURE_LEVELS as _adventure_connect_and_inspect
from .adventure_create_and_move import ADVENTURE_LEVELS as _adventure_create_and_move
from .adventure_detach_and_clean import ADVENTURE_LEVELS as _adventure_detach_and_clean
from .adventure_integrate_branches import ADVENTURE_LEVELS as _adventure_integrate_branches
from .adventure_integrate_upstream import ADVENTURE_LEVELS as _adventure_integrate_upstream
from .adventure_manage_the_merge import ADVENTURE_LEVELS as _adventure_manage_the_merge
from .adventure_publish_work import ADVENTURE_LEVELS as _adventure_publish_work
from .adventure_repository_foundations import ADVENTURE_LEVELS as _adventure_repository_foundations
from .adventure_resolve_conflicts import ADVENTURE_LEVELS as _adventure_resolve_conflicts
from .adventure_reverse_and_recover import ADVENTURE_LEVELS as _adventure_reverse_and_recover
from .adventure_seal_the_snapshot import ADVENTURE_LEVELS as _adventure_seal_the_snapshot
from .adventure_shelve_work import ADVENTURE_LEVELS as _adventure_shelve_work
from .adventure_stage_with_intent import ADVENTURE_LEVELS as _adventure_stage_with_intent
from .adventure_step_back_safely import ADVENTURE_LEVELS as _adventure_step_back_safely
from .adventure_transplant_commits import ADVENTURE_LEVELS as _adventure_transplant_commits
from .adventure_untrack_and_undo_edits import ADVENTURE_LEVELS as _adventure_untrack_and_undo_edits
from .challenge_specs import BLUEPRINT_CHALLENGE_SPECS

BLUEPRINT_ADVENTURE_LEVELS = {
    'repository-foundations': _adventure_repository_foundations,
    'stage-with-intent': _adventure_stage_with_intent,
    'untrack-and-undo-edits': _adventure_untrack_and_undo_edits,
    'seal-the-snapshot': _adventure_seal_the_snapshot,
    'create-and-move': _adventure_create_and_move,
    'detach-and-clean': _adventure_detach_and_clean,
    'integrate-branches': _adventure_integrate_branches,
    'resolve-conflicts': _adventure_resolve_conflicts,
    'manage-the-merge': _adventure_manage_the_merge,
    'step-back-safely': _adventure_step_back_safely,
    'reverse-and-recover': _adventure_reverse_and_recover,
    'shelve-work': _adventure_shelve_work,
    'transplant-commits': _adventure_transplant_commits,
    'connect-and-inspect': _adventure_connect_and_inspect,
    'integrate-upstream': _adventure_integrate_upstream,
    'publish-work': _adventure_publish_work,
}

__all__ = ["BLUEPRINT_ADVENTURE_LEVELS", "BLUEPRINT_CHALLENGE_SPECS"]
