from simulator.services import RepositoryStateSimulator


def test_simulator_rejects_non_git_input_without_execution():
    state = {"commits": [], "branches": {"main": None}, "head": {"type": "branch", "name": "main"}}

    result = RepositoryStateSimulator().process(state, "powershell Remove-Item important.txt")

    assert result.processed is False
    assert result.state == state
    assert "Only simulated git commands" in result.output
