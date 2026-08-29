"""Ordered Frostbound Citadel form-drill composition."""

from __future__ import annotations

from .temper_the_commit import DRILLS as _TEMPER_THE_COMMIT_DRILLS
from .temper_the_commit import WORKFLOWS as _TEMPER_THE_COMMIT_WORKFLOWS
from .choose_the_integration import DRILLS as _CHOOSE_THE_INTEGRATION_DRILLS
from .choose_the_integration import WORKFLOWS as _CHOOSE_THE_INTEGRATION_WORKFLOWS
from .survive_the_conflict import DRILLS as _SURVIVE_THE_CONFLICT_DRILLS
from .survive_the_conflict import WORKFLOWS as _SURVIVE_THE_CONFLICT_WORKFLOWS
from .move_the_patch import DRILLS as _MOVE_THE_PATCH_DRILLS
from .move_the_patch import WORKFLOWS as _MOVE_THE_PATCH_WORKFLOWS
from .reforge_the_branch import DRILLS as _REFORGE_THE_BRANCH_DRILLS
from .reforge_the_branch import WORKFLOWS as _REFORGE_THE_BRANCH_WORKFLOWS
from .govern_the_remote import DRILLS as _GOVERN_THE_REMOTE_DRILLS
from .govern_the_remote import WORKFLOWS as _GOVERN_THE_REMOTE_WORKFLOWS
from .deliver_the_release import DRILLS as _DELIVER_THE_RELEASE_DRILLS
from .deliver_the_release import WORKFLOWS as _DELIVER_THE_RELEASE_WORKFLOWS
from .hunt_the_regression import DRILLS as _HUNT_THE_REGRESSION_DRILLS
from .hunt_the_regression import WORKFLOWS as _HUNT_THE_REGRESSION_WORKFLOWS
from .publish_the_core import DRILLS as _PUBLISH_THE_CORE_DRILLS
from .publish_the_core import WORKFLOWS as _PUBLISH_THE_CORE_WORKFLOWS

LEVELS = [
    *_TEMPER_THE_COMMIT_DRILLS,
    *_TEMPER_THE_COMMIT_WORKFLOWS,
    *_CHOOSE_THE_INTEGRATION_DRILLS,
    *_CHOOSE_THE_INTEGRATION_WORKFLOWS,
    *_SURVIVE_THE_CONFLICT_DRILLS,
    *_SURVIVE_THE_CONFLICT_WORKFLOWS,
    *_MOVE_THE_PATCH_DRILLS,
    *_MOVE_THE_PATCH_WORKFLOWS,
    *_REFORGE_THE_BRANCH_DRILLS,
    *_REFORGE_THE_BRANCH_WORKFLOWS,
    *_GOVERN_THE_REMOTE_DRILLS,
    *_GOVERN_THE_REMOTE_WORKFLOWS,
    *_DELIVER_THE_RELEASE_DRILLS,
    *_DELIVER_THE_RELEASE_WORKFLOWS,
    *_HUNT_THE_REGRESSION_DRILLS,
    *_HUNT_THE_REGRESSION_WORKFLOWS,
    *_PUBLISH_THE_CORE_DRILLS,
    *_PUBLISH_THE_CORE_WORKFLOWS,
]
