from simulator.commands.add import AddCommandHandler
from simulator.commands.branch import BranchCommandHandler
from simulator.commands.check_ignore import CheckIgnoreCommandHandler
from simulator.commands.checkout import CheckoutCommandHandler
from simulator.commands.cherry_pick import CherryPickCommandHandler
from simulator.commands.clone import CloneCommandHandler
from simulator.commands.commit import CommitCommandHandler
from simulator.commands.config import ConfigCommandHandler
from simulator.commands.diff import DiffCommandHandler
from simulator.commands.fetch import FetchCommandHandler
from simulator.commands.init import InitCommandHandler
from simulator.commands.log import LogCommandHandler
from simulator.commands.ls_files import LsFilesCommandHandler
from simulator.commands.merge import MergeCommandHandler
from simulator.commands.mergetool import MergetoolCommandHandler
from simulator.commands.merge_base import MergeBaseCommandHandler
from simulator.commands.pull import PullCommandHandler
from simulator.commands.push import PushCommandHandler
from simulator.commands.reflog import ReflogCommandHandler
from simulator.commands.rebase import RebaseCommandHandler
from simulator.commands.reset import ResetCommandHandler
from simulator.commands.remote import RemoteCommandHandler
from simulator.commands.restore import RestoreCommandHandler
from simulator.commands.rm import RmCommandHandler
from simulator.commands.rev_list import RevListCommandHandler
from simulator.commands.revert import RevertCommandHandler
from simulator.commands.show import ShowCommandHandler
from simulator.commands.stash import StashCommandHandler
from simulator.commands.status import StatusCommandHandler
from simulator.commands.switch import SwitchCommandHandler


def command_handlers() -> dict:
    handlers = [
        InitCommandHandler(),
        CloneCommandHandler(),
        StatusCommandHandler(),
        AddCommandHandler(),
        CommitCommandHandler(),
        DiffCommandHandler(),
        LogCommandHandler(),
        ShowCommandHandler(),
        BranchCommandHandler(),
        RestoreCommandHandler(),
        RemoteCommandHandler(),
        RmCommandHandler(),
        ReflogCommandHandler(),
        CheckIgnoreCommandHandler(),
        CheckoutCommandHandler(),
        LsFilesCommandHandler(),
        MergeCommandHandler(),
        MergetoolCommandHandler(),
        ConfigCommandHandler(),
        FetchCommandHandler(),
        CherryPickCommandHandler(),
        ResetCommandHandler(),
        RevertCommandHandler(),
        RebaseCommandHandler(),
        MergeBaseCommandHandler(),
        RevListCommandHandler(),
        SwitchCommandHandler(),
        StashCommandHandler(),
        PushCommandHandler(),
        PullCommandHandler(),
    ]
    return {handler.command: handler for handler in handlers}


__all__ = ["command_handlers"]
