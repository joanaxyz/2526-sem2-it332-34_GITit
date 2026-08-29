from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERIFICATION_DIR = ROOT / "common" / "git" / "verification"


def test_git_transition_verifier_is_a_compatibility_shim_only():
    shim = ROOT / "common" / "git" / "command_transition_verifier.py"
    source = shim.read_text()

    assert "Backward-compatible import shim" in source
    assert "class ClientTransitionVerifier" not in source
    assert len(source.splitlines()) <= 8


def test_git_verification_has_command_family_modules():
    expected_modules = {
        "assertions.py",
        "commit_history.py",
        "init_clone_remote.py",
        "merge_stash.py",
        "refs.py",
        "staging.py",
        "verifier.py",
    }

    assert expected_modules.issubset({path.name for path in VERIFICATION_DIR.glob("*.py")})


def test_git_verifier_uses_handler_map_instead_of_long_branch_chain():
    source = (VERIFICATION_DIR / "verifier.py").read_text()

    assert "VERIFY_HANDLERS" in source
    assert "getattr(self, handler_name)" in source
    assert source.count("elif command_family ==") == 0
