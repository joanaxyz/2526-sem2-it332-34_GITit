"""Backward-compatible registry module for supported simulated commands."""

from simulator.git_commands import GitCommandRegistry, GitCommandSpec

__all__ = ["GitCommandRegistry", "GitCommandSpec"]
