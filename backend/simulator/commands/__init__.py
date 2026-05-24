from simulator.commands.add import AddCommandHandler
from simulator.commands.branch import BranchCommandHandler
from simulator.commands.check_ignore import CheckIgnoreCommandHandler
from simulator.commands.checkout import CheckoutCommandHandler
from simulator.commands.commit import CommitCommandHandler
from simulator.commands.diff import DiffCommandHandler
from simulator.commands.init import InitCommandHandler
from simulator.commands.log import LogCommandHandler
from simulator.commands.ls_files import LsFilesCommandHandler
from simulator.commands.reflog import ReflogCommandHandler
from simulator.commands.remote import RemoteCommandHandler
from simulator.commands.reset import ResetCommandHandler
from simulator.commands.restore import RestoreCommandHandler
from simulator.commands.rm import RmCommandHandler
from simulator.commands.show import ShowCommandHandler
from simulator.commands.status import StatusCommandHandler
from simulator.commands.switch import SwitchCommandHandler


def command_handlers() -> dict:
    handlers = [
        InitCommandHandler(),
        StatusCommandHandler(),
        AddCommandHandler(),
        CommitCommandHandler(),
        DiffCommandHandler(),
        LogCommandHandler(),
        ShowCommandHandler(),
        BranchCommandHandler(),
        CheckoutCommandHandler(),
        SwitchCommandHandler(),
        RestoreCommandHandler(),
        ResetCommandHandler(),
        RemoteCommandHandler(),
        RmCommandHandler(),
        ReflogCommandHandler(),
        CheckIgnoreCommandHandler(),
        LsFilesCommandHandler(),
    ]
    return {handler.command: handler for handler in handlers}


__all__ = ["command_handlers"]
