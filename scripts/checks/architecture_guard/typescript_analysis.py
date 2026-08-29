"""Pure TypeScript source-analysis helpers for architecture policies."""

from __future__ import annotations

import ast
import posixpath
import re

TS_TRIVIA = r"(?:\s|/\*(?:(?!\*/)[\s\S])*\*/|//[^\r\n]*(?:\r?\n|$))*"
TS_MODULE_SPECIFIER = re.compile(
    r"(?:\bfrom\b|\bimport\s*\(|\bimport\b|\brequire\s*\()"
    + TS_TRIVIA
    + r"(?:(?P<quote>['\"])(?P<quoted>[^'\"]+)(?P=quote)|`(?P<template>[^`$]+)`)"
)
TS_IMPORT_EXPORT_FROM = re.compile(
    r"\b(?:import|export)\b"
    + TS_TRIVIA
    + r"(?P<clause>[^'\"`;]*?)"
    + TS_TRIVIA
    + r"from\b"
    + TS_TRIVIA
    + r"(?P<quote>['\"])(?P<module>[^'\"]+)(?P=quote)",
    re.S,
)
TS_QUERY_CONSUMER_CALL = (
    r"\s*(?:[A-Za-z_$][\w$]*\s*\.\s*)?"
    r"(?:useQuery|useInfiniteQuery|useSuspenseQuery|useSuspenseInfiniteQuery|"
    r"queryOptions|infiniteQueryOptions)\s*\("
)


def ts_module_specifiers(source: str) -> list[str]:
    """Return static, aliased, side-effect, require, and dynamic TS imports."""
    return [
        match.group("quoted") or match.group("template")
        for match in TS_MODULE_SPECIFIER.finditer(source)
    ]


def canonical_ts_module_reference(*, module: str, path_label: str) -> str:
    """Resolve project aliases and relative imports to one repository path."""
    normalized_module = module.replace("\\", "/")
    normalized_path = path_label.replace("\\", "/")
    if normalized_module.startswith("@/"):
        reference = f"frontend/src/{normalized_module[2:]}"
    elif normalized_module.startswith("."):
        reference = posixpath.join(posixpath.dirname(normalized_path), normalized_module)
    else:
        return normalized_module
    reference = posixpath.normpath(reference)
    for suffix in (".tsx", ".ts", ".jsx", ".js"):
        if reference.endswith(suffix):
            return reference[: -len(suffix)]
    return reference


def ts_module_matches_boundary(module: str, boundary: str) -> bool:
    """Match a package/file boundary without matching similarly named siblings."""
    return module == boundary or module.startswith(f"{boundary}/")


def ts_clause_is_type_only(clause: str) -> bool:
    """Recognize `import type` and named `type`-only import/export clauses."""
    normalized = re.sub(r"/\*[\s\S]*?\*/|//[^\r\n]*(?:\r?\n|$)", " ", clause).strip()
    if normalized.startswith("type "):
        return True
    if not (normalized.startswith("{") and normalized.endswith("}")):
        return False
    bindings = [binding.strip() for binding in normalized[1:-1].split(",") if binding.strip()]
    return bool(bindings) and all(binding.startswith("type ") for binding in bindings)


def ts_value_module_references(source: str) -> list[str]:
    """Return runtime module references while excluding demonstrably type-only imports."""
    references: list[str] = []
    masked = list(source)
    for match in TS_IMPORT_EXPORT_FROM.finditer(source):
        if not ts_clause_is_type_only(match.group("clause")):
            references.append(match.group("module"))
        for index in range(match.start(), match.end()):
            if masked[index] not in "\r\n":
                masked[index] = " "
    references.extend(ts_module_specifiers("".join(masked)))
    return references


def destructured_function_props(source: str, function_name: str) -> list[str]:
    """Return top-level names from a named function's destructured first parameter."""
    match = re.search(
        rf"\bfunction\s+{re.escape(function_name)}\s*\(\s*\{{(?P<body>[^}}]*)\}}",
        source,
        re.S,
    )
    if not match:
        return []
    return [
        binding.split(":", 1)[0].split("=", 1)[0].strip()
        for binding in match.group("body").split(",")
        if binding.strip()
    ]


def jsx_component_props(source: str, component_name: str) -> tuple[list[str], str]:
    """Return explicit JSX prop names and a whitespace-neutral opening tag body."""
    match = re.search(rf"<{re.escape(component_name)}\b(?P<body>[^>]*)>", source, re.S)
    if not match:
        return [], ""
    body = match.group("body")
    names = re.findall(r"(?<![\w.-])([A-Za-z_$][\w$-]*)\s*=", body)
    return names, re.sub(r"\s+", "", body)


def strip_ts_comments(source: str) -> str:
    """Remove TypeScript comments before source-shape checks."""
    return re.sub(r"/\*[\s\S]*?\*/|//[^\r\n]*", "", source)


def ts_balanced_brace_body(source: str, opening_index: int) -> str | None:
    """Return a quote-aware balanced TypeScript brace body."""
    if opening_index >= len(source) or source[opening_index] != "{":
        return None
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(opening_index, len(source)):
        char = source[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'", "`"}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[opening_index + 1 : index]
    return None


def ts_object_method_body(source: str, method_name: str) -> str | None:
    """Return a quote-aware object-method body by its exact method name."""
    match = re.search(
        rf"\b{re.escape(method_name)}\s*\([^)]*\)\s*\{{",
        source,
    )
    if match is None:
        return None
    return ts_balanced_brace_body(source, match.end() - 1)


def ts_top_level_statements(body: str) -> list[str]:
    """Split a TS block on top-level newlines/semicolons without flattening literals."""
    statements: list[str] = []
    start = 0
    braces = brackets = parentheses = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(body):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'", "`"}:
            quote = char
        elif char == "{":
            braces += 1
        elif char == "}":
            braces = max(0, braces - 1)
        elif char == "[":
            brackets += 1
        elif char == "]":
            brackets = max(0, brackets - 1)
        elif char == "(":
            parentheses += 1
        elif char == ")":
            parentheses = max(0, parentheses - 1)
        elif char in {";", "\n"} and not (braces or brackets or parentheses):
            current = body[start:index].rstrip()
            following = body[index + 1 :].lstrip()
            if char == "\n" and (
                re.search(r"(?:=|=>|[?:,.+*/-]|&&|\|\|)\s*$", current)
                or re.match(r"^(?:[?:,.+*/-]|&&|\|\|)", following)
            ):
                continue
            statement = body[start:index].strip()
            if statement:
                statements.append(statement)
            start = index + 1
    tail = body[start:].strip()
    if tail:
        statements.append(tail)
    return statements


def ts_recursive_statements(body: str) -> list[str]:
    """Flatten bounded TS statements while retaining nested control-flow returns."""
    statements: list[str] = []
    for statement in ts_top_level_statements(body):
        statements.append(statement)
        opening = statement.find("{")
        while opening >= 0:
            nested_body = ts_balanced_brace_body(statement, opening)
            if nested_body is None:
                break
            statements.extend(ts_recursive_statements(nested_body))
            opening = statement.find("{", opening + len(nested_body) + 2)
    return statements


def ts_exported_type_aliases(source: str) -> dict[str, str]:
    """Return single-statement exported TypeScript aliases by name."""
    return {
        match.group("name"): match.group("body").strip()
        for match in re.finditer(
            r"\bexport\s+type\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*(?P<body>[^;\r\n]+)",
            source,
        )
    }


def ts_type_aliases(source: str) -> dict[str, str]:
    """Return all single-statement TypeScript aliases by name."""
    return {
        match.group("name"): match.group("body").strip()
        for match in re.finditer(
            r"\b(?:export\s+)?type\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*"
            r"(?P<body>[^;\r\n]+)",
            source,
        )
    }


def normalized_ts_type(value: str) -> str:
    """Normalize harmless quote/whitespace differences in a TS type expression."""
    return re.sub(r"\s+", "", value).replace('"', "'")


def ts_interface_declarations(source: str) -> dict[str, tuple[str, str]]:
    """Return interface extends clauses and balanced bodies by name."""
    declarations: dict[str, tuple[str, str]] = {}
    pattern = re.compile(
        r"\b(?:export\s+)?interface\s+(?P<name>[A-Za-z_$][\w$]*)"
        r"(?:\s+extends\s+(?P<extends>[^\{]+))?\s*\{"
    )
    for match in pattern.finditer(source):
        body = ts_balanced_brace_body(source, match.end() - 1)
        if body is not None:
            declarations[match.group("name")] = (
                (match.group("extends") or "").strip(),
                body,
            )
    return declarations


def ts_object_type_alias_bodies(source: str) -> dict[str, str]:
    """Return balanced object-literal bodies for TypeScript aliases."""
    declarations: dict[str, str] = {}
    pattern = re.compile(r"\b(?:export\s+)?type\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*\{")
    for match in pattern.finditer(source):
        body = ts_balanced_brace_body(source, match.end() - 1)
        if body is not None:
            declarations[match.group("name")] = body
    return declarations


def ts_object_type_field_names(body: str) -> frozenset[str]:
    """Return top-level property names from an interface or object type body."""
    names: set[str] = set()
    for statement in ts_top_level_statements(body):
        match = re.match(
            r"^(?:readonly\s+)?(?P<name>[A-Za-z_$][\w$]*|['\"][^'\"]+['\"])?\s*"
            r"\??\s*:",
            statement,
        )
        if match and match.group("name"):
            names.add(match.group("name").strip("'\""))
    return frozenset(names)


def strip_outer_ts_parentheses(value: str) -> str:
    """Remove balanced parentheses that wrap an entire TypeScript expression."""
    value = value.strip()
    while value.startswith("(") and value.endswith(")"):
        depth = 0
        wraps_entire_value = True
        for index, char in enumerate(value):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0 and index != len(value) - 1:
                    wraps_entire_value = False
                    break
        if not wraps_entire_value or depth != 0:
            break
        value = value[1:-1].strip()
    return value


def normalized_ts_module_reference(path_label: str, module: str) -> str:
    """Resolve alias/relative TS module references to a suffix-free repo path."""
    if module.startswith("@/"):
        resolved = posixpath.join("frontend/src", module[2:])
    elif module.startswith("."):
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path_label), module))
    else:
        resolved = module
    return re.sub(r"\.(?:tsx?|jsx?)$", "", resolved)


def ts_module_matches(
    *,
    path_label: str,
    module: str,
    canonical_module: str,
) -> bool:
    """Match canonical TS imports across aliases and relative specifiers."""
    return normalized_ts_module_reference(path_label, module) == normalized_ts_module_reference(
        path_label, canonical_module
    )


def ts_named_import_bindings(
    source: str,
    *,
    path_label: str,
    module: str,
    exported_names: set[str],
) -> set[str]:
    """Resolve local names for selected named imports from one module."""
    bindings: set[str] = set()
    for match in TS_IMPORT_EXPORT_FROM.finditer(source):
        if not ts_module_matches(
            path_label=path_label,
            module=match.group("module"),
            canonical_module=module,
        ) or not match.group(0).lstrip().startswith("import"):
            continue
        clause = re.sub(r"^type\s+", "", match.group("clause").strip())
        if not clause.startswith("{"):
            continue
        for item in clause.strip("{} ").split(","):
            parts = re.split(r"\s+as\s+", re.sub(r"^type\s+", "", item.strip()))
            if parts and parts[0].strip() in exported_names:
                bindings.add(parts[-1].strip())
    return bindings


def ts_namespace_import_bindings(
    source: str,
    *,
    path_label: str,
    module: str,
) -> set[str]:
    """Resolve `import * as name` bindings from one canonical TS module."""
    bindings: set[str] = set()
    for match in TS_IMPORT_EXPORT_FROM.finditer(source):
        if not ts_module_matches(
            path_label=path_label,
            module=match.group("module"),
            canonical_module=module,
        ) or not match.group(0).lstrip().startswith("import"):
            continue
        namespace = re.fullmatch(
            r"\*\s+as\s+([A-Za-z_$][\w$]*)",
            match.group("clause").strip(),
        )
        if namespace:
            bindings.add(namespace.group(1))
    return bindings


def ts_reexports_all_from_module(
    source: str,
    *,
    path_label: str,
    module: str,
) -> bool:
    """Report an `export *` from one canonical TS module."""
    return any(
        ts_module_matches(
            path_label=path_label,
            module=match.group("module"),
            canonical_module=module,
        )
        and match.group(0).lstrip().startswith("export")
        and match.group("clause").strip() == "*"
        for match in TS_IMPORT_EXPORT_FROM.finditer(source)
    )


def ts_reexports_named_binding(
    source: str,
    *,
    path_label: str,
    module: str,
    exported_names: set[str],
) -> bool:
    """Report a selected named re-export from one canonical module."""
    for match in TS_IMPORT_EXPORT_FROM.finditer(source):
        if not ts_module_matches(
            path_label=path_label,
            module=match.group("module"),
            canonical_module=module,
        ) or not match.group(0).lstrip().startswith("export"):
            continue
        clause = re.sub(r"^type\s+", "", match.group("clause").strip())
        if not clause.startswith("{"):
            continue
        for item in clause.strip("{} ").split(","):
            origin = re.split(r"\s+as\s+", item.strip())[0].strip()
            if origin in exported_names:
                return True
    return False


def ts_member_access_aliases(
    source: str,
    *,
    object_bindings: set[str],
    member_names: set[str],
) -> tuple[list[str], set[str]]:
    """Resolve bounded const/destructuring aliases for selected object members."""
    objects = set(object_bindings)
    callables: set[str] = set()
    member = "|".join(re.escape(item) for item in sorted(member_names))
    assignments = [
        (match.group("name"), match.group("expression").strip())
        for match in re.finditer(
            r"\b(?:export\s+)?const\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*"
            r"(?P<expression>[^;\r\n]+)",
            source,
        )
    ]
    changed = True
    while changed:
        changed = False
        for name, expression in assignments:
            normalized = normalized_ts_type(expression)
            if normalized in objects and name not in objects:
                objects.add(name)
                changed = True
                continue
            if normalized in callables and name not in callables:
                callables.add(name)
                changed = True
                continue
            for binding in objects:
                escaped = re.escape(binding)
                member = "|".join(re.escape(item) for item in sorted(member_names))
                if (
                    re.fullmatch(
                        rf"{escaped}(?:\.(?:{member})|\['(?:{member})'\])",
                        normalized,
                    )
                    and name not in callables
                ):
                    callables.add(name)
                    changed = True
            arrow = re.match(
                r"\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*"
                r"(?P<body>[\s\S]+)$",
                expression,
            )
            if arrow and name not in callables:
                body = arrow.group("body")
                access_patterns = [
                    rf"\b{re.escape(binding)}\s*(?:\.\s*(?:{member})|"
                    rf"\[\s*['\"](?:{member})['\"]\s*\])"
                    for binding in objects
                ]
                access_patterns.extend(rf"\b{re.escape(binding)}\b" for binding in callables)
                access_call = (
                    "(?:" + "|".join(access_patterns) + r")\s*\(" if access_patterns else r"(?!)"
                )
                if re.search(access_call, body) and not re.match(TS_QUERY_CONSUMER_CALL, body):
                    callables.add(name)
                    changed = True
        for binding in tuple(objects):
            for match in re.finditer(
                rf"\b(?:const|let|var)\s*\{{(?P<body>[^}}]*)\}}\s*=\s*"
                rf"{re.escape(binding)}\b",
                source,
            ):
                for item in match.group("body").split(","):
                    parts = item.strip().split(":", 1)
                    origin = parts[0].strip()
                    local = parts[-1].strip()
                    if origin in member_names and local not in callables:
                        callables.add(local)
                        changed = True
    access_patterns = [
        rf"\b{re.escape(binding)}\s*(?:\.\s*(?:{member})|"
        rf"\[\s*['\"](?:{member})['\"]\s*\])"
        for binding in sorted(objects)
    ]
    access_patterns.extend(rf"\b{re.escape(binding)}\b" for binding in sorted(callables))
    return access_patterns, objects | callables


def ts_exports_tainted_binding(source: str, tainted_names: set[str]) -> bool:
    """Report direct exported declarations or export lists for tainted aliases."""
    declared = set(
        re.findall(
            r"\bexport\s+const\s+([A-Za-z_$][\w$]*)\s*=",
            source,
        )
    )
    if declared & tainted_names:
        return True
    default_binding = re.search(
        r"\bexport\s+default\s+(?P<name>[A-Za-z_$][\w$]*)\s*;?",
        source,
    )
    if default_binding and default_binding.group("name") in tainted_names:
        return True
    for match in re.finditer(r"\bexport\s*\{(?P<body>[^}]*)\}", source):
        origins = {
            re.split(r"\s+as\s+", item.strip())[0].strip()
            for item in match.group("body").split(",")
        }
        if origins & tainted_names:
            return True
    return False


def ts_exported_adapter_uses_access(source: str, access_patterns: list[str]) -> bool:
    """Detect exported wrappers or API objects derived from a canonical access."""
    if not access_patterns:
        return False
    access = "(?:" + "|".join(access_patterns) + ")"
    access_call = rf"{access}\s*\("
    if re.search(rf"\bexport\s+default\s+{access}(?:\s*\([^;\r\n]*\))?", source):
        return True
    for match in re.finditer(
        r"\bexport\s+default\s+(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*(?!\{)"
        r"(?P<expression>[^;\r\n]+)",
        source,
    ):
        expression = match.group("expression")
        if re.search(access_call, expression) and not re.match(TS_QUERY_CONSUMER_CALL, expression):
            return True
    if re.search(
        rf"\bexport\s+const\s+\w+\s*=\s*(?:(?:async\s*)?"
        rf"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*(?:await\s+)?)?"
        rf"{access}(?:\s*\([^;\r\n]*\))?\s*;?",
        source,
        re.S,
    ):
        return True
    exported_bodies: list[str] = []
    for pattern in (
        r"\bexport\s+(?:async\s+)?function\s+\w+\s*\([^)]*\)\s*\{",
        r"\bexport\s+default\s+(?:async\s+)?function(?:\s+\w+)?\s*"
        r"\([^)]*\)\s*\{",
        r"\bexport\s+const\s+\w+\s*=\s*(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*\{",
    ):
        for match in re.finditer(pattern, source):
            body = ts_balanced_brace_body(source, match.end() - 1)
            if body is not None:
                exported_bodies.append(body)
    for body in exported_bodies:
        assignments: list[tuple[str, str]] = []
        returns: list[str] = []
        for statement in ts_recursive_statements(body):
            assignment = re.match(
                r"^(?:(?:const|let|var)\s+(?P<declared>[A-Za-z_$][\w$]*)"
                r"(?:\s*:[^=]+)?|(?P<assigned>[A-Za-z_$][\w$]*))"
                r"\s*=\s*(?P<expression>[\s\S]+)$",
                statement,
            )
            if assignment:
                assignments.append(
                    (
                        assignment.group("declared") or assignment.group("assigned"),
                        assignment.group("expression"),
                    )
                )
            returned = re.match(r"^return\b(?P<expression>[\s\S]*)$", statement)
            if returned:
                returns.append(returned.group("expression"))
        tainted_names: set[str] = set()
        changed = True
        while changed:
            changed = False
            for name, expression in assignments:
                query_consumer = re.match(TS_QUERY_CONSUMER_CALL, expression)
                uses_tainted_name = any(
                    re.search(rf"\b{re.escape(tainted)}\b", expression) for tainted in tainted_names
                )
                if name not in tainted_names and (
                    (re.search(access_call, expression) and not query_consumer) or uses_tainted_name
                ):
                    tainted_names.add(name)
                    changed = True
        if any(
            (
                re.search(access_call, expression)
                and not re.match(TS_QUERY_CONSUMER_CALL, expression)
            )
            or any(re.search(rf"\b{re.escape(tainted)}\b", expression) for tainted in tainted_names)
            for expression in returns
        ):
            return True
    for match in re.finditer(
        r"\bexport\s+const\s+\w+\s*=\s*(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*(?!\{)"
        r"(?P<expression>[^;\r\n]+)",
        source,
    ):
        expression = match.group("expression")
        if re.search(access_call, expression) and not re.match(TS_QUERY_CONSUMER_CALL, expression):
            return True
    for match in re.finditer(r"\bexport\s+const\s+\w+\s*=\s*\{", source):
        body = ts_balanced_brace_body(source, match.end() - 1)
        if body is not None and re.search(access, body):
            return True
    return False


def ts_response_forwarding_bindings(
    source: str,
    access_patterns: list[str],
) -> set[str]:
    """Return top-level bindings that directly forward a canonical response."""
    if not access_patterns:
        return set()
    access = "(?:" + "|".join(access_patterns) + ")"
    direct_access = rf"{access}"
    direct_call = rf"^(?:await)?{access}\s*\("

    def body_forwards_response(body: str) -> bool:
        tainted_names: set[str] = set()
        for statement in ts_top_level_statements(body):
            assignment = re.match(
                r"^(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)"
                r"(?:\s*:[^=]+)?\s*=\s*(?P<expression>[\s\S]+)$",
                statement,
            )
            if assignment:
                expression = normalized_ts_type(assignment.group("expression"))
                if re.match(direct_call, expression) or expression in tainted_names:
                    tainted_names.add(assignment.group("name"))
                continue
            returned = re.match(r"^return\b(?P<expression>[\s\S]*)$", statement)
            if returned:
                expression = normalized_ts_type(returned.group("expression"))
                if re.match(direct_call, expression) or expression in tainted_names:
                    return True
        return False

    bindings = {
        match.group("name")
        for match in re.finditer(
            r"\bconst\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*"
            rf"{direct_access}\s*;?",
            source,
        )
    }
    bindings.update(
        match.group("name")
        for match in re.finditer(
            r"\bconst\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*"
            r"(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*"
            rf"(?:await\s+)?{access}\s*\(",
            source,
            re.S,
        )
    )
    for pattern in (
        r"\bconst\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*\{",
        r"\b(?:async\s+)?function\s+(?P<name>[A-Za-z_$][\w$]*)\s*"
        r"\([^)]*\)\s*\{",
    ):
        for match in re.finditer(pattern, source):
            body = ts_balanced_brace_body(source, match.end() - 1)
            if body is not None and body_forwards_response(body):
                bindings.add(match.group("name"))
    return bindings


def ts_exported_top_level_adapter_uses_access(
    source: str,
    access_patterns: list[str],
) -> bool:
    """Detect exported adapters without treating nested UI callbacks as adapters."""
    if not access_patterns:
        return False
    access = "(?:" + "|".join(access_patterns) + ")"
    direct_call = rf"^(?:await)?{access}\s*\("

    def body_returns_adapter(body: str) -> bool:
        tainted_names: set[str] = set()
        for statement in ts_top_level_statements(body):
            assignment = re.match(
                r"^(?:(?:const|let|var)\s+(?P<declared>[A-Za-z_$][\w$]*)"
                r"(?:\s*:[^=]+)?|(?P<assigned>[A-Za-z_$][\w$]*))"
                r"\s*=\s*(?P<expression>[\s\S]+)$",
                statement,
            )
            if assignment:
                name = assignment.group("declared") or assignment.group("assigned")
                expression = normalized_ts_type(assignment.group("expression"))
                if re.match(direct_call, expression) or expression in tainted_names:
                    tainted_names.add(name)
                continue
            returned = re.match(r"^return\b(?P<expression>[\s\S]*)$", statement)
            if returned:
                expression = normalized_ts_type(returned.group("expression"))
                if (
                    re.match(direct_call, expression)
                    or expression in tainted_names
                    or expression.startswith("{")
                    and re.search(access, expression)
                ):
                    return True
        return False

    adapter_bindings = {
        match.group("name")
        for match in re.finditer(
            r"\bconst\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*"
            r"(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*"
            rf"(?:await\s+)?{access}\s*\(",
            source,
            re.S,
        )
    }
    for match in re.finditer(
        r"\bconst\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*\{",
        source,
    ):
        body = ts_balanced_brace_body(source, match.end() - 1)
        if body is not None and re.search(access, body):
            adapter_bindings.add(match.group("name"))
    for match in re.finditer(
        r"\bconst\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*\(\s*\{",
        source,
    ):
        body = ts_balanced_brace_body(source, match.end() - 1)
        if body is not None and re.search(access, body):
            adapter_bindings.add(match.group("name"))
    for match in re.finditer(
        r"\bconst\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*\{",
        source,
    ):
        body = ts_balanced_brace_body(source, match.end() - 1)
        if body is not None and body_returns_adapter(body):
            adapter_bindings.add(match.group("name"))
    adapter_bindings.update(ts_response_forwarding_bindings(source, access_patterns))
    if ts_exports_tainted_binding(source, adapter_bindings):
        return True
    if re.search(
        r"\bexport\s+default\s+(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*"
        rf"(?:await\s+)?{access}\s*\(",
        source,
        re.S,
    ):
        return True
    for match in re.finditer(
        r"\bexport\s+default\s+(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*\(\s*\{",
        source,
    ):
        body = ts_balanced_brace_body(source, match.end() - 1)
        if body is not None and re.search(access, body):
            return True
    bodies: list[str] = []
    for pattern in (
        r"\bexport\s+(?:async\s+)?function\s+\w+\s*\([^)]*\)\s*\{",
        r"\bexport\s+default\s+(?:async\s+)?function(?:\s+\w+)?\s*"
        r"\([^)]*\)\s*\{",
        r"\bexport\s+const\s+\w+\s*=\s*(?:async\s*)?"
        r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*\{",
    ):
        for match in re.finditer(pattern, source):
            body = ts_balanced_brace_body(source, match.end() - 1)
            if body is not None:
                bodies.append(body)
    for body in bodies:
        if body_returns_adapter(body):
            return True
    return False


def resolve_ts_static_string_expression(
    expression: str,
    bindings: dict[str, str],
) -> str | None:
    """Resolve a bounded TS expression made from static strings, names, and `+`."""
    template = re.fullmatch(r"\s*`(?P<body>[^`]*)`\s*", expression)
    if template:
        unresolved = False

        def replace_binding(match: re.Match[str]) -> str:
            nonlocal unresolved
            name = match.group("name")
            if name not in bindings:
                unresolved = True
                return ""
            return bindings[name]

        value = re.sub(
            r"\$\{(?P<name>[A-Za-z_$][\w$]*)\}",
            replace_binding,
            template.group("body"),
        )
        if unresolved or "${" in value:
            return None
        return value
    token = r"(?:'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`[^`$]*`|[A-Za-z_$][\w$]*)"
    if not re.fullmatch(rf"\s*{token}(?:\s*\+\s*{token})*\s*", expression):
        return None
    values: list[str] = []
    for item in re.findall(token, expression):
        if item.startswith("`"):
            values.append(item[1:-1])
        elif item.startswith(("'", '"')):
            try:
                values.append(ast.literal_eval(item))
            except (SyntaxError, ValueError):
                return None
        elif item in bindings:
            values.append(bindings[item])
        else:
            return None
    return "".join(values)


def ts_static_string_bindings(source: str) -> dict[str, str]:
    """Resolve bounded const/let/var string bindings to a fixed point."""
    assignments = [
        (match.group("name"), match.group("expression").strip())
        for match in re.finditer(
            r"\b(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*"
            r"(?P<expression>[^;\r\n]+)",
            source,
        )
    ]
    bindings: dict[str, str] = {}
    changed = True
    while changed:
        changed = False
        for name, expression in assignments:
            value = resolve_ts_static_string_expression(expression, bindings)
            if value is not None and bindings.get(name) != value:
                bindings[name] = value
                changed = True
    return bindings
