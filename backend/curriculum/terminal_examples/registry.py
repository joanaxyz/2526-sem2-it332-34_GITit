"""Ordered terminal-example renderer registry."""

from .branching import render as render_branching
from .history import render as render_history
from .recovery_remote import render as render_recovery_remote
from .setup import render as render_setup
from .working_tree import render as render_working_tree

TERMINAL_EXAMPLE_RENDERERS = (
    render_setup,
    render_history,
    render_working_tree,
    render_branching,
    render_recovery_remote,
)
