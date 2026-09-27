from copy import deepcopy

from simulator.trajectory import (
    RepositoryFingerprinter,
    build_solution_trajectory,
    describe_transition,
    next_solution_step,
    route_position,
)


def repo(**overrides):
    state = {
        "repository_initialized": True,
        "commits": [{"id": "c0", "parents": [], "tree": {"README.md": "v1"}, "message": "Initial"}],
        "branches": {"main": "c0"},
        "head": {"type": "branch", "name": "main"},
        "working_tree": {},
        "staging": {},
    }
    state.update(overrides)
    return state


def trajectory(commands, states, final):
    return build_solution_trajectory({
        "steps": [
            {"command": command, "diagnostic": command.split()[1] in {"status", "log", "show"}, "ready": state}
            for command, state in zip(commands, states, strict=True)
        ],
        "final": final,
    })


def test_fingerprint_ignores_generated_ids_bookkeeping_and_status_spelling():
    fingerprinter = RepositoryFingerprinter()
    original = repo(staging={"app.py": "changed"}, operation_metadata={"last_init_quiet": True})
    renamed = repo(
        commits=[{"id": "abc123", "parents": [], "tree": {"README.md": "v1"}, "message": "Initial"}],
        branches={"main": "abc123"},
        staging={"app.py": "modified"},
        last_switch_branch="main",
        reflog=[{"message": "anything"}],
    )
    assert fingerprinter.fingerprints(original) == fingerprinter.fingerprints(renamed)


def test_commit_message_matters_exactly_but_not_coarsely():
    fingerprinter = RepositoryFingerprinter()
    authored = fingerprinter.fingerprints(repo())
    reworded = repo()
    reworded["commits"][0]["message"] = "My own words"
    learner = fingerprinter.fingerprints(reworded)
    assert authored["exact"] != learner["exact"]
    assert authored["coarse"] == learner["coarse"]


def test_file_content_matters_exactly_but_not_coarsely():
    fingerprinter = RepositoryFingerprinter()
    authored = fingerprinter.fingerprints(repo(working_tree={"a.txt": {"status": "modified", "content": "x"}}))
    learner = fingerprinter.fingerprints(repo(working_tree={"a.txt": {"status": "modified", "content": "y"}}))
    assert authored["exact"] != learner["exact"]
    assert authored["coarse"] == learner["coarse"]


def test_long_histories_do_not_recurse():
    commits = [{"id": f"c{i}", "parents": [f"c{i - 1}"] if i else [], "tree": {"f": str(i)}, "message": str(i)}
               for i in range(3000)]
    RepositoryFingerprinter().fingerprints(repo(commits=commits, branches={"main": "c2999"}))


def test_next_step_skips_diagnostics_and_ends_at_the_target():
    start = repo(working_tree={"a.txt": "modified"})
    staged = repo(staging={"a.txt": "modified"})
    route = trajectory(["git status", "git add a.txt"], [start, start], staged)
    assert next_solution_step(route, start)["command"] == "git add a.txt"
    assert next_solution_step(route, staged) is None
    assert route_position(route, staged) == 2


def test_learner_commit_message_still_follows_the_route():
    start = repo(staging={"a.txt": "modified"})
    after = repo(
        commits=[
            {"id": "c0", "parents": [], "tree": {"README.md": "v1"}, "message": "Initial"},
            {"id": "c1", "parents": ["c0"], "tree": {"README.md": "v1", "a.txt": "modified"}, "message": "Add a"},
        ],
        branches={"main": "c1"},
    )
    pushed = deepcopy(after)
    pushed["remotes"] = {"origin": "https://example.test/repo.git"}
    route = trajectory(["git commit -m 'Add a'", "git remote add origin https://example.test/repo.git"],
                       [start, after], pushed)
    learner = deepcopy(after)
    learner["commits"][1]["message"] = "my wording"
    assert next_solution_step(route, learner)["command"].startswith("git remote add")


def test_off_route_state_is_unknown():
    route = trajectory(["git add a.txt"], [repo(working_tree={"a.txt": "modified"})], repo())
    assert route_position(route, repo(branches={"main": "c0", "other": "c0"})) is None
    assert next_solution_step({}, repo()) is None


def test_history_resolves_a_route_that_revisits_a_state():
    start = repo(working_tree={"a.txt": "modified"})
    detached = deepcopy(start)
    detached["head"] = {"type": "detached", "target": "c0"}
    staged = repo(staging={"a.txt": "modified"})
    commands = ["git switch --detach c0", "git show", "git switch main", "git add a.txt"]
    route = trajectory(commands, [start, detached, detached, start], staged)

    assert next_solution_step(route, start, [])["command"] == "git switch --detach c0"
    assert next_solution_step(route, detached, ["git switch --detach c0"])["command"] == "git switch main"
    history = ["git switch --detach c0", "git show", "git switch main"]
    assert next_solution_step(route, start, history)["command"] == "git add a.txt"


def test_a_cycle_back_to_the_final_state_is_not_mistaken_for_done():
    start = repo(working_tree={"a.txt": "modified"})
    stashed = deepcopy(start)
    stashed["working_tree"] = {}
    stashed["stash_stack"] = [{"working_tree": {"a.txt": "modified"}}]
    route = trajectory(["git stash", "git stash pop"], [start, stashed], start)
    assert next_solution_step(route, start, [])["command"] == "git stash"
    assert next_solution_step(route, start, ["git stash", "git stash pop"]) is None


def test_pre_edit_positions_are_recognized():
    conflicted = repo(conflicts=["a.txt"], working_tree={"a.txt": {"status": "conflicted", "content": "<<<"}})
    resolved = deepcopy(conflicted)
    resolved["working_tree"]["a.txt"] = {"status": "conflicted", "content": "fixed"}
    route = build_solution_trajectory({
        "steps": [{"command": "git add a.txt", "diagnostic": False, "before_edits": conflicted, "ready": resolved}],
        "final": repo(),
    })
    assert next_solution_step(route, conflicted)["command"] == "git add a.txt"


def test_describe_transition_speaks_about_repository_meaning():
    before = repo(working_tree={"a.txt": "modified"})
    after = repo(branches={"main": "c0", "feature": "c0"}, head={"type": "branch", "name": "feature"},
                 staging={"a.txt": "modified"})
    # Staging moves a file out of the working tree: one change, not two.
    assert describe_transition(before, after) == [
        {"kind": "branch", "text": "Branch feature is created.", "action": "create", "subjects": ["feature"]},
        {"kind": "head", "text": "HEAD moves to feature.", "action": "move", "subjects": ["feature"]},
        {"kind": "staging", "text": "a.txt is staged.", "action": "add", "subjects": ["a.txt"]},
    ]
    uninitialized = repo(repository_initialized=False, commits=[], branches={})
    assert describe_transition(uninitialized, repo(commits=[], branches={"main": None}))[0] == {
        "kind": "repository", "text": "The folder becomes a Git repository.", "action": "create", "subjects": [],
    }


def test_a_commit_names_what_it_saved_instead_of_listing_unstaging():
    before = repo(staging={"a.txt": "modified"})
    after = repo(
        commits=[
            {"id": "c0", "parents": [], "tree": {"README.md": "v1"}, "message": "Initial"},
            {"id": "c1", "parents": ["c0"], "tree": {"README.md": "v1", "a.txt": "x"}, "message": "Add a"},
        ],
        branches={"main": "c1"},
    )
    assert describe_transition(before, after) == [{
        "kind": "commit", "text": "New commit on main, saving a.txt.", "action": "create",
        "subjects": ["a.txt"], "ref": "main",
    }]
