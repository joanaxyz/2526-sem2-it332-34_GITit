"""Official Specific Objective (SO) to adventure-level mapping for per-SO CAR.

Only the SOs measured by CAR (Command Accuracy Rate) are mapped; the HLCR,
ARC and RTA objectives are measured per module instead. The mapping is at
level granularity: an SO's CAR is computed from every command submitted in
the listed levels' tier runs (story git-it-legacy, replays excluded), so a
level that exercised several commands counts all of them toward its SO.

Every level currently maps to exactly one SO. If a level ever needs to count
toward several SOs, list it under each and note the limitation here, because
level-level CAR cannot separate the commands that belong to each SO.
"""

SO_CAR_LEVELS: dict[str, tuple[str, ...]] = {
    # Module 1 - Local Repository Foundations
    "SO 1.1": ("initializing-a-local-repository",),
    "SO 1.2": ("cloning-a-remote-repository",),
    "SO 1.3": ("staging-and-committing-basic-workflow",),
    "SO 1.4": ("partial-staging-and-git-add-p",),
    "SO 1.5": ("amending-commits",),
    "SO 1.6": ("unstaging-and-discarding-changes",),
    # Module 2 - Branching and Collaboration
    "SO 2.1": ("creating-and-switching-branches",),
    # Limitation: the SO is "Branch Naming Conventions and Housekeeping", but
    # this level covers branch naming only, not housekeeping (managing stale
    # branches), so its CAR says nothing about housekeeping commands.
    "SO 2.2": ("branch-naming-and-housekeeping",),
    "SO 2.3": ("stashing-work-in-progress",),
    "SO 2.4": ("pushing-to-a-remote",),
    "SO 2.5": ("fetching-and-pulling",),
    "SO 2.6": ("reconciling-diverged-histories",),
    "SO 2.7": ("completing-branch-merges",),
    "SO 2.8": ("squash-merging",),
    "SO 2.9": ("deleting-and-recovering-remote-branches",),
    # Module 3 - Conflict Resolution
    "SO 3.1": ("resolving-conflicts-manually",),
    "SO 3.2": ("using-a-merge-tool",),
    "SO 3.3": ("cherry-picking-commits",),
    # Module 4 - Advanced Recovery and History
    "SO 4.1": ("recovering-from-hard-resets",),
    "SO 4.2": ("reversing-pushed-commits-safely",),
    "SO 4.3": ("completing-rebase-recovery-sequences",),
}
