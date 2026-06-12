"""Authored tomes: general lessons that open as books in the tower.

A tome is not a command. It teaches an idea (mental models, platform rules,
workflow philosophy) with the same section/block vocabulary the command
library uses, so the book reader renders both. Unlike adventures and
challenges, tomes are not a repeating per-storey pattern — each one is
authored onto a specific storey (the frozen ``"module"`` key = storey slug)
at an explicit ``placement`` slot:

  * ``above_adventure``  — before the storey's Command Adventure gate
  * ``below_adventure``  — between the adventure and the challenges
  * ``below_challenges`` — after the storey's challenges

Pages are built at import time through ``tome_pages`` so the seed persists
ready-to-render pages, exactly like seeded command library entries.
"""

from __future__ import annotations

from curriculum.library import _bullets, _callout, _diagram, _paragraph, _warning, tome_pages

TOMES = [
    {
        "module": "creating-inspecting-repositories",
        "slug": "how-git-thinks",
        "title": "How Git Thinks",
        "summary": (
            "The four places your work lives — working directory, staging area, "
            "commit history, and HEAD — and how every Git command moves changes between them."
        ),
        "placement": "above_adventure",
        "pages": tome_pages(
            [
                {
                    "id": "overview",
                    "title": "The four places",
                    "type": "overview",
                    "content": [
                        _paragraph(
                            "Every Git command you will ever run moves information between four "
                            "places. Once you can name them, no command is mysterious — each one "
                            "is just an arrow between two of these places."
                        ),
                        _bullets(
                            "The places",
                            [
                                "Working directory — the files you actually edit.",
                                "Staging area — the snapshot you are assembling for the next commit.",
                                "Commit history — permanent snapshots, linked into a graph.",
                                "HEAD — the marker for where you are standing in that graph.",
                            ],
                        ),
                        _diagram(
                            kind="flow",
                            title="Where work flows",
                            caption="add moves edits into staging; commit seals staging into history; HEAD points at where you stand.",
                            nodes=[
                                {"id": "wd", "label": "Working directory", "accent": "muted"},
                                {"id": "staging", "label": "Staging area", "accent": "cyan"},
                                {"id": "history", "label": "Commit history", "accent": "cyan"},
                            ],
                            edges=[
                                {"from": "wd", "to": "staging", "label": "git add"},
                                {"from": "staging", "to": "history", "label": "git commit"},
                            ],
                        ),
                    ],
                },
                {
                    "id": "snapshots-not-diffs",
                    "title": "Snapshots, not saves",
                    "type": "concept",
                    "content": [
                        _paragraph(
                            "A commit is not a 'save' of one file — it is a snapshot of the whole "
                            "project at one moment, plus a link to the snapshot that came before it. "
                            "That chain of links is the commit graph you see in the tower's diagrams."
                        ),
                        _callout(
                            "Why the graph matters",
                            "Branches and merges are nothing more than names pointing at commits in "
                            "this graph. When a scenario asks you to 'move a branch' or 'undo a "
                            "commit', you are really moving pointers and adding snapshots.",
                        ),
                        _warning(
                            "Editing a file changes only the working directory. Until you stage and "
                            "commit, Git's history does not know your change exists."
                        ),
                    ],
                },
                {
                    "id": "reading-before-acting",
                    "title": "Read the state before acting",
                    "type": "practice-notes",
                    "content": [
                        _paragraph(
                            "Every quest in this tower starts the same way: look at the repository "
                            "diagram and status signals first, then decide which arrow you need. "
                            "The answer is always a repository state, never a memorized command string."
                        ),
                        _bullets(
                            "Before every command, ask",
                            [
                                "Where is the change I care about right now — working directory, staging, or history?",
                                "Where does it need to end up?",
                                "Which command moves work between exactly those two places?",
                            ],
                        ),
                    ],
                },
            ]
        ),
    },
]
