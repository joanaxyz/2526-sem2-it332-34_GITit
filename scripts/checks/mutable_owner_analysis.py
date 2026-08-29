#!/usr/bin/env python3
"""Reusable lexical and mutable-owner analysis for Python syntax trees."""

from __future__ import annotations

import ast
from collections.abc import Callable

MUTATING_METHODS = frozenset(
    {
        "__delitem__",
        "__iadd__",
        "__imul__",
        "__init__",
        "__ior__",
        "__setitem__",
        "append",
        "add",
        "clear",
        "difference_update",
        "discard",
        "extend",
        "insert",
        "intersection_update",
        "pop",
        "popitem",
        "remove",
        "reverse",
        "setdefault",
        "sort",
        "symmetric_difference_update",
        "update",
    }
)

MUTATING_OPERATOR_FUNCTIONS = frozenset({"delitem", "iadd", "iconcat", "imul", "ior", "setitem"})

READ_ONLY_PARAMETER_METHODS = frozenset(
    {
        "casefold",
        "endswith",
        "get",
        "items",
        "lower",
        "split",
        "startswith",
        "strip",
    }
)

IMMUTABLE_LITERAL_READ_ONLY_METHODS = frozenset({"join"})

OWNER_ALIAS_RETURN_METHODS = frozenset(
    {"__iadd__", "__imul__", "__ior__", "get", "pop", "setdefault"}
)


def _literal_immutable_value(node: ast.AST | None) -> bool:
    if isinstance(node, ast.Constant):
        return isinstance(node.value, (bool, bytes, float, int, str, type(None)))
    if isinstance(node, ast.Tuple):
        return all(_literal_immutable_value(element) for element in node.elts)
    if isinstance(node, ast.Dict):
        return all(_literal_immutable_value(item) for item in [*node.keys, *node.values])
    return False


def _root_name(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Attribute, ast.Subscript)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


class _ScopeBindingCollector(ast.NodeVisitor):
    """Collect bindings in one executable scope without entering nested scopes."""

    def __init__(self) -> None:
        self.bindings: dict[str, list[str]] = {}

    def _record(self, name: str | None, kind: str) -> None:
        if name:
            self.bindings.setdefault(name, []).append(kind)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self._record(node.id, "store")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record(node.name, "function")
        self._visit_outer_scope_expressions(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record(node.name, "function")
        self._visit_outer_scope_expressions(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._record(node.name, "class")
        for expression in [*node.decorator_list, *node.bases]:
            self.visit(expression)
        for keyword in node.keywords:
            self.visit(keyword.value)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for expression in [*node.args.defaults, *node.args.kw_defaults]:
            if expression is not None:
                self.visit(expression)

    def _visit_outer_scope_expressions(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        for expression in [
            *node.decorator_list,
            *node.args.defaults,
            *node.args.kw_defaults,
        ]:
            if expression is not None:
                self.visit(expression)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._record(alias.asname or alias.name.split(".")[0], "import")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            self._record(alias.asname or alias.name, "import")

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._record(node.name, "except")
        for statement in node.body:
            self.visit(statement)

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        self._record(node.name, "match")
        if node.pattern is not None:
            self.visit(node.pattern)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        self._record(node.name, "match")

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        self._record(node.rest, "match")
        for pattern in node.patterns:
            self.visit(pattern)


def _scope_bindings(statements: list[ast.stmt]) -> dict[str, list[str]]:
    collector = _ScopeBindingCollector()
    for statement in statements:
        collector.visit(statement)
    return {name: sorted(kinds) for name, kinds in collector.bindings.items()}


def _derived_from_owner(
    node: ast.AST | None,
    *,
    symbol: str,
    aliases: set[str],
) -> bool:
    if node is None:
        return False
    if isinstance(node, ast.Name):
        return node.id in aliases
    if isinstance(node, ast.Attribute):
        return node.attr == symbol or _derived_from_owner(
            node.value,
            symbol=symbol,
            aliases=aliases,
        )
    if isinstance(node, ast.Subscript):
        return _derived_from_owner(node.value, symbol=symbol, aliases=aliases)
    if isinstance(node, ast.Call):
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in {"copy", "get", "items", "keys", "values"}
            and _derived_from_owner(
                node.func.value,
                symbol=symbol,
                aliases=aliases,
            )
        ):
            return True
        if isinstance(node.func, ast.Name) and node.func.id in {
            "dict",
            "iter",
            "list",
            "next",
            "set",
            "tuple",
        }:
            return any(
                _derived_from_owner(argument, symbol=symbol, aliases=aliases)
                for argument in node.args
            )
        return False
    if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
        return any(
            _derived_from_owner(element, symbol=symbol, aliases=aliases) for element in node.elts
        )
    if isinstance(node, ast.Dict):
        return any(
            _derived_from_owner(item, symbol=symbol, aliases=aliases)
            for item in [*node.keys, *node.values]
        )
    if isinstance(node, ast.IfExp):
        return _derived_from_owner(
            node.body,
            symbol=symbol,
            aliases=aliases,
        ) or _derived_from_owner(
            node.orelse,
            symbol=symbol,
            aliases=aliases,
        )
    if isinstance(node, ast.BinOp):
        return _derived_from_owner(
            node.left,
            symbol=symbol,
            aliases=aliases,
        ) or _derived_from_owner(
            node.right,
            symbol=symbol,
            aliases=aliases,
        )
    return False


def _richly_derived_from_owner(
    node: ast.AST | None,
    *,
    symbol: str,
    aliases: set[str],
) -> bool:
    if _derived_from_owner(node, symbol=symbol, aliases=aliases):
        return True
    if node is None:
        return False
    if isinstance(node, ast.Starred):
        return _richly_derived_from_owner(
            node.value,
            symbol=symbol,
            aliases=aliases,
        )
    if isinstance(node, ast.BoolOp):
        return any(
            _richly_derived_from_owner(value, symbol=symbol, aliases=aliases)
            for value in node.values
        )
    if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
        return any(
            _richly_derived_from_owner(element, symbol=symbol, aliases=aliases)
            for element in node.elts
        )
    if isinstance(node, ast.Dict):
        return any(
            _richly_derived_from_owner(item, symbol=symbol, aliases=aliases)
            for item in [*node.keys, *node.values]
        )
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
        return _richly_derived_from_owner(
            node.elt,
            symbol=symbol,
            aliases=aliases,
        ) or any(
            _richly_derived_from_owner(item.iter, symbol=symbol, aliases=aliases)
            for item in node.generators
        )
    if isinstance(node, ast.DictComp):
        return any(
            _richly_derived_from_owner(item, symbol=symbol, aliases=aliases)
            for item in (node.key, node.value)
        ) or any(
            _richly_derived_from_owner(item.iter, symbol=symbol, aliases=aliases)
            for item in node.generators
        )
    if isinstance(node, ast.Call):
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "copy"
            and node.func.attr == "deepcopy"
        ):
            return False
        return any(
            _richly_derived_from_owner(argument, symbol=symbol, aliases=aliases)
            for argument in [*node.args, *[item.value for item in node.keywords]]
        )
    return False


def _bound_target_names(target: ast.AST) -> list[str]:
    """Return simple names bound by an assignment, loop, or comprehension target."""

    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, ast.Starred):
        return _bound_target_names(target.value)
    if isinstance(target, (ast.List, ast.Tuple)):
        return [name for item in target.elts for name in _bound_target_names(item)]
    return []


def _assignment_sink_targets(target: ast.AST) -> list[ast.AST]:
    """Return attribute/subscript sinks nested in an assignment target."""

    if isinstance(target, (ast.Attribute, ast.Subscript)):
        return [target]
    if isinstance(target, ast.Starred):
        return _assignment_sink_targets(target.value)
    if isinstance(target, (ast.List, ast.Tuple)):
        return [sink for item in target.elts for sink in _assignment_sink_targets(item)]
    return []


def _assignment_sink_bindings(
    target: ast.AST,
    value: ast.AST | None,
) -> list[tuple[ast.AST, ast.AST | None]]:
    """Pair nested assignment sinks with their matching destructured values."""

    if (
        isinstance(target, (ast.List, ast.Tuple))
        and isinstance(value, (ast.List, ast.Tuple))
        and len(target.elts) == len(value.elts)
    ):
        return [
            binding
            for target_item, value_item in zip(
                target.elts,
                value.elts,
                strict=True,
            )
            for binding in _assignment_sink_bindings(target_item, value_item)
        ]
    return [(sink, value) for sink in _assignment_sink_targets(target)]


def _statement_bound_names(node: ast.AST) -> set[str]:
    """Return names introduced by non-assignment binding statements."""

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, (ast.With, ast.AsyncWith)):
        return {
            name
            for item in node.items
            if item.optional_vars is not None
            for name in _bound_target_names(item.optional_vars)
        }
    if isinstance(node, ast.ExceptHandler):
        return {node.name} if node.name is not None else set()
    if isinstance(node, ast.match_case):
        return _pattern_bound_names(node.pattern)
    return set()


def _import_bound_names(node: ast.Import | ast.ImportFrom) -> set[str]:
    """Return names introduced by an import, preserving wildcard uncertainty."""

    if isinstance(node, ast.Import):
        return {item.asname or item.name.split(".")[0] for item in node.names}
    return {item.asname or item.name for item in node.names}


def _pattern_bound_names(pattern: ast.pattern) -> set[str]:
    """Return every local name introduced by a structural-match pattern."""

    names = {
        node.name
        for node in ast.walk(pattern)
        if isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name is not None
    }
    names.update(
        node.rest
        for node in ast.walk(pattern)
        if isinstance(node, ast.MatchMapping) and node.rest is not None
    )
    return names


def _assignment_targets(node: ast.AST) -> list[ast.AST]:
    """Normalize targets for assignment-like AST nodes."""

    if isinstance(node, ast.Assign):
        return node.targets
    if isinstance(node, (ast.AnnAssign, ast.NamedExpr)):
        return [node.target]
    if isinstance(node, ast.TypeAlias):
        return [node.name]
    if isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
        return [node.target]
    return []


def _name_access_counts(tree: ast.AST) -> tuple[dict[str, int], dict[str, int]]:
    """Count stores and non-store uses once for an ownership analysis."""

    store_counts: dict[str, int] = {}
    load_counts: dict[str, int] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Name):
            continue
        counts = store_counts if isinstance(node.ctx, ast.Store) else load_counts
        counts[node.id] = counts.get(node.id, 0) + 1
    return store_counts, load_counts


def _local_binding_names(tree: ast.AST, store_counts: dict[str, int]) -> set[str]:
    """Collect local names that can shadow builtins or trusted modules."""

    names = set(store_counts)
    names.update(node.arg for node in ast.walk(tree) if isinstance(node, ast.arg))
    names.update(
        item.asname or item.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for item in node.names
    )
    names.update(name for node in ast.walk(tree) for name in _statement_bound_names(node))
    return names


class _LexicalBindings:
    """Resolve binding scopes and unshadowed namespace builtins for AST policy checks."""

    _SCOPE_TYPES = (
        ast.Module,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.Lambda,
        ast.ClassDef,
    )

    def __init__(self, tree: ast.AST) -> None:
        self.tree = tree
        self.parents = {
            child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)
        }
        self._binding_cache: dict[ast.AST, set[str]] = {}
        self._namespace_capabilities: dict[tuple[ast.AST, str], set[int]] = {}
        self._namespace_container_values: dict[tuple[ast.AST, str], set[int]] = {}
        self._local_functions = {
            (self.scope(node), node.name): node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self._functools_aliases = {
            item.asname or item.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for item in node.names
            if item.name == "functools"
        }
        self._partial_aliases = {
            item.asname or item.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module == "functools"
            for item in node.names
            if item.name == "partial"
        }
        self._sys_aliases = {
            item.asname or item.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for item in node.names
            if item.name == "sys"
        }

    def scope(self, node: ast.AST) -> ast.AST:
        current = node
        while current in self.parents:
            current = self.parents[current]
            if isinstance(current, self._SCOPE_TYPES):
                return current
        return self.tree

    def parent_scope(self, scope: ast.AST) -> ast.AST | None:
        current = scope
        while current in self.parents:
            current = self.parents[current]
            if isinstance(current, self._SCOPE_TYPES):
                return current
        return None

    def binding_names(self, scope: ast.AST) -> set[str]:
        cached = self._binding_cache.get(scope)
        if cached is not None:
            return cached
        if isinstance(scope, ast.Lambda):
            names = {
                node.id
                for node in ast.walk(scope.body)
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
            }
        else:
            names = set(_scope_bindings(scope.body))
        if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            names.update(parameter.arg for parameter in _function_parameters(scope))
        self._binding_cache[scope] = names
        return names

    def builtin_is_unshadowed(self, node: ast.AST, name: str) -> bool:
        scope: ast.AST | None = self.scope(node)
        while scope is not None:
            if name in self.binding_names(scope):
                return False
            parent = self.parent_scope(scope)
            if isinstance(
                scope,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda),
            ) and isinstance(parent, ast.ClassDef):
                parent = self.parent_scope(parent)
            scope = parent
        return True

    def scope_rebinds_outer_name(self, scope: ast.AST, symbol: str) -> bool:
        return any(
            isinstance(node, (ast.Global, ast.Nonlocal))
            and symbol in node.names
            and self.scope(node) is scope
            for node in ast.walk(scope)
        )

    def _scope_declares(
        self,
        scope: ast.AST,
        declaration: type[ast.Global] | type[ast.Nonlocal],
        name: str,
    ) -> bool:
        return any(
            isinstance(node, declaration) and name in node.names and self.scope(node) is scope
            for node in ast.walk(scope)
        )

    def _module_scope(self) -> ast.AST:
        scope = self.tree
        while (parent := self.parent_scope(scope)) is not None:
            scope = parent
        return scope

    def _store_scope(self, node: ast.AST, name: str) -> ast.AST:
        scope = self.scope(node)
        if self._scope_declares(scope, ast.Global, name):
            return self._module_scope()
        if self._scope_declares(scope, ast.Nonlocal, name):
            parent = self.parent_scope(scope)
            while parent is not None:
                if name in self.binding_names(parent):
                    return parent
                parent = self.parent_scope(parent)
        return scope

    def _name_namespace_depths(self, node: ast.Name) -> set[int]:
        return self._resolved_name_depths(node, self._namespace_capabilities)

    def _resolved_name_depths(
        self,
        node: ast.Name,
        bindings: dict[tuple[ast.AST, str], set[int]],
    ) -> set[int]:
        scope: ast.AST | None = self.scope(node)
        while scope is not None:
            if depths := bindings.get((scope, node.id)):
                return set(depths)
            if node.id in self.binding_names(scope):
                return set()
            parent = self.parent_scope(scope)
            if isinstance(
                scope,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda),
            ) and isinstance(parent, ast.ClassDef):
                parent = self.parent_scope(parent)
            scope = parent
        return set()

    def namespace_container_depths(self, node: ast.AST | None) -> set[int]:
        if isinstance(node, ast.Name):
            return self._resolved_name_depths(node, self._namespace_container_values)
        if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
            return set().union(*(self.namespace_depths(item) for item in node.elts))
        if isinstance(node, ast.Dict):
            return set().union(
                *(
                    self.namespace_depths(item)
                    for item in [*node.keys, *node.values]
                    if item is not None
                )
            )
        if isinstance(node, (ast.Await, ast.NamedExpr, ast.Starred)):
            return self.namespace_container_depths(node.value)
        if isinstance(node, ast.IfExp):
            return self.namespace_container_depths(node.body) | self.namespace_container_depths(
                node.orelse
            )
        if isinstance(node, ast.BoolOp):
            return set().union(*(self.namespace_container_depths(value) for value in node.values))
        return set()

    def _resolved_local_function(
        self,
        node: ast.AST | None,
    ) -> ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda | None:
        if isinstance(node, ast.Lambda):
            return node
        if not isinstance(node, ast.Name):
            return None
        scope: ast.AST | None = self.scope(node)
        while scope is not None:
            if function := self._local_functions.get((scope, node.id)):
                return function
            if node.id in self.binding_names(scope):
                return None
            parent = self.parent_scope(scope)
            if isinstance(
                scope,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda),
            ) and isinstance(parent, ast.ClassDef):
                parent = self.parent_scope(parent)
            scope = parent
        return None

    def _partial_application(
        self,
        node: ast.Call,
    ) -> (
        tuple[
            ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda,
            list[ast.AST],
            list[ast.keyword],
        ]
        | None
    ):
        is_partial = (
            isinstance(node.func, ast.Name) and node.func.id in self._partial_aliases
        ) or (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in self._functools_aliases
            and node.func.attr == "partial"
        )
        if not is_partial or not node.args:
            return None
        function = self._resolved_local_function(node.args[0])
        if function is None:
            return None
        return function, list(node.args[1:]), list(node.keywords)

    def namespace_depths(self, node: ast.AST | None) -> set[int]:
        if isinstance(node, ast.Name):
            return self._name_namespace_depths(node)
        if self.current_module_object(node):
            return {0}
        if isinstance(node, ast.Await):
            return {depth - 1 for depth in self.namespace_depths(node.value) if depth > 0}
        if isinstance(node, (ast.NamedExpr, ast.Starred)):
            return self.namespace_depths(node.value)
        if isinstance(node, ast.Lambda):
            return {depth + 1 for depth in self.namespace_depths(node.body)}
        if (
            isinstance(node, ast.Attribute)
            and node.attr == "__dict__"
            and self.namespace_mapping(node.value)
        ):
            return {0}
        if isinstance(node, ast.IfExp):
            return self.namespace_depths(node.body) | self.namespace_depths(node.orelse)
        if isinstance(node, ast.BoolOp):
            return set().union(*(self.namespace_depths(value) for value in node.values))
        if isinstance(node, ast.Subscript):
            try:
                selected_key = ast.literal_eval(node.slice)
            except (ValueError, TypeError):
                return set()
            if isinstance(node.value, (ast.List, ast.Tuple)) and isinstance(
                selected_key,
                int,
            ):
                try:
                    return self.namespace_depths(node.value.elts[selected_key])
                except IndexError:
                    return set()
            if isinstance(node.value, ast.Dict):
                for key, value in zip(
                    node.value.keys,
                    node.value.values,
                    strict=True,
                ):
                    if key is None:
                        continue
                    try:
                        literal_key = ast.literal_eval(key)
                    except (ValueError, TypeError):
                        continue
                    if literal_key == selected_key:
                        return self.namespace_depths(value)
            return self.namespace_container_depths(node.value)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "vars"
            and self.builtin_is_unshadowed(node, "vars")
            and len(node.args) == 1
            and not node.keywords
            and self.current_module_object(node.args[0])
        ):
            return {0}
        if (
            not isinstance(node, ast.Call)
            or not isinstance(node.func, ast.Name)
            or node.args
            or node.keywords
        ):
            if isinstance(node, ast.Call):
                return {depth - 1 for depth in self.namespace_depths(node.func) if depth > 0}
            return set()
        name = node.func.id
        if name == "globals" and self.builtin_is_unshadowed(node, name):
            return {0}
        if (
            name in {"locals", "vars"}
            and isinstance(self.scope(node), ast.Module)
            and self.builtin_is_unshadowed(node, name)
        ):
            return {0}
        return {depth - 1 for depth in self.namespace_depths(node.func) if depth > 0}

    def namespace_mapping(self, node: ast.AST | None) -> bool:
        return 0 in self.namespace_depths(node)

    def current_module_object(self, node: ast.AST | None) -> bool:
        return (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id in self._sys_aliases
            and node.value.attr == "modules"
            and isinstance(node.slice, ast.Name)
            and node.slice.id == "__name__"
        )

    def discover_namespace_aliases(self) -> None:
        changed = True
        while changed:
            changed = False
            for node in ast.walk(self.tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                return_depths = set().union(
                    *(
                        self.namespace_depths(item.value)
                        for item in ast.walk(node)
                        if isinstance(item, ast.Return) and self.scope(item) is node
                    )
                )
                added_depth = 2 if isinstance(node, ast.AsyncFunctionDef) else 1
                depths = {depth + added_depth for depth in return_depths}
                binding = (self.scope(node), node.name)
                known = self._namespace_capabilities.setdefault(binding, set())
                if not depths <= known:
                    known.update(depths)
                    changed = True
                positional_parameters = [
                    *node.args.posonlyargs,
                    *node.args.args,
                ]
                default_parameters = (
                    positional_parameters[-len(node.args.defaults) :] if node.args.defaults else []
                )
                for parameter, default in zip(
                    default_parameters,
                    node.args.defaults,
                    strict=True,
                ):
                    if depths := self.namespace_depths(default):
                        binding = (node, parameter.arg)
                        known = self._namespace_capabilities.setdefault(binding, set())
                        if not depths <= known:
                            known.update(depths)
                            changed = True
                for parameter, default in zip(
                    node.args.kwonlyargs,
                    node.args.kw_defaults,
                    strict=True,
                ):
                    if default is None:
                        continue
                    if depths := self.namespace_depths(default):
                        binding = (node, parameter.arg)
                        known = self._namespace_capabilities.setdefault(binding, set())
                        if not depths <= known:
                            known.update(depths)
                            changed = True
            for node in ast.walk(self.tree):
                if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                    continue
                for target in _assignment_targets(node):
                    for name, depths in self._value_bindings(
                        target,
                        node.value,
                        self.namespace_depths,
                    ):
                        binding = (self._store_scope(node, name), name)
                        known = self._namespace_capabilities.setdefault(binding, set())
                        if not depths <= known:
                            known.update(depths)
                            changed = True
                    for name, depths in self._value_bindings(
                        target,
                        node.value,
                        self.namespace_container_depths,
                    ):
                        binding = (self._store_scope(node, name), name)
                        known = self._namespace_container_values.setdefault(
                            binding,
                            set(),
                        )
                        if not depths <= known:
                            known.update(depths)
                            changed = True
            for node in ast.walk(self.tree):
                if not isinstance(node, ast.Call):
                    continue
                partial_application = self._partial_application(node)
                if partial_application is None:
                    function = self._resolved_local_function(node.func)
                    if function is None:
                        continue
                    call_args = list(node.args)
                    call_keywords = list(node.keywords)
                else:
                    function, call_args, call_keywords = partial_application
                positional_parameters = [
                    *function.args.posonlyargs,
                    *function.args.args,
                ]
                parameter_by_name = {
                    parameter.arg: parameter
                    for parameter in [
                        *positional_parameters,
                        *function.args.kwonlyargs,
                    ]
                }
                for index, argument in enumerate(call_args):
                    if isinstance(argument, ast.Starred):
                        if function.args.vararg is not None:
                            depths = self.namespace_container_depths(argument.value)
                            binding = (function, function.args.vararg.arg)
                            known = self._namespace_container_values.setdefault(
                                binding,
                                set(),
                            )
                            if not depths <= known:
                                known.update(depths)
                                changed = True
                        continue
                    if index >= len(positional_parameters):
                        if function.args.vararg is not None:
                            depths = self.namespace_depths(argument)
                            binding = (function, function.args.vararg.arg)
                            known = self._namespace_container_values.setdefault(
                                binding,
                                set(),
                            )
                            if not depths <= known:
                                known.update(depths)
                                changed = True
                        continue
                    if depths := self.namespace_depths(argument):
                        binding = (function, positional_parameters[index].arg)
                        known = self._namespace_capabilities.setdefault(binding, set())
                        if not depths <= known:
                            known.update(depths)
                            changed = True
                for keyword in call_keywords:
                    if keyword.arg is None:
                        if function.args.kwarg is not None:
                            depths = self.namespace_container_depths(keyword.value)
                            binding = (function, function.args.kwarg.arg)
                            known = self._namespace_container_values.setdefault(
                                binding,
                                set(),
                            )
                            if not depths <= known:
                                known.update(depths)
                                changed = True
                        continue
                    parameter = parameter_by_name.get(keyword.arg)
                    if parameter is None:
                        if function.args.kwarg is not None:
                            depths = self.namespace_depths(keyword.value)
                            binding = (function, function.args.kwarg.arg)
                            known = self._namespace_container_values.setdefault(
                                binding,
                                set(),
                            )
                            if not depths <= known:
                                known.update(depths)
                                changed = True
                        continue
                    if depths := self.namespace_depths(keyword.value):
                        binding = (function, parameter.arg)
                        known = self._namespace_capabilities.setdefault(binding, set())
                        if not depths <= known:
                            known.update(depths)
                            changed = True

    def _value_bindings(
        self,
        target: ast.AST,
        value: ast.AST | None,
        evaluator: Callable[[ast.AST | None], set[int]],
    ) -> list[tuple[str, set[int]]]:
        if (
            isinstance(target, (ast.List, ast.Tuple))
            and isinstance(value, (ast.List, ast.Tuple))
            and len(target.elts) == len(value.elts)
        ):
            return [
                binding
                for target_item, value_item in zip(
                    target.elts,
                    value.elts,
                    strict=True,
                )
                for binding in self._value_bindings(
                    target_item,
                    value_item,
                    evaluator,
                )
            ]
        depths = evaluator(value)
        if not depths:
            return []
        return [(name, depths) for name in _bound_target_names(target)]

    def protected_namespace_slot(
        self,
        node: ast.AST | None,
        symbol: str,
    ) -> bool:
        if (
            isinstance(node, ast.Attribute)
            and self.namespace_mapping(node.value)
            and node.attr == symbol
        ):
            return True
        if isinstance(node, ast.Subscript) and self.namespace_mapping(node.value):
            return isinstance(node.slice, ast.Constant) and node.slice.value == symbol
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"get", "__getitem__"}
            and self.namespace_mapping(node.func.value)
            and len(node.args) == 1
            and not node.keywords
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == symbol
        )

    def protected_namespace_attribute_call(
        self,
        node: ast.Call,
        symbol: str,
    ) -> bool:
        builtin_call = (
            isinstance(node.func, ast.Name)
            and node.func.id in {"delattr", "setattr"}
            and self.builtin_is_unshadowed(node, node.func.id)
            and len(node.args) == (3 if node.func.id == "setattr" else 2)
            and not node.keywords
            and self.namespace_mapping(node.args[0])
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value == symbol
        )
        bound_call = (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in {"__delattr__", "__setattr__"}
            and self.namespace_mapping(node.func.value)
            and len(node.args) == (2 if node.func.attr == "__setattr__" else 1)
            and not node.keywords
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == symbol
        )
        unbound_call = (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "object"
            and self.builtin_is_unshadowed(node, "object")
            and node.func.attr in {"__delattr__", "__setattr__"}
            and len(node.args) == (3 if node.func.attr == "__setattr__" else 2)
            and not node.keywords
            and self.namespace_mapping(node.args[0])
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value == symbol
        )
        return builtin_call or bound_call or unbound_call


def _definition_store_counts(tree: ast.AST) -> dict[str, int]:
    """Count assignment-like definitions for fresh-container sink validation."""

    counts: dict[str, int] = {}
    for node in ast.walk(tree):
        for target in _assignment_targets(node):
            for name in _bound_target_names(target):
                counts[name] = counts.get(name, 0) + 1
        for name in _statement_bound_names(node):
            counts[name] = counts.get(name, 0) + 1
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for name in _import_bound_names(node) - {"*"}:
                counts[name] = counts.get(name, 0) + 1
        if isinstance(node, ast.arg):
            counts[node.arg] = counts.get(node.arg, 0) + 1
    return counts


def _owner_import_context(
    tree: ast.AST,
    symbol: str,
) -> tuple[set[str], set[str], set[str], set[str]]:
    """Collect owner aliases and imported mutation-callable spellings."""

    aliases = {symbol}
    operator_module_aliases = {"operator"}
    imported_operator_mutators: set[str] = set()
    imported_methodcallers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for item in node.names:
                if item.name == symbol:
                    aliases.add(item.asname or item.name)
                if node.module == "operator" and item.name in MUTATING_OPERATOR_FUNCTIONS:
                    imported_operator_mutators.add(item.asname or item.name)
                if node.module == "operator" and item.name == "methodcaller":
                    imported_methodcallers.add(item.asname or item.name)
        elif isinstance(node, ast.Import):
            for item in node.names:
                if item.name == "operator":
                    operator_module_aliases.add(item.asname or item.name)
    return (
        aliases,
        operator_module_aliases,
        imported_operator_mutators,
        imported_methodcallers,
    )


def _fresh_mutable_value(
    node: ast.AST | None,
    *,
    local_binding_names: set[str],
    safe_deepcopy: bool,
) -> bool:
    """Return whether an expression creates a new policy-safe mutable sink."""

    if isinstance(
        node,
        (ast.Dict, ast.DictComp, ast.List, ast.ListComp, ast.Set, ast.SetComp),
    ):
        return True
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"dict", "list", "set"}
        and node.func.id not in local_binding_names
        and not node.keywords
    ):
        return True
    return (
        safe_deepcopy
        and isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "copy"
        and "copy" not in local_binding_names
        and node.func.attr == "deepcopy"
    )


def _safe_sink_identity_names(
    node: ast.AST | None,
    safe_sink_names: set[str],
) -> set[str]:
    """Resolve expressions that select an existing fresh sink without copying it."""

    if isinstance(node, ast.Name) and node.id in safe_sink_names:
        return {node.id}
    if isinstance(node, (ast.NamedExpr, ast.Starred)):
        return _safe_sink_identity_names(node.value, safe_sink_names)
    if isinstance(node, ast.Subscript):
        try:
            selected_key = ast.literal_eval(node.slice)
        except (ValueError, TypeError):
            return set()
        if isinstance(node.value, (ast.List, ast.Tuple)) and isinstance(
            selected_key,
            int,
        ):
            try:
                selected = node.value.elts[selected_key]
            except IndexError:
                return set()
            return _safe_sink_identity_names(selected, safe_sink_names)
        if isinstance(node.value, ast.Dict):
            for key, value in zip(node.value.keys, node.value.values, strict=True):
                if key is None:
                    continue
                try:
                    literal_key = ast.literal_eval(key)
                except (ValueError, TypeError):
                    continue
                if literal_key == selected_key:
                    return _safe_sink_identity_names(value, safe_sink_names)
        return set()
    if isinstance(node, ast.IfExp):
        branches = [
            _safe_sink_identity_names(node.body, safe_sink_names),
            _safe_sink_identity_names(node.orelse, safe_sink_names),
        ]
    elif isinstance(node, ast.BoolOp):
        branches = [_safe_sink_identity_names(value, safe_sink_names) for value in node.values]
    else:
        return set()
    if any(not branch for branch in branches):
        return set()
    return set().union(*branches)


def _safe_sink_identity_bindings(
    target: ast.AST,
    value: ast.AST | None,
    safe_sink_names: set[str],
) -> list[tuple[str, set[str]]]:
    """Pair destructured targets with the existing fresh sinks they select."""

    if (
        isinstance(target, (ast.List, ast.Tuple))
        and isinstance(value, (ast.List, ast.Tuple))
        and len(target.elts) == len(value.elts)
    ):
        return [
            binding
            for target_item, value_item in zip(target.elts, value.elts, strict=True)
            for binding in _safe_sink_identity_bindings(
                target_item,
                value_item,
                safe_sink_names,
            )
        ]
    identities = _safe_sink_identity_names(value, safe_sink_names)
    return [(name, identities) for name in _bound_target_names(target)]


def _fresh_container_names(
    tree: ast.AST,
    *,
    definition_store_counts: dict[str, int],
    local_binding_names: set[str],
    safe_deepcopy: bool,
) -> set[str]:
    """Collect single-definition names for fresh mutable sinks and direct aliases."""

    names = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and _fresh_mutable_value(
            node.value,
            local_binding_names=local_binding_names,
            safe_deepcopy=safe_deepcopy,
        )
        for target in _assignment_targets(node)
        if isinstance(target, ast.Name) and definition_store_counts.get(target.id) == 1
    }
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                continue
            for target in _assignment_targets(node):
                for name, identities in _safe_sink_identity_bindings(
                    target,
                    node.value,
                    names,
                ):
                    if identities and name not in names and definition_store_counts.get(name) == 1:
                        names.add(name)
                        changed = True
    return names


def _immutable_lookup_names(
    tree: ast.AST,
    *,
    store_counts: dict[str, int],
    load_counts: dict[str, int],
) -> set[str]:
    """Collect one-shot literal mappings whose `.get` breaks owner provenance."""

    return {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in _assignment_targets(node)
        if isinstance(target, ast.Name)
        and isinstance(node.value, ast.Dict)
        and _literal_immutable_value(node.value)
        and store_counts.get(target.id) == 1
        and load_counts.get(target.id) == 1
    }


class _OwnerProvenance:
    """Propagate aliases, containment, and owner-returning callables to a fixpoint."""

    def __init__(
        self,
        *,
        symbol: str,
        aliases: set[str],
        rich_expressions: bool,
        safe_callable_contracts: dict[
            str,
            tuple[tuple[str, ...], frozenset[str]],
        ],
        provenance_callables: frozenset[str],
        immutable_lookup_names: set[str],
    ) -> None:
        self.symbol = symbol
        self.aliases = aliases
        self.contained_owner_names: set[str] = set()
        self.owner_returning_callables: set[str] = set()
        self._rich_expressions = rich_expressions
        self._safe_callable_contracts = safe_callable_contracts
        self._provenance_callables = provenance_callables
        self._immutable_lookup_names = immutable_lookup_names

    def ownership_break(self, node: ast.AST | None) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in self._immutable_lookup_names
            and node.func.attr == "get"
            and not node.keywords
            and len(node.args) in {1, 2}
            and (len(node.args) == 1 or _literal_immutable_value(node.args[1]))
        )

    def contains_owner(self, node: ast.AST | None) -> bool:
        if node is None:
            return False
        if isinstance(node, ast.Name):
            return node.id in self.contained_owner_names
        if isinstance(node, (ast.Await, ast.Starred)):
            return self.contains_owner(node.value)
        if isinstance(node, ast.NamedExpr):
            return self.contains_owner(node.value)
        if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
            return any(self.derived(item) or self.contains_owner(item) for item in node.elts)
        if isinstance(node, ast.Dict):
            return any(
                self.derived(item) or self.contains_owner(item)
                for item in [*node.keys, *node.values]
                if item is not None
            )
        if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            return (
                self.derived(node.elt)
                or self.contains_owner(node.elt)
                or any(
                    self.derived(generator.iter) or self.contains_owner(generator.iter)
                    for generator in node.generators
                )
            )
        if isinstance(node, ast.DictComp):
            return any(
                self.derived(item) or self.contains_owner(item) for item in (node.key, node.value)
            ) or any(
                self.derived(generator.iter) or self.contains_owner(generator.iter)
                for generator in node.generators
            )
        if isinstance(node, ast.IfExp):
            return self.contains_owner(node.body) or self.contains_owner(node.orelse)
        if isinstance(node, ast.BoolOp):
            return any(self.contains_owner(item) for item in node.values)
        if isinstance(node, ast.BinOp):
            return any(
                self.derived(item) or self.contains_owner(item) for item in (node.left, node.right)
            )
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "dict",
                "enumerate",
                "iter",
                "list",
                "set",
                "tuple",
            }:
                return any(
                    self.derived(item) or self.contains_owner(item)
                    for item in [*node.args, *[kw.value for kw in node.keywords]]
                )
            if isinstance(node.func, ast.Attribute) and self.contains_owner(node.func.value):
                return node.func.attr in {"copy", "items", "values"}
        return False

    def derived(self, node: ast.AST | None) -> bool:
        if self.ownership_break(node):
            return False
        if isinstance(node, ast.Await):
            return self.derived(node.value)
        if isinstance(node, ast.NamedExpr):
            return self.derived(node.value)
        if isinstance(node, ast.IfExp):
            return self.derived(node.body) or self.derived(node.orelse)
        if isinstance(node, ast.BoolOp):
            return any(self.derived(item) for item in node.values)
        if isinstance(node, ast.Call) and self.owner_returning_callable(node.func):
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and (
                node.func.id in self._safe_callable_contracts
                or node.func.id in self._provenance_callables
            )
            and any(
                self.derived(item) or self.contains_owner(item)
                for item in [*node.args, *[keyword.value for keyword in node.keywords]]
            )
        ):
            return True
        if isinstance(node, (ast.Attribute, ast.Subscript)) and (
            self.derived(node.value) or self.contains_owner(node.value)
        ):
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and (self.derived(node.func.value) or self.contains_owner(node.func.value))
            and node.func.attr in {"get", "items", "pop", "popitem", "values", "__getitem__"}
        ):
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in OWNER_ALIAS_RETURN_METHODS
            and (
                self.derived(node.func.value)
                or self.contains_owner(node.func.value)
                or any(
                    self.derived(item) or self.contains_owner(item)
                    for item in [
                        *node.args,
                        *[keyword.value for keyword in node.keywords],
                    ]
                )
            )
        ):
            return True
        analyzer = _richly_derived_from_owner if self._rich_expressions else _derived_from_owner
        return analyzer(node, symbol=self.symbol, aliases=self.aliases)

    def owner_returning_callable(self, node: ast.AST | None) -> bool:
        if isinstance(node, ast.Name):
            return node.id in self.owner_returning_callables
        if isinstance(node, ast.Lambda):
            return self.derived(node.body) or self.contains_owner(node.body)
        if isinstance(node, (ast.Await, ast.NamedExpr, ast.Starred)):
            return self.owner_returning_callable(node.value)
        if isinstance(node, ast.IfExp):
            return self.owner_returning_callable(node.body) or self.owner_returning_callable(
                node.orelse
            )
        if isinstance(node, ast.BinOp):
            return self.owner_returning_callable(node.left) or self.owner_returning_callable(
                node.right
            )
        if isinstance(node, (ast.BoolOp, ast.List, ast.Set, ast.Tuple)):
            candidates = node.values if isinstance(node, ast.BoolOp) else node.elts
            return any(self.owner_returning_callable(item) for item in candidates)
        if isinstance(node, ast.Dict):
            return any(
                self.owner_returning_callable(item)
                for item in [*node.keys, *node.values]
                if item is not None
            )
        if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            return self.owner_returning_callable(node.elt)
        if isinstance(node, ast.DictComp):
            return self.owner_returning_callable(node.key) or self.owner_returning_callable(
                node.value
            )
        if isinstance(node, ast.Subscript):
            return self.owner_returning_callable(node.value)
        if isinstance(node, ast.Call):
            if self.owner_returning_callable(node.func):
                return True
            if isinstance(node.func, ast.Name) and node.func.id in {
                "dict",
                "enumerate",
                "filter",
                "iter",
                "list",
                "map",
                "next",
                "reversed",
                "set",
                "tuple",
                "zip",
            }:
                return any(
                    self.owner_returning_callable(item)
                    for item in [*node.args, *[kw.value for kw in node.keywords]]
                )
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "copy",
                "get",
                "items",
                "pop",
                "popitem",
                "setdefault",
                "values",
                "__getitem__",
            }:
                return self.owner_returning_callable(node.func.value)
        return False

    def escapable_owner_callable(self, node: ast.AST | None) -> bool:
        """Return whether a value carries an untrusted callable owner capability."""

        if isinstance(node, ast.Name):
            return (
                node.id in self.owner_returning_callables
                and node.id not in self._safe_callable_contracts
                and node.id not in self._provenance_callables
            )
        if isinstance(node, ast.Lambda):
            return self.derived(node.body) or self.contains_owner(node.body)
        if isinstance(node, (ast.Await, ast.NamedExpr, ast.Starred)):
            return self.escapable_owner_callable(node.value)
        if isinstance(node, ast.IfExp):
            return self.escapable_owner_callable(node.body) or self.escapable_owner_callable(
                node.orelse
            )
        if isinstance(node, ast.BinOp):
            return self.escapable_owner_callable(node.left) or self.escapable_owner_callable(
                node.right
            )
        if isinstance(node, (ast.BoolOp, ast.List, ast.Set, ast.Tuple)):
            candidates = node.values if isinstance(node, ast.BoolOp) else node.elts
            return any(self.escapable_owner_callable(item) for item in candidates)
        if isinstance(node, ast.Dict):
            return any(
                self.escapable_owner_callable(item)
                for item in [*node.keys, *node.values]
                if item is not None
            )
        if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            return self.escapable_owner_callable(node.elt)
        if isinstance(node, ast.DictComp):
            return self.escapable_owner_callable(node.key) or self.escapable_owner_callable(
                node.value
            )
        if isinstance(node, ast.Subscript):
            return self.escapable_owner_callable(node.value)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and self.escapable_owner_callable(node.func):
                return True
            if isinstance(node.func, ast.Name) and node.func.id in {
                "dict",
                "enumerate",
                "filter",
                "iter",
                "list",
                "map",
                "next",
                "reversed",
                "set",
                "tuple",
                "zip",
            }:
                return any(
                    self.escapable_owner_callable(item)
                    for item in [*node.args, *[kw.value for kw in node.keywords]]
                )
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "copy",
                "get",
                "items",
                "pop",
                "popitem",
                "setdefault",
                "values",
                "__getitem__",
            }:
                return self.escapable_owner_callable(node.func.value)
        return False

    def propagate(self, tree: ast.AST, *, safe_sink_names: set[str]) -> None:
        changed = True
        while changed:
            changed = self._propagate_value_aliases(tree)
            changed = self._propagate_parameter_defaults(tree) or changed
            changed = self._propagate_callable_results(tree, safe_sink_names) or changed
            changed = self._propagate_containment(tree, safe_sink_names) or changed
            changed = (
                self._propagate_safe_sink_identity(
                    tree,
                    safe_sink_names,
                )
                or changed
            )

    def _propagate_value_aliases(self, tree: ast.AST) -> bool:
        changed = False
        for node in ast.walk(tree):
            value: ast.AST | None = None
            targets: list[ast.AST] = []
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                value, targets = node.value, _assignment_targets(node)
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                value, targets = node.iter, [node.target]
            elif isinstance(node, ast.Match):
                if self.derived(node.subject) or self.contains_owner(node.subject):
                    for case in node.cases:
                        for name in _pattern_bound_names(case.pattern):
                            if name not in self.aliases:
                                self.aliases.add(name)
                                changed = True
                continue
            if value is None:
                continue
            value_is_derived = self.derived(value)
            value_contains_owner = self.contains_owner(value)
            if isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                value_is_derived = value_is_derived or value_contains_owner
                value_contains_owner = False
            for target in targets:
                for name in _bound_target_names(target):
                    if value_is_derived and name not in self.aliases:
                        self.aliases.add(name)
                        changed = True
                    elif value_contains_owner and name not in self.contained_owner_names:
                        self.contained_owner_names.add(name)
                        changed = True
        return changed

    def _propagate_parameter_defaults(self, tree: ast.AST) -> bool:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(
                node,
                (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda),
            ):
                continue
            positional_parameters = [*node.args.posonlyargs, *node.args.args]
            default_parameters = (
                positional_parameters[-len(node.args.defaults) :] if node.args.defaults else []
            )
            bindings = [
                *zip(default_parameters, node.args.defaults, strict=True),
                *(
                    (parameter, default)
                    for parameter, default in zip(
                        node.args.kwonlyargs,
                        node.args.kw_defaults,
                        strict=True,
                    )
                    if default is not None
                ),
            ]
            for parameter, default in bindings:
                if self.derived(default) and parameter.arg not in self.aliases:
                    self.aliases.add(parameter.arg)
                    changed = True
                if self.contains_owner(default) and parameter.arg not in self.contained_owner_names:
                    self.contained_owner_names.add(parameter.arg)
                    changed = True
                if (
                    self.owner_returning_callable(default)
                    and parameter.arg not in self.owner_returning_callables
                ):
                    self.owner_returning_callables.add(parameter.arg)
                    changed = True
        return changed

    def _propagate_callable_results(
        self,
        tree: ast.AST,
        safe_sink_names: set[str],
    ) -> bool:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            if node.name in self.owner_returning_callables:
                continue
            if any(
                self.derived(item.value)
                or self.contains_owner(item.value)
                or self.owner_returning_callable(item.value)
                for item in ast.walk(node)
                if isinstance(item, (ast.Return, ast.Yield, ast.YieldFrom))
                and item.value is not None
            ):
                self.owner_returning_callables.add(node.name)
                changed = True
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                value = node.value
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                value = node.iter
            else:
                continue
            if not self.owner_returning_callable(value):
                continue
            for target in _assignment_targets(node):
                for name in _bound_target_names(target):
                    if name not in self.owner_returning_callables:
                        self.owner_returning_callables.add(name)
                        changed = True
                if (
                    isinstance(target, ast.Subscript)
                    and (sink_name := _root_name(target.value)) in safe_sink_names
                    and sink_name not in self.owner_returning_callables
                ):
                    self.owner_returning_callables.add(sink_name)
                    changed = True
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in safe_sink_names
                and node.func.attr in MUTATING_METHODS
                and any(
                    self.owner_returning_callable(item)
                    for item in [*node.args, *[kw.value for kw in node.keywords]]
                )
            ):
                continue
            if node.func.value.id not in self.owner_returning_callables:
                self.owner_returning_callables.add(node.func.value.id)
                changed = True
        return changed

    def _propagate_containment(
        self,
        tree: ast.AST,
        safe_sink_names: set[str],
    ) -> bool:
        changed = False
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in safe_sink_names
                and not self.derived(node.func.value)
                and node.func.attr in MUTATING_METHODS
                and any(
                    self.derived(item) or self.contains_owner(item)
                    for item in [*node.args, *[kw.value for kw in node.keywords]]
                )
                and node.func.value.id not in self.contained_owner_names
            ):
                self.contained_owner_names.add(node.func.value.id)
                changed = True
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                for target in _assignment_targets(node):
                    for sink, value in _assignment_sink_bindings(target, node.value):
                        if not (self.derived(value) or self.contains_owner(value)):
                            continue
                        if (
                            isinstance(sink, ast.Subscript)
                            and (sink_name := _root_name(sink.value)) in safe_sink_names
                            and sink_name not in self.contained_owner_names
                        ):
                            self.contained_owner_names.add(sink_name)
                            changed = True
            elif (
                isinstance(node, ast.AugAssign)
                and (
                    isinstance(node.target, ast.Name)
                    and node.target.id in safe_sink_names
                    or isinstance(node.target, ast.Subscript)
                    and _root_name(node.target.value) in safe_sink_names
                )
                and not self.derived(node.target)
                and (self.derived(node.value) or self.contains_owner(node.value))
            ):
                sink_name = _root_name(node.target)
                if sink_name is not None and sink_name not in self.contained_owner_names:
                    self.contained_owner_names.add(sink_name)
                    changed = True
        return changed

    def _propagate_safe_sink_identity(
        self,
        tree: ast.AST,
        safe_sink_names: set[str],
    ) -> bool:
        """Share propagated state between direct names for one fresh container."""

        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                continue
            for target in _assignment_targets(node):
                for name, sources in _safe_sink_identity_bindings(
                    target,
                    node.value,
                    safe_sink_names,
                ):
                    if not sources:
                        continue
                    if name not in safe_sink_names:
                        continue
                    identities = {*sources, name}
                    if identities & self.contained_owner_names:
                        for identity in identities - self.contained_owner_names:
                            self.contained_owner_names.add(identity)
                            changed = True
                    if identities & self.owner_returning_callables:
                        for identity in identities - self.owner_returning_callables:
                            self.owner_returning_callables.add(identity)
                            changed = True
        return changed


class _MutatorClassifier:
    """Classify direct, aliased, and selected bound/unbound mutator callables."""

    def __init__(
        self,
        *,
        derived: Callable[[ast.AST | None], bool],
        operator_module_aliases: set[str],
        imported_operator_mutators: set[str],
        imported_methodcallers: set[str],
    ) -> None:
        self._derived = derived
        self._operator_module_aliases = operator_module_aliases
        self._imported_methodcallers = imported_methodcallers
        self._bound_aliases: set[str] = set()
        self._unbound_aliases = set(imported_operator_mutators)

    def kind(self, node: ast.AST | None) -> str | None:
        if isinstance(node, ast.Name):
            if node.id in self._bound_aliases:
                return "bound"
            if node.id in self._unbound_aliases:
                return "unbound"
            return None
        if isinstance(node, ast.Attribute) and node.attr in MUTATING_METHODS:
            if self._derived(node.value):
                return "bound"
            if isinstance(node.value, ast.Name) and node.value.id in {
                "dict",
                "list",
                "set",
            }:
                return "unbound"
            return None
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in self._operator_module_aliases
            and node.attr in MUTATING_OPERATOR_FUNCTIONS
        ):
            return "unbound"
        if (
            isinstance(node, ast.Call)
            and (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in self._operator_module_aliases
                and node.func.attr == "methodcaller"
                or isinstance(node.func, ast.Name)
                and node.func.id in self._imported_methodcallers
            )
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value in MUTATING_METHODS
        ):
            return "unbound"
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "getattr"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value in MUTATING_METHODS
        ):
            if self._derived(node.args[0]):
                return "bound"
            if isinstance(node.args[0], ast.Name) and node.args[0].id in {
                "dict",
                "list",
                "set",
            }:
                return "unbound"
            return None
        if isinstance(node, ast.Starred):
            return self.kind(node.value)
        if isinstance(node, (ast.Subscript, ast.IfExp)):
            candidates = (
                [node.value] if isinstance(node, ast.Subscript) else [node.body, node.orelse]
            )
        elif isinstance(node, (ast.BoolOp, ast.List, ast.Set, ast.Tuple)):
            candidates = node.values if isinstance(node, ast.BoolOp) else node.elts
        else:
            return None
        kinds = {kind for candidate in candidates if (kind := self.kind(candidate))}
        if "bound" in kinds:
            return "bound"
        if "unbound" in kinds:
            return "unbound"
        return None

    def discover_aliases(self, nodes: tuple[ast.AST, ...]) -> None:
        changed = True
        while changed:
            changed = False
            for node in nodes:
                if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                    continue
                kind = self.kind(node.value)
                if kind is None:
                    continue
                destination = self._bound_aliases if kind == "bound" else self._unbound_aliases
                for target in _assignment_targets(node):
                    for name in _bound_target_names(target):
                        if name not in destination:
                            destination.add(name)
                            changed = True


class MutableOwnerAnalyzer:
    """Reuse symbol-independent syntax analysis across owner checks for one tree."""

    def __init__(
        self,
        tree: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda,
    ) -> None:
        self.tree = tree
        self.nodes = tuple(ast.walk(tree))
        self.lexical = _LexicalBindings(tree)
        self.lexical.discover_namespace_aliases()
        self.store_counts, self.load_counts = _name_access_counts(tree)
        self.local_binding_names = _local_binding_names(tree, self.store_counts)
        self.definition_store_counts = _definition_store_counts(tree)
        self.cross_scope_names = {
            name
            for node in self.nodes
            if isinstance(node, (ast.Global, ast.Nonlocal))
            for name in node.names
        }
        self.immutable_lookup_names = _immutable_lookup_names(
            tree,
            store_counts=self.store_counts,
            load_counts=self.load_counts,
        )
        self._owner_import_contexts: dict[
            str,
            tuple[set[str], set[str], set[str], set[str]],
        ] = {}
        self._fresh_container_names: dict[bool, set[str]] = {}

    def owner_import_context(
        self,
        symbol: str,
    ) -> tuple[set[str], set[str], set[str], set[str]]:
        cached = self._owner_import_contexts.get(symbol)
        if cached is None:
            cached = _owner_import_context(self.tree, symbol)
            self._owner_import_contexts[symbol] = cached
        aliases, modules, mutators, methodcallers = cached
        return set(aliases), set(modules), set(mutators), set(methodcallers)

    def fresh_container_names(self, *, safe_deepcopy: bool) -> set[str]:
        cached = self._fresh_container_names.get(safe_deepcopy)
        if cached is None:
            cached = _fresh_container_names(
                self.tree,
                definition_store_counts=self.definition_store_counts,
                local_binding_names=self.local_binding_names,
                safe_deepcopy=safe_deepcopy,
            )
            self._fresh_container_names[safe_deepcopy] = cached
        return set(cached)

    def mutations(
        self,
        symbol: str,
        *,
        allow_definition: bool = False,
        rich_expressions: bool = False,
        reject_unknown_owner_calls: bool = False,
        safe_callables: frozenset[str] = frozenset(),
        safe_callable_contracts: dict[
            str,
            tuple[tuple[str, ...], frozenset[str]],
        ]
        | None = None,
        provenance_callables: frozenset[str] = frozenset(),
        additional_safe_sink_names: frozenset[str] = frozenset(),
        safe_deepcopy: bool = False,
        safe_method_receivers: frozenset[str] = frozenset(),
    ) -> list[ast.AST]:
        return _mutable_owner_mutations(
            self.tree,
            symbol,
            allow_definition=allow_definition,
            rich_expressions=rich_expressions,
            reject_unknown_owner_calls=reject_unknown_owner_calls,
            safe_callables=safe_callables,
            safe_callable_contracts=safe_callable_contracts,
            provenance_callables=provenance_callables,
            additional_safe_sink_names=additional_safe_sink_names,
            safe_deepcopy=safe_deepcopy,
            safe_method_receivers=safe_method_receivers,
            _analyzer=self,
        )


def _mutable_owner_mutations(
    tree: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda,
    symbol: str,
    *,
    allow_definition: bool = False,
    rich_expressions: bool = False,
    reject_unknown_owner_calls: bool = False,
    safe_callables: frozenset[str] = frozenset(),
    safe_callable_contracts: dict[
        str,
        tuple[tuple[str, ...], frozenset[str]],
    ]
    | None = None,
    provenance_callables: frozenset[str] = frozenset(),
    additional_safe_sink_names: frozenset[str] = frozenset(),
    safe_deepcopy: bool = False,
    safe_method_receivers: frozenset[str] = frozenset(),
    _analyzer: MutableOwnerAnalyzer | None = None,
) -> list[ast.AST]:
    """Find static writes through a mutable owner or a derived local alias."""

    analyzer = _analyzer or MutableOwnerAnalyzer(tree)
    if analyzer.tree is not tree:
        raise ValueError("mutable-owner analyzer tree does not match the requested tree")
    (
        aliases,
        operator_module_aliases,
        imported_operator_mutators,
        imported_methodcallers,
    ) = analyzer.owner_import_context(symbol)

    lexical = analyzer.lexical
    local_binding_names = analyzer.local_binding_names
    for node in analyzer.nodes:
        if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            continue
        if not lexical.protected_namespace_slot(node.value, symbol):
            continue
        for target in _assignment_targets(node):
            aliases.update(_bound_target_names(target))
    safe_callable_contracts = safe_callable_contracts or {}
    cross_scope_names = analyzer.cross_scope_names
    fresh_container_names = analyzer.fresh_container_names(safe_deepcopy=safe_deepcopy)
    safe_sink_names = fresh_container_names | set(additional_safe_sink_names)

    provenance = _OwnerProvenance(
        symbol=symbol,
        aliases=aliases,
        rich_expressions=rich_expressions,
        safe_callable_contracts=safe_callable_contracts,
        provenance_callables=provenance_callables,
        immutable_lookup_names=analyzer.immutable_lookup_names,
    )
    provenance.propagate(tree, safe_sink_names=safe_sink_names)
    aliases = provenance.aliases
    contained_owner_names = provenance.contained_owner_names
    contains_owner = provenance.contains_owner
    derived = provenance.derived

    def read_only_owner_call(node: ast.Call) -> bool:
        if isinstance(node.func, ast.Name):
            if node.func.id in safe_callables:
                return True
            contract = safe_callable_contracts.get(node.func.id)
            if contract is None:
                return False
            positional_parameters, protected_parameters = contract
            for index, argument in enumerate(node.args):
                if not (derived(argument) or contains_owner(argument)):
                    continue
                if (
                    isinstance(argument, ast.Starred)
                    or index >= len(positional_parameters)
                    or positional_parameters[index] not in protected_parameters
                ):
                    return False
            for keyword in node.keywords:
                if not (derived(keyword.value) or contains_owner(keyword.value)):
                    continue
                if keyword.arg is None or keyword.arg not in protected_parameters:
                    return False
            return True
        if not isinstance(node.func, ast.Attribute):
            return False
        if (
            isinstance(node.func.value, ast.Name)
            and node.func.value.id in safe_sink_names
            and not derived(node.func.value)
            and node.func.attr in MUTATING_METHODS
        ):
            return True
        if node.func.attr in READ_ONLY_PARAMETER_METHODS:
            trusted_global_mapping = (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id in safe_method_receivers
                and node.func.value.id not in local_binding_names
            )
            return (
                derived(node.func.value)
                or contains_owner(node.func.value)
                or provenance.ownership_break(node)
                or trusted_global_mapping
            )
        if (
            node.func.attr in IMMUTABLE_LITERAL_READ_ONLY_METHODS
            and isinstance(node.func.value, ast.Constant)
            and isinstance(node.func.value.value, (bytes, str))
        ):
            return True
        return (
            safe_deepcopy
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "copy"
            and "copy" not in local_binding_names
            and node.func.attr == "deepcopy"
        )

    mutators = _MutatorClassifier(
        derived=derived,
        operator_module_aliases=operator_module_aliases,
        imported_operator_mutators=imported_operator_mutators,
        imported_methodcallers=imported_methodcallers,
    )
    mutators.discover_aliases(analyzer.nodes)

    mutations: list[ast.AST] = (
        [
            node
            for node in analyzer.nodes
            if node is not tree
            and isinstance(
                node,
                (ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef, ast.Lambda),
            )
            and any(
                isinstance(item, ast.Name)
                and isinstance(item.ctx, ast.Load)
                and item.id in aliases | contained_owner_names
                for item in ast.walk(node)
            )
        ]
        if isinstance(tree, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda))
        else []
    )
    mutations.extend(
        node
        for node in analyzer.nodes
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda))
        and any(
            derived(default) or contains_owner(default)
            for default in [*node.args.defaults, *node.args.kw_defaults]
            if default is not None
        )
    )
    mutations.extend(
        node
        for node in analyzer.nodes
        if reject_unknown_owner_calls
        and isinstance(node, ast.ClassDef)
        and any(
            isinstance(item, ast.Name)
            and isinstance(item.ctx, ast.Load)
            and item.id in aliases | contained_owner_names
            for item in ast.walk(node)
        )
    )
    parents = lexical.parents

    mutations.extend(
        node
        for node in analyzer.nodes
        if mutators.kind(node) == "bound"
        and not (isinstance((parent := parents.get(node)), ast.Call) and parent.func is node)
    )
    definition_seen = False
    for node in analyzer.nodes:
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr, ast.TypeAlias)):
            targets = (
                node.targets
                if isinstance(node, ast.Assign)
                else [node.name if isinstance(node, ast.TypeAlias) else node.target]
            )
            for target in targets:
                sink_targets = _assignment_sink_targets(target)
                sink_bindings = _assignment_sink_bindings(target, node.value)
                if symbol in _bound_target_names(target):
                    if (
                        allow_definition
                        and isinstance(node, (ast.Assign, ast.AnnAssign))
                        and isinstance(target, ast.Name)
                        and node in tree.body
                        and not definition_seen
                    ):
                        definition_seen = True
                    else:
                        mutations.append(node)
                elif (
                    isinstance(target, ast.Name)
                    and target.id in cross_scope_names
                    and (derived(node.value) or contains_owner(node.value))
                ):
                    mutations.append(node)
                elif any(
                    lexical.protected_namespace_slot(sink, symbol) or derived(sink.value)
                    for sink in sink_targets
                ):
                    mutations.append(node)
                elif any(
                    isinstance(sink, ast.Attribute)
                    or isinstance(sink, ast.Subscript)
                    and _root_name(sink.value) not in safe_sink_names
                    for sink, _ in sink_bindings
                ) and any(
                    (
                        isinstance(sink, ast.Attribute)
                        or isinstance(sink, ast.Subscript)
                        and _root_name(sink.value) not in safe_sink_names
                    )
                    and (
                        derived(value)
                        or contains_owner(value)
                        or provenance.escapable_owner_callable(value)
                    )
                    for sink, value in sink_bindings
                ):
                    mutations.append(node)
        elif isinstance(node, (ast.Import, ast.ImportFrom)) and symbol in (
            _import_bound_names(node)
        ):
            scope = lexical.scope(node)
            if isinstance(scope, ast.Module) and node in scope.body and not definition_seen:
                definition_seen = True
            elif isinstance(scope, ast.Module) or lexical.scope_rebinds_outer_name(
                scope,
                symbol,
            ):
                mutations.append(node)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            optional_targets = [
                item.optional_vars for item in node.items if item.optional_vars is not None
            ]
            if any(
                symbol in _bound_target_names(target)
                or any(derived(sink.value) for sink in _assignment_sink_targets(target))
                for target in optional_targets
            ):
                mutations.append(node)
        elif symbol in _statement_bound_names(node):
            mutations.append(node)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
            sink_targets = _assignment_sink_targets(node.target)
            if (
                symbol in _bound_target_names(node.target)
                or any(derived(target.value) for target in sink_targets)
                or sink_targets
                and (
                    derived(node.iter)
                    or contains_owner(node.iter)
                    or provenance.owner_returning_callable(node.iter)
                )
            ):
                mutations.append(node)
        elif isinstance(node, ast.AugAssign):
            unsafe_sink = isinstance(node.target, ast.Attribute) or (
                isinstance(node.target, ast.Subscript)
                and _root_name(node.target.value) not in safe_sink_names
            )
            if (
                lexical.protected_namespace_slot(
                    node.target,
                    symbol,
                )
                or derived(node.target)
                or unsafe_sink
                and (derived(node.value) or contains_owner(node.value))
            ):
                mutations.append(node)
        elif isinstance(node, ast.Delete) and any(
            derived(target) or lexical.protected_namespace_slot(target, symbol)
            for target in node.targets
        ):
            mutations.append(node)
        elif isinstance(node, ast.Call):
            owner_arguments = [
                argument
                for argument in [*node.args, *[item.value for item in node.keywords]]
                if derived(argument) or contains_owner(argument)
            ]
            owner_callable_arguments = [
                argument
                for argument in [*node.args, *[item.value for item in node.keywords]]
                if provenance.escapable_owner_callable(argument)
            ]
            namespace_arguments = [
                argument
                for argument in [*node.args, *[item.value for item in node.keywords]]
                if lexical.namespace_mapping(argument)
            ]
            callable_kind = mutators.kind(node.func)
            mutates_owner = callable_kind == "bound" or (
                callable_kind == "unbound" and bool(owner_arguments)
            )
            mutates_namespace = callable_kind == "unbound" and bool(namespace_arguments)
            derived_receiver = isinstance(node.func, ast.Attribute) and (
                derived(node.func.value) or contains_owner(node.func.value)
            )
            unsafe_unknown_call = (
                reject_unknown_owner_calls
                and (bool(owner_arguments) or derived_receiver)
                and not read_only_owner_call(node)
            )
            tracked_callable_sink = (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in safe_sink_names
                and node.func.attr in MUTATING_METHODS
            )
            unsafe_owner_callable_escape = (
                reject_unknown_owner_calls
                and bool(owner_callable_arguments)
                and not tracked_callable_sink
            )
            mutates_global_namespace = (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in MUTATING_METHODS
                and lexical.namespace_mapping(node.func.value)
            )
            if (
                mutates_owner
                or mutates_namespace
                or lexical.protected_namespace_attribute_call(node, symbol)
                or unsafe_unknown_call
                or unsafe_owner_callable_escape
                or mutates_global_namespace
            ):
                mutations.append(node)
    return mutations


def _function_parameters(
    function: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda,
) -> list[ast.arg]:
    parameters = [
        *function.args.posonlyargs,
        *function.args.args,
        *function.args.kwonlyargs,
    ]
    if function.args.vararg is not None:
        parameters.append(function.args.vararg)
    if function.args.kwarg is not None:
        parameters.append(function.args.kwarg)
    return parameters


function_parameters = _function_parameters
literal_immutable_value = _literal_immutable_value
mutable_owner_mutations = _mutable_owner_mutations
root_name = _root_name
scope_bindings = _scope_bindings

__all__ = (
    "MUTATING_METHODS",
    "MutableOwnerAnalyzer",
    "function_parameters",
    "literal_immutable_value",
    "mutable_owner_mutations",
    "root_name",
    "scope_bindings",
)
