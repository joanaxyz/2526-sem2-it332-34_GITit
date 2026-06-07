FOUNDATIONS = [
    {
        "slug": "git-mental-model",
        "title": "Git Mental Model",
        "summary": "Repositories are snapshots connected by commits, with names pointing at history.",
        "body": "Think in repository areas: working directory, staging area, local repository, branch pointers, HEAD, remotes, and stash.",
        "icon": "brain",
        "cards": [
            {"title": "Working directory", "body": "Files you can currently edit."},
            {"title": "Staging area", "body": "The next snapshot you are preparing."},
            {"title": "Commits", "body": "Saved snapshots connected by parent links."},
            {"title": "HEAD", "body": "The current checkout, usually attached to a branch."},
        ],
    },
    {
        "slug": "platform-rules",
        "title": "How This Platform Works",
        "summary": "Use the simulated terminal, read the repository visuals, and reach the requested outcome.",
        "body": "The simulator accepts Git commands and mutates an in-memory repository. It never runs real Git on your machine.",
        "icon": "terminal",
        "cards": [
            {"title": "No-answer policy", "body": "Prompts explain the target state, not the exact command sequence."},
            {"title": "Command counting", "body": "State-changing Git commands count toward the budget; diagnostics do not."},
            {"title": "Repository visuals", "body": "Use the state lens for files and index state, and the DAG for history."},
        ],
    },
]
