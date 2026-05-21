from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygit2


@dataclass(frozen=True)
class MaterializedRepository:
    repo: pygit2.Repository
    aliases_to_oids: dict[str, pygit2.Oid]


class Pygit2RepositoryMaterializer:
    """Build an isolated libgit2 repository from the authored scenario state.

    The authored scenario data uses stable teaching aliases such as ``c0`` and
    ``r0``. pygit2 necessarily creates real object IDs. This service is the
    translation boundary between those two worlds.
    """

    def materialize(self, *, state: dict, path: str | Path) -> MaterializedRepository:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        head = state.get("head", {})
        initial_head = head.get("name") if head.get("type") == "branch" else "main"
        repo = pygit2.init_repository(str(path), initial_head=initial_head or "main")
        signature = pygit2.Signature("GIT it", "git-it@example.test")
        aliases_to_oids: dict[str, pygit2.Oid] = {}
        empty_tree = repo.TreeBuilder().write()

        for commit in state.get("commits", []):
            alias = commit["id"]
            parents = [
                aliases_to_oids[parent]
                for parent in commit.get("parents", [])
                if parent in aliases_to_oids
            ]
            oid = repo.create_commit(
                None,
                signature,
                signature,
                commit.get("message", alias),
                empty_tree,
                parents,
            )
            aliases_to_oids[alias] = oid

        self._materialize_branches(repo=repo, state=state, aliases_to_oids=aliases_to_oids)
        self._materialize_head(repo=repo, state=state, aliases_to_oids=aliases_to_oids)
        return MaterializedRepository(repo=repo, aliases_to_oids=aliases_to_oids)

    def _materialize_branches(
        self,
        *,
        repo: pygit2.Repository,
        state: dict,
        aliases_to_oids: dict[str, pygit2.Oid],
    ) -> None:
        for name, alias in state.get("branches", {}).items():
            if not alias:
                continue
            oid = aliases_to_oids.get(alias)
            if not oid:
                continue
            repo.branches.local.create(name, repo[oid], force=True)

    def _materialize_head(
        self,
        *,
        repo: pygit2.Repository,
        state: dict,
        aliases_to_oids: dict[str, pygit2.Oid],
    ) -> None:
        head = state.get("head", {})
        if head.get("type") == "branch" and head.get("name"):
            branch_name = head["name"]
            if branch_name in repo.branches.local:
                repo.set_head(f"refs/heads/{branch_name}")
            return

        target = aliases_to_oids.get(head.get("target"))
        if target:
            repo.set_head(target)


class Pygit2RepositorySnapshotter:
    def snapshot(self, *, repo: pygit2.Repository) -> dict:
        branches = {
            name: str(repo.branches.local[name].target)
            if repo.branches.local[name].target
            else None
            for name in repo.branches.local
        }
        head = self._head_payload(repo)
        return {
            "repository_initialized": True,
            "commits": self._commits(repo),
            "branches": branches,
            "head": head,
            "staging": {},
            "working_tree": {
                path: self._status_label(flags)
                for path, flags in repo.status().items()
            },
            "conflicts": [],
            "remotes": {remote.name: remote.url for remote in repo.remotes},
            "remote_branches": {},
            "upstream_tracking": {},
            "stash_stack": [],
            "reflog": [],
        }

    def _head_payload(self, repo: pygit2.Repository) -> dict:
        if repo.head_is_unborn:
            return {"type": "branch", "name": repo.head.shorthand, "target": None}
        if repo.head_is_detached:
            return {"type": "detached", "target": str(repo.head.target)}
        return {
            "type": "branch",
            "name": repo.head.shorthand,
            "target": str(repo.head.target),
        }

    def _commits(self, repo: pygit2.Repository) -> list[dict]:
        if repo.head_is_unborn:
            return []
        commits = []
        for commit in repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL | pygit2.GIT_SORT_REVERSE):
            commits.append(
                {
                    "id": str(commit.id),
                    "message": commit.message.strip(),
                    "parents": [str(parent.id) for parent in commit.parents],
                }
            )
        return commits

    def _status_label(self, flags: int) -> str:
        if flags & pygit2.GIT_STATUS_WT_NEW:
            return "untracked"
        if flags & (pygit2.GIT_STATUS_WT_DELETED | pygit2.GIT_STATUS_INDEX_DELETED):
            return "deleted"
        if flags & (pygit2.GIT_STATUS_WT_MODIFIED | pygit2.GIT_STATUS_INDEX_MODIFIED):
            return "modified"
        if flags & pygit2.GIT_STATUS_INDEX_NEW:
            return "added"
        return "updated"
