"""Ordered terminal-example renderer registry."""

from . import branching, history, recovery_remote, setup, working_tree

TERMINAL_EXAMPLE_RENDERERS = (
    setup.render,
    history.render,
    working_tree.render,
    branching.render,
    recovery_remote.render,
)
