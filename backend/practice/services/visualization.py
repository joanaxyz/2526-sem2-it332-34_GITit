from simulator.state import RepositoryStateNormalizer


class RepositoryVisualizationService:
    def __init__(self) -> None:
        self.normalizer = RepositoryStateNormalizer()

    def snapshot(
        self,
        state: dict,
        *,
        previous_state: dict | None = None,
        target_state: dict | None = None,
        already_normalized: bool = False,
    ) -> dict:
        del previous_state, target_state
        # The command-submit path passes state that the executor already
        # normalized; re-normalizing here was a redundant deep-copy + walk of the
        # full repository JSON on every command.
        current = state if already_normalized else self.normalizer.normalize(state)
        return {
            "schema_version": 2,
            "commit_dag": self._commit_dag(current),
        }

    def _commit_dag(self, state: dict) -> dict:
        return {
            "commits": state.get("commits", []),
            "branches": state.get("branches", {}),
            "head": state.get("head", {}),
            "remote_tracking_branches": state.get("remote_branches", {}),
            "reflog": state.get("reflog", []),
        }
