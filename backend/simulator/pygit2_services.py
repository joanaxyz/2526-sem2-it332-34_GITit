from __future__ import annotations

import shutil
import tempfile
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

import pygit2

from simulator.services import RepositoryStateSimulator
from simulator.state import RepositoryStateNormalizer


@dataclass(frozen=True)
class MaterializedRepository:
    repo: pygit2.Repository
    aliases_to_oids: dict[str, pygit2.Oid]
    original_remote_urls: dict[str, str]


@dataclass(frozen=True)
class BridgedRepositoryState:
    state_hash: str
    normalized_state: dict


class RepositoryStateBridge:
    """Bridge authored teaching JSON and libgit2 repositories.

    Most Module 1 scenarios are authored as normalized JSON so the evaluator can
    stay state-based and deterministic. This bridge centralizes the conversion
    points to pygit2 and keeps a tiny normalized-state cache so command
    submission does not repeatedly re-normalize identical repository payloads.
    """

    _normalized_cache: OrderedDict[str, BridgedRepositoryState] = OrderedDict()
    _max_cache_entries = 128

    def __init__(self) -> None:
        self.normalizer = RepositoryStateNormalizer()
        self.state_tools = RepositoryStateSimulator()
        self.materializer = Pygit2RepositoryMaterializer()
        self.snapshotter = Pygit2RepositorySnapshotter()

    def normalize(self, state: dict) -> dict:
        state_hash = self.state_tools.state_hash(state)
        cached = self._normalized_cache.get(state_hash)
        if cached:
            self._normalized_cache.move_to_end(state_hash)
            return self.state_tools.clone_state(cached.normalized_state)
        normalized = self.normalizer.normalize(state)
        self._remember(BridgedRepositoryState(state_hash=state_hash, normalized_state=normalized))
        return self.state_tools.clone_state(normalized)

    def materialize(self, *, state: dict, path: str | Path) -> MaterializedRepository:
        return self.materializer.materialize(state=self.normalize(state), path=path)

    def snapshot(self, *, repo: pygit2.Repository, previous_state: dict | None = None) -> dict:
        return self.snapshotter.snapshot(repo=repo, previous_state=previous_state)

    def round_trip_snapshot(self, state: dict) -> dict:
        with tempfile.TemporaryDirectory(prefix="git-it-bridge-") as workspace:
            materialized = self.materialize(state=state, path=workspace)
            return self.snapshotter.snapshot(
                repo=materialized.repo,
                aliases_to_oids=materialized.aliases_to_oids,
                previous_state=state,
            )

    def _remember(self, bridged: BridgedRepositoryState) -> None:
        self._normalized_cache[bridged.state_hash] = bridged
        self._normalized_cache.move_to_end(bridged.state_hash)
        while len(self._normalized_cache) > self._max_cache_entries:
            self._normalized_cache.popitem(last=False)


class Pygit2RepositoryMaterializer:
    """Build an isolated libgit2 repository from the authored scenario state.

    The authored scenario data uses stable teaching aliases such as ``c0`` and
    ``r0``. pygit2 necessarily creates real object IDs. This service is the
    translation boundary between those two worlds.
    """

    def materialize(
        self,
        *,
        state: dict,
        path: str | Path,
        remote_url_overrides: dict[str, str] | None = None,
    ) -> MaterializedRepository:
        state = RepositoryStateNormalizer().normalize(state)
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        head = state.get("head", {})
        initial_head = head.get("name") if head.get("type") == "branch" else "main"
        repo = pygit2.init_repository(str(path), initial_head=initial_head or "main")
        repo.config["core.autocrlf"] = "false"
        signature = pygit2.Signature("GIT it", "git-it@example.test")
        aliases_to_oids: dict[str, pygit2.Oid] = {}
        commit_files: dict[str, dict[str, str]] = {}

        for commit in state.get("commits", []):
            alias = commit["id"]
            files = self._files_for_commit(commit=commit, commit_files=commit_files)
            tree = self._write_tree(repo=repo, files=files)
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
                tree,
                parents,
            )
            aliases_to_oids[alias] = oid
            commit_files[alias] = files

        self._materialize_branches(repo=repo, state=state, aliases_to_oids=aliases_to_oids)
        self._materialize_remote_refs(repo=repo, state=state, aliases_to_oids=aliases_to_oids)
        original_remote_urls = self._materialize_remotes(
            repo=repo,
            state=state,
            remote_url_overrides=remote_url_overrides or {},
        )
        self._materialize_upstream_tracking(repo=repo, state=state)
        self._materialize_head(repo=repo, state=state, aliases_to_oids=aliases_to_oids)
        self._checkout_head(repo=repo)
        self._apply_index_and_worktree(repo=repo, state=state)
        return MaterializedRepository(
            repo=repo,
            aliases_to_oids=aliases_to_oids,
            original_remote_urls=original_remote_urls,
        )

    def materialize_workspace_files(self, *, state: dict, path: str | Path) -> None:
        state = RepositoryStateNormalizer().normalize(state)
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        for source in (state.get("staging", {}), state.get("working_tree", {})):
            for relative_path, marker in source.items():
                if str(marker).lower() in {"deleted", "removed"}:
                    continue
                self._write_worktree_file(
                    root=path,
                    relative_path=relative_path,
                    content=self._file_content(relative_path, marker, "workspace"),
                )

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

    def _materialize_remote_refs(
        self,
        *,
        repo: pygit2.Repository,
        state: dict,
        aliases_to_oids: dict[str, pygit2.Oid],
    ) -> None:
        for name, alias in state.get("remote_branches", {}).items():
            oid = aliases_to_oids.get(alias)
            if not oid:
                continue
            repo.references.create(f"refs/remotes/{name}", oid, force=True)

    def _materialize_remotes(
        self,
        *,
        repo: pygit2.Repository,
        state: dict,
        remote_url_overrides: dict[str, str],
    ) -> dict[str, str]:
        original_urls: dict[str, str] = {}
        for name, original_url in state.get("remotes", {}).items():
            original_urls[name] = original_url
            repo.remotes.create(name, remote_url_overrides.get(name, original_url))
        return original_urls

    def _materialize_upstream_tracking(self, *, repo: pygit2.Repository, state: dict) -> None:
        config = repo.config
        for branch_name, upstream in state.get("upstream_tracking", {}).items():
            if "/" not in upstream:
                continue
            remote, remote_branch = upstream.split("/", 1)
            config[f"branch.{branch_name}.remote"] = remote
            config[f"branch.{branch_name}.merge"] = f"refs/heads/{remote_branch}"

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

    def _checkout_head(self, *, repo: pygit2.Repository) -> None:
        if repo.head_is_unborn:
            return
        repo.index.read_tree(repo[repo.head.target].tree)
        repo.index.write()
        repo.checkout_head(strategy=pygit2.GIT_CHECKOUT_FORCE)

    def _apply_index_and_worktree(self, *, repo: pygit2.Repository, state: dict) -> None:
        index = repo.index
        for relative_path, marker in state.get("staging", {}).items():
            if str(marker).lower() in {"deleted", "removed"}:
                try:
                    index.remove(relative_path)
                except KeyError:
                    pass
                self._remove_worktree_file(root=Path(repo.workdir), relative_path=relative_path)
                continue
            self._write_worktree_file(
                root=Path(repo.workdir),
                relative_path=relative_path,
                content=self._file_content(relative_path, marker, "staged"),
            )
            index.add(relative_path)
        index.write()

        for relative_path, marker in state.get("working_tree", {}).items():
            if str(marker).lower() in {"deleted", "removed"}:
                self._remove_worktree_file(root=Path(repo.workdir), relative_path=relative_path)
                continue
            self._write_worktree_file(
                root=Path(repo.workdir),
                relative_path=relative_path,
                content=self._file_content(relative_path, marker, "working"),
            )

    def _files_for_commit(
        self,
        *,
        commit: dict,
        commit_files: dict[str, dict[str, str]],
    ) -> dict[str, str]:
        if isinstance(commit.get("tree"), dict):
            return {
                path: self._file_content(path, marker, commit["id"])
                for path, marker in commit["tree"].items()
            }
        parents = commit.get("parents", [])
        files = dict(commit_files.get(parents[0], {})) if parents else {}
        for path, marker in (commit.get("files") or {}).items():
            if str(marker).lower() in {"deleted", "removed"}:
                files.pop(path, None)
                continue
            files[path] = self._file_content(path, marker, commit["id"])
        return files

    def _write_tree(self, *, repo: pygit2.Repository, files: dict[str, str]) -> pygit2.Oid:
        nested: dict[str, object] = {}
        for path, content in files.items():
            parts = Path(path).as_posix().split("/")
            cursor = nested
            for part in parts[:-1]:
                cursor = cursor.setdefault(part, {})
            cursor[parts[-1]] = content
        return self._write_tree_node(repo=repo, node=nested)

    def _write_tree_node(self, *, repo: pygit2.Repository, node: dict[str, object]) -> pygit2.Oid:
        builder = repo.TreeBuilder()
        for name, value in sorted(node.items()):
            if isinstance(value, dict):
                oid = self._write_tree_node(repo=repo, node=value)
                builder.insert(name, oid, pygit2.GIT_FILEMODE_TREE)
            else:
                oid = repo.create_blob(str(value).encode("utf-8"))
                builder.insert(name, oid, pygit2.GIT_FILEMODE_BLOB)
        return builder.write()

    def _write_worktree_file(self, *, root: Path, relative_path: str, content: str) -> None:
        target = root / Path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def _remove_worktree_file(self, *, root: Path, relative_path: str) -> None:
        target = root / Path(relative_path)
        if target.exists():
            target.unlink()
        parent = target.parent
        while parent != root and parent.exists():
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent

    def _file_content(self, path: str, marker: object, namespace: str) -> str:
        return f"{path}\n{namespace}: {marker}\n"


class Pygit2RepositorySnapshotter:
    def snapshot(
        self,
        *,
        repo: pygit2.Repository,
        aliases_to_oids: dict[str, pygit2.Oid] | None = None,
        previous_state: dict | None = None,
    ) -> dict:
        aliases = _OidAliasMap(aliases_to_oids or {})
        branches = {
            name: aliases.alias_for_oid(repo.branches.local[name].target)
            if repo.branches.local[name].target
            else None
            for name in repo.branches.local
        }
        remote_branches = self._remote_branches(repo=repo, aliases=aliases)
        status = repo.status()
        snapshot = {
            "repository_initialized": True,
            "commits": self._commits(repo, aliases=aliases),
            "branches": branches,
            "head": self._head_payload(repo, aliases=aliases),
            "staging": self._staging(status),
            "working_tree": self._working_tree(status),
            "conflicts": self._conflicts(repo=repo, status=status),
            "remotes": {remote.name: remote.url for remote in repo.remotes},
            "remote_branches": remote_branches,
            "upstream_tracking": self._upstream_tracking(repo=repo),
            "stash_stack": (previous_state or {}).get("stash_stack", []),
            "reflog": (previous_state or {}).get("reflog", []),
        }
        return RepositoryStateNormalizer().normalize(snapshot)

    def _head_payload(self, repo: pygit2.Repository, aliases: _OidAliasMap) -> dict:
        if repo.head_is_unborn:
            return {"type": "branch", "name": repo.head.shorthand, "target": None}
        if repo.head_is_detached:
            return {"type": "detached", "target": aliases.alias_for_oid(repo.head.target)}
        return {
            "type": "branch",
            "name": repo.head.shorthand,
            "target": aliases.alias_for_oid(repo.head.target),
        }

    def _commits(self, repo: pygit2.Repository, aliases: _OidAliasMap) -> list[dict]:
        if repo.head_is_unborn:
            return []
        commits = []
        for commit in repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL | pygit2.GIT_SORT_REVERSE):
            commits.append(
                {
                    "id": aliases.alias_for_oid(commit.id),
                    "message": commit.message.strip(),
                    "parents": [aliases.alias_for_oid(parent.id) for parent in commit.parents],
                    "files": self._changed_files(commit),
                    "tree": self._tree_files(repo, commit.tree),
                }
            )
        return commits

    def _tree_files(self, repo: pygit2.Repository, tree: pygit2.Tree, prefix: str = "") -> dict[str, str]:
        files: dict[str, str] = {}
        for entry in tree:
            path = f"{prefix}{entry.name}"
            obj = repo[entry.id]
            if isinstance(obj, pygit2.Tree):
                files.update(self._tree_files(repo, obj, f"{path}/"))
            else:
                files[path] = obj.data.decode("utf-8")
        return files

    def _changed_files(self, commit: pygit2.Commit) -> dict[str, str]:
        if commit.parents:
            diff = commit.parents[0].tree.diff_to_tree(commit.tree)
        else:
            diff = commit.tree.diff_to_tree(swap=True)
        files: dict[str, str] = {}
        for patch in diff:
            path = patch.delta.new_file.path or patch.delta.old_file.path
            files[path] = self._delta_label(patch.delta.status_char())
        return files

    def _staging(self, status: dict[str, int]) -> dict[str, str]:
        return {
            path: self._index_status_label(flags)
            for path, flags in status.items()
            if flags
            & (
                pygit2.GIT_STATUS_INDEX_NEW
                | pygit2.GIT_STATUS_INDEX_MODIFIED
                | pygit2.GIT_STATUS_INDEX_DELETED
                | pygit2.GIT_STATUS_INDEX_RENAMED
                | pygit2.GIT_STATUS_INDEX_TYPECHANGE
            )
        }

    def _working_tree(self, status: dict[str, int]) -> dict[str, str]:
        return {
            path: self._worktree_status_label(flags)
            for path, flags in status.items()
            if flags
            & (
                pygit2.GIT_STATUS_WT_NEW
                | pygit2.GIT_STATUS_WT_MODIFIED
                | pygit2.GIT_STATUS_WT_DELETED
                | pygit2.GIT_STATUS_WT_RENAMED
                | pygit2.GIT_STATUS_WT_TYPECHANGE
            )
        }

    def _conflicts(self, *, repo: pygit2.Repository, status: dict[str, int]) -> list[str]:
        conflict_paths = [
            path
            for path, flags in status.items()
            if flags & pygit2.GIT_STATUS_CONFLICTED
        ]
        try:
            conflicts = repo.index.conflicts
        except KeyError:
            conflicts = None
        if conflicts:
            for ancestor, ours, theirs in conflicts:
                entry = ancestor or ours or theirs
                if entry:
                    conflict_paths.append(entry.path)
        return sorted(set(conflict_paths))

    def _remote_branches(self, *, repo: pygit2.Repository, aliases: _OidAliasMap) -> dict[str, str]:
        remote_branches: dict[str, str] = {}
        for reference in repo.references:
            if not reference.startswith("refs/remotes/"):
                continue
            name = reference.removeprefix("refs/remotes/")
            remote_branches[name] = aliases.alias_for_oid(repo.references[reference].target)
        return remote_branches

    def _upstream_tracking(self, *, repo: pygit2.Repository) -> dict[str, str]:
        tracking: dict[str, str] = {}
        for branch_name in repo.branches.local:
            try:
                upstream = repo.branches.local[branch_name].upstream
            except (KeyError, pygit2.GitError):
                continue
            if upstream:
                tracking[branch_name] = upstream.shorthand
        return tracking

    def _worktree_status_label(self, flags: int) -> str:
        if flags & pygit2.GIT_STATUS_WT_NEW:
            return "untracked"
        if flags & pygit2.GIT_STATUS_WT_DELETED:
            return "deleted"
        if flags & pygit2.GIT_STATUS_WT_MODIFIED:
            return "modified"
        return "updated"

    def _index_status_label(self, flags: int) -> str:
        if flags & pygit2.GIT_STATUS_INDEX_NEW:
            return "added"
        if flags & pygit2.GIT_STATUS_INDEX_DELETED:
            return "deleted"
        if flags & pygit2.GIT_STATUS_INDEX_MODIFIED:
            return "modified"
        return "updated"

    def _delta_label(self, status: str) -> str:
        if status == "A":
            return "added"
        if status == "D":
            return "deleted"
        return "modified"


class Pygit2RemoteRepositoryFactory:
    def materialize_remote(
        self,
        *,
        state: dict,
        path: str | Path,
        remote_name: str = "origin",
    ) -> str:
        state = RepositoryStateNormalizer().normalize(state)
        path = Path(path)
        if path.exists():
            shutil.rmtree(path)
        repo = pygit2.init_repository(str(path), bare=True)
        repo.config["core.autocrlf"] = "false"
        signature = pygit2.Signature("GIT it", "git-it@example.test")
        aliases_to_oids: dict[str, pygit2.Oid] = {}
        commit_files: dict[str, dict[str, str]] = {}
        materializer = Pygit2RepositoryMaterializer()

        commits = list(state.get("commits", []))
        remote_targets = sorted(
            target for target in state.get("remote_branches", {}).values() if target
        )
        for target in remote_targets:
            if target not in {commit.get("id") for commit in commits}:
                commits.append({"id": target, "message": f"Remote commit {target}", "parents": []})

        for commit in commits:
            alias = commit["id"]
            files = materializer._files_for_commit(commit=commit, commit_files=commit_files)
            tree = materializer._write_tree(repo=repo, files=files)
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
                tree,
                parents,
            )
            aliases_to_oids[alias] = oid
            commit_files[alias] = files

        refs = state.get("remote_branches", {}) or {f"{remote_name}/main": remote_targets[-1] if remote_targets else None}
        for name, alias in refs.items():
            if not name.startswith(f"{remote_name}/"):
                continue
            oid = aliases_to_oids.get(alias)
            if not oid:
                continue
            branch = name.split("/", 1)[1]
            repo.references.create(f"refs/heads/{branch}", oid, force=True)
            if branch == "main":
                repo.set_head("refs/heads/main")
        return str(path)


class _OidAliasMap:
    def __init__(self, aliases_to_oids: dict[str, pygit2.Oid]):
        self._oid_to_alias = {str(oid): alias for alias, oid in aliases_to_oids.items()}
        self._allocated = set(aliases_to_oids)

    def alias_for_oid(self, oid: pygit2.Oid | str | None) -> str | None:
        if oid is None:
            return None
        oid_text = str(oid)
        if oid_text in self._oid_to_alias:
            return self._oid_to_alias[oid_text]

        index = 0
        while f"c{index}" in self._allocated:
            index += 1
        alias = f"c{index}"
        self._allocated.add(alias)
        self._oid_to_alias[oid_text] = alias
        return alias
