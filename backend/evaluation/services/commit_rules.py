class StateCommitRuleMixin:
    def _check_commit_conditions(
        self,
        commit: dict,
        rule: dict,
        *,
        state: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        checks = [
            ("commit_message_contains", {"text": rule.get("message_contains")}),
            ("commit_changes_include", {"paths": rule.get("changes_include")}),
            ("commit_changes_exclude", {"paths": rule.get("changes_exclude")}),
            ("commit_changes_include_tokens", {"tokens": rule.get("changes_include_tokens")}),
            ("commit_changes_exclude_tokens", {"tokens": rule.get("changes_exclude_tokens")}),
            (
                "commit_tree_contains",
                {"tree": rule.get("tree_contains"), "paths": rule.get("tree_contains")},
            ),
            ("commit_tree_excludes", {"paths": rule.get("tree_excludes")}),
            ("commit_tree_contains_tokens", {"tokens": rule.get("tree_contains_tokens")}),
            ("commit_tree_excludes_tokens", {"tokens": rule.get("tree_excludes_tokens")}),
            ("commit_parent_equals", {"parent": rule.get("parent_equals")}),
            ("commit_parent_count_equals", {"count": rule.get("parent_count_equals")}),
        ]
        if "message_equals" in rule and commit.get("message") != rule.get("message_equals"):
            return False, f"Commit message was {commit.get('message')!r}."
        if rule.get("is_merge") is True and len(commit.get("parents", [])) <= 1:
            return False, "Commit is not a merge commit."
        if rule.get("is_not_merge") is True and len(commit.get("parents", [])) > 1:
            return False, "Commit is a merge commit."
        for rule_type, payload in checks:
            if all(value in (None, [], {}) for value in payload.values()):
                continue
            passed, reason = self._check_commit_rule(
                rule_type,
                commit,
                payload,
                state=state,
                initial_state=initial_state,
            )
            if not passed:
                return passed, reason
        return True, f"Commit {commit.get('id')} matched expected details."

    def _check_commit_rule(
        self,
        rule_type: str,
        commit: dict,
        rule: dict,
        *,
        state: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        if rule_type == "commit_message_contains":
            texts = self._as_list(rule.get("text") or rule.get("message_contains"))
            message = commit.get("message", "")
            missing = [text for text in texts if str(text).lower() not in message.lower()]
            return (
                not missing,
                "Commit message contains expected text."
                if not missing
                else f"Commit message did not contain {missing}.",
            )
        if rule_type == "commit_changes_include":
            paths = set(rule.get("paths") or rule.get("changes_include") or [])
            changed = set(self._changed_paths(commit))
            missing = sorted(paths - changed)
            return (
                not missing,
                "Commit changes include expected paths."
                if not missing
                else f"Commit changes were missing {missing}.",
            )
        if rule_type == "commit_changes_exclude":
            paths = set(rule.get("paths") or rule.get("changes_exclude") or [])
            changed = set(self._changed_paths(commit))
            present = sorted(paths & changed)
            return (
                not present,
                "Commit changes exclude forbidden paths."
                if not present
                else f"Commit unexpectedly changed {present}.",
            )
        if rule_type == "commit_changes_include_tokens":
            return self._token_rule_for_payload(
                commit.get("changes") or {},
                rule.get("tokens") or rule.get("changes_include_tokens") or [],
                should_contain=True,
                label="Commit changes",
            )
        if rule_type == "commit_changes_exclude_tokens":
            return self._token_rule_for_payload(
                commit.get("changes") or {},
                rule.get("tokens") or rule.get("changes_exclude_tokens") or [],
                should_contain=False,
                label="Commit changes",
            )
        if rule_type == "commit_tree_contains":
            tree = commit.get("tree") or {}
            expected_tree = rule.get("tree")
            if isinstance(expected_tree, dict):
                mismatched = [
                    path for path, value in expected_tree.items() if tree.get(path) != value
                ]
                return (
                    not mismatched,
                    "Commit tree contains expected file contents."
                    if not mismatched
                    else f"Tree mismatched paths: {mismatched}.",
                )
            paths = set(rule.get("paths") or rule.get("tree_contains") or [])
            missing = sorted(path for path in paths if path not in tree)
            return (
                not missing,
                "Commit tree contains expected paths."
                if not missing
                else f"Tree missing paths: {missing}.",
            )
        if rule_type == "commit_tree_excludes":
            tree = commit.get("tree") or {}
            paths = set(rule.get("paths") or rule.get("tree_excludes") or [])
            present = sorted(path for path in paths if path in tree)
            return (
                not present,
                "Commit tree excludes expected paths."
                if not present
                else f"Tree unexpectedly contains paths: {present}.",
            )
        if rule_type == "commit_tree_contains_tokens":
            return self._token_rule_for_payload(
                commit.get("tree") or {},
                rule.get("tokens") or rule.get("tree_contains_tokens") or [],
                should_contain=True,
                label="Commit tree",
            )
        if rule_type == "commit_tree_excludes_tokens":
            return self._token_rule_for_payload(
                commit.get("tree") or {},
                rule.get("tokens") or rule.get("tree_excludes_tokens") or [],
                should_contain=False,
                label="Commit tree",
            )
        if rule_type in {"commit_has_parent", "commit_parent_equals"}:
            parent = self._resolve_expected(
                rule.get("parent") or rule.get("parent_equals") or rule.get("expected"),
                state,
                initial_state,
            )
            passed = parent in commit.get("parents", [])
            return (
                passed,
                "Commit has expected parent."
                if passed
                else f"Commit parents were {commit.get('parents', [])}, expected {parent!r}.",
            )
        if rule_type == "commit_parent_count_equals":
            expected = int(rule.get("count", rule.get("parent_count", 0)))
            actual = len(commit.get("parents", []))
            return actual == expected, f"Commit parent count was {actual}, expected {expected}."
        if rule_type == "commit_is_merge":
            passed = len(commit.get("parents", [])) > 1
            return (
                passed,
                "Commit is a merge commit." if passed else "Commit is not a merge commit.",
            )
        if rule_type == "commit_is_not_merge":
            passed = len(commit.get("parents", [])) <= 1
            return (
                passed,
                "Commit is not a merge commit." if passed else "Commit is a merge commit.",
            )
        return False, f"Unsupported commit rule type: {rule_type!r}."

    def _check_operation_metadata(
        self, rule_type: str, state: dict, rule: dict
    ) -> tuple[bool, str]:
        key = rule.get("key")
        metadata = state.get("operation_metadata", {})
        present = key in metadata or key in state
        actual = self._operation_value(state, key)
        expected = rule.get("value")
        if rule_type == "operation_metadata_absent":
            return (
                not present,
                f"Operation metadata {key!r} {'is absent' if not present else 'is present'}.",
            )
        if rule_type == "operation_metadata_equals":
            passed = actual == expected
            return passed, f"Operation metadata {key!r} was {actual!r}, expected {expected!r}."
        if rule_type == "operation_metadata_not_equals":
            passed = actual != expected
            return passed, f"Operation metadata {key!r} was {actual!r}."
        if rule_type == "operation_metadata_contains":
            needle = rule.get("value")
            if isinstance(actual, dict) and isinstance(needle, dict):
                passed = all(
                    actual.get(item_key) == item_value for item_key, item_value in needle.items()
                )
            elif isinstance(actual, (list, tuple, set)):
                passed = needle in actual
            else:
                passed = str(needle) in str(actual)
            return passed, f"Operation metadata {key!r} was {actual!r}."
        return False, f"Unsupported operation metadata rule: {rule_type!r}."

    def _check_commit_replaced_by_amend(
        self,
        state: dict,
        rule: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        old_commit = self._resolve_expected(
            rule.get("old")
            or rule.get("replaced")
            or rule.get("commit")
            or self._operation_value(state, "last_amend_replaced_commit"),
            state,
            initial_state,
        )
        new_commit = self._resolve_expected(
            rule.get("new")
            or rule.get("created")
            or self._operation_value(state, "last_amend_created_commit"),
            state,
            initial_state,
        )
        replaced = state.get("replaced_commits", {}).get(old_commit)
        passed = bool(old_commit and new_commit and replaced == new_commit)
        return (
            passed,
            "Amend replacement metadata matched."
            if passed
            else f"Amend metadata was {old_commit!r} -> {replaced!r}, expected {new_commit!r}.",
        )

    def _check_commit_not_followed_by_extra_commit(
        self,
        state: dict,
        rule: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        branch = rule.get("branch") or self._head_branch(state)
        expected_tip = self._resolve_expected(
            rule.get("commit")
            or rule.get("tip")
            or self._operation_value(state, "last_amend_created_commit"),
            state,
            initial_state,
        )
        actual_tip = self._ref_target(state, branch)
        passed = bool(expected_tip and actual_tip == expected_tip)
        return (
            passed,
            f"Branch {branch!r} tip is {actual_tip!r}, expected amended tip {expected_tip!r}.",
        )

    def _check_branch_tip_replaces_commit(
        self,
        state: dict,
        rule: dict,
        initial_state: dict | None,
    ) -> tuple[bool, str]:
        branch = rule.get("branch") or self._head_branch(state)
        old_id = self._resolve_expected(
            rule.get("old")
            or rule.get("replaced")
            or rule.get("commit")
            or self._operation_value(state, "last_amend_replaced_commit"),
            state,
            initial_state,
        )
        tip_id = self._ref_target(state, branch)
        old_commit = self._commit_by_id(state, old_id)
        tip_commit = self._commit_by_id(state, tip_id)
        passed = bool(
            old_commit
            and tip_commit
            and tip_id != old_id
            and tip_commit.get("parents", []) == old_commit.get("parents", [])
        )
        return passed, f"Branch {branch!r} tip {tip_id!r} compared with replaced commit {old_id!r}."
