class StatePayloadRuleMixin:
    def _token_rule_for_entries(
        self,
        entries: dict,
        rule: dict,
        *,
        should_contain: bool,
        label: str,
    ) -> tuple[bool, str]:
        path_map = rule.get("paths")
        if isinstance(path_map, dict):
            for path, tokens in path_map.items():
                missing = self._missing_tokens(entries.get(path), self._as_list(tokens))
                if should_contain and missing:
                    return False, f"{label} entry {path!r} is missing tokens {missing}."
                if not should_contain and len(missing) != len(self._as_list(tokens)):
                    present = sorted(set(map(str, self._as_list(tokens))) - set(missing))
                    return False, f"{label} entry {path!r} still contains tokens {present}."
            return True, f"{label} token rule matched."
        return self._token_rule_for_payload(
            entries,
            rule.get("tokens", []),
            should_contain=should_contain,
            label=label,
        )

    def _token_rule_for_payload(
        self,
        payload: object,
        tokens: object,
        *,
        should_contain: bool,
        label: str,
    ) -> tuple[bool, str]:
        token_list = self._as_list(tokens)
        missing = self._missing_tokens(payload, token_list)
        if should_contain:
            return (
                not missing,
                f"{label} contains expected tokens."
                if not missing
                else f"{label} is missing tokens {missing}.",
            )
        present = sorted(set(map(str, token_list)) - set(missing))
        return (
            not present,
            f"{label} excludes expected tokens."
            if not present
            else f"{label} still contains tokens {present}.",
        )

    def _path_token_map_rule(
        self, entries: dict, path_map: dict, *, label: str
    ) -> tuple[bool, str]:
        for path, tokens in (path_map or {}).items():
            missing = self._missing_tokens(entries.get(path), self._as_list(tokens))
            if missing:
                return False, f"{label} for {path!r} is missing tokens {missing}."
        return True, f"{label} matched expected tokens."

    def _missing_tokens(self, payload: object, tokens: list) -> list[str]:
        haystack = self.normalizer.token_haystack(payload).lower()
        return [str(token) for token in tokens if str(token).lower() not in haystack]
