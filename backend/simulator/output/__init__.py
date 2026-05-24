from __future__ import annotations

from simulator.output.add import format_add
from simulator.output.branch import format_branch
from simulator.output.check_ignore import format_check_ignore
from simulator.output.checkout import format_checkout
from simulator.output.commit import format_commit
from simulator.output.diff import format_diff
from simulator.output.errors import OUTPUT_REFERENCE
from simulator.output.init import format_init
from simulator.output.log import format_log
from simulator.output.ls_files import format_ls_files
from simulator.output.reflog import format_reflog
from simulator.output.remote import format_remote
from simulator.output.reset import format_reset
from simulator.output.restore import format_restore
from simulator.output.rm import format_rm
from simulator.output.show import format_show
from simulator.output.status import format_status


class GitLikeOutputFormatter:
    reference = OUTPUT_REFERENCE

    def format(self, runtime, state: dict, intent, outcome) -> tuple[str, str]:
        if outcome.stdout is not None or outcome.stderr is not None:
            return outcome.stdout or "", outcome.stderr or ""
        formatter = {
            "init": format_init,
            "status": lambda rt, st, oc: format_status(
                rt,
                st,
                short=bool(oc.details.get("short")),
                branch=bool(oc.details.get("branch")),
                ignored=bool(oc.details.get("ignored")),
            ),
            "add": format_add,
            "commit": format_commit,
            "diff": format_diff,
            "log": format_log,
            "show": format_show,
            "branch": format_branch,
            "checkout": format_checkout,
            "switch": format_checkout,
            "restore": format_restore,
            "reset": format_reset,
            "remote": format_remote,
            "rm": format_rm,
            "reflog": format_reflog,
            "check-ignore": format_check_ignore,
            "ls-files": format_ls_files,
        }.get(outcome.command)
        if formatter is None:
            return "", ""
        return formatter(runtime, state, outcome), ""


__all__ = ["GitLikeOutputFormatter", "OUTPUT_REFERENCE"]
