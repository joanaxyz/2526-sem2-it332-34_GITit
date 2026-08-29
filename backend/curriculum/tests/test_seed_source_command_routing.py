from curriculum.seed_data.source.command_routing import adventure_for_usage


def test_command_routing_keeps_chapter_one_save_loop_together():
    assert adventure_for_usage("git-add/file") == "repository-foundations"
    assert adventure_for_usage("git-commit/message") == "repository-foundations"
    assert adventure_for_usage("git-diff/staged") == "repository-foundations"


def test_command_routing_falls_back_to_command_family_adventure():
    assert adventure_for_usage("git-push/set-upstream") == "publish-work"
    assert adventure_for_usage("unknown-command/special-case") == "found-a-repository"
