COMMAND_DRILL_ADVENTURES = {
    "creating-inspecting-repositories": {
        "title": "Repository Basecamp",
        "description": "Learn how to prepare a repository and inspect its first signals.",
    },
    "tracking-changes-snapshots": {
        "title": "Preparing File Changes",
        "description": "Learn how to inspect, stage, and save file changes.",
    },
    "branching-switching": {
        "title": "Branch Navigation",
        "description": "Learn how to move between work streams once changes are safe.",
    },
}


def command_drill_adventure_for(module) -> dict:
    configured = COMMAND_DRILL_ADVENTURES.get(module.slug, {})
    return {
        "title": configured.get("title") or f"{module.title} Adventure",
        "description": configured.get("description") or module.description,
    }
