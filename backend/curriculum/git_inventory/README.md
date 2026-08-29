# Git command inventory

`baseline.json` is generated from the repository toolchain's pinned Git executable
with `python scripts/sync_git_command_inventory.py`.

The file is a coverage contract, not a claim that every internal helper should be
a scored day-to-day skill. Every command is classified as mastery, practice,
demonstration, or reference in `curriculum.seed_data.command_coverage`.

A Git upgrade must regenerate this inventory and update the coverage decision for
any added or removed command.
