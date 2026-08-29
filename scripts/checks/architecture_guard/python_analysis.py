"""Pure Python source-analysis helpers for architecture policies."""

from __future__ import annotations

import ast


def python_class_fields(source: str, class_name: str) -> set[str] | None:
    """Return names assigned directly on a Python class, or None when absent."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        fields: set[str] = set()
        for statement in node.body:
            if isinstance(statement, ast.Assign):
                fields.update(
                    target.id for target in statement.targets if isinstance(target, ast.Name)
                )
            elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                fields.add(statement.target.id)
        return fields
    return None


def python_top_level_class_names(source: str) -> list[str]:
    """Return top-level Python class names in declaration order."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def python_top_level_assignment_names(source: str) -> list[str]:
    """Return names assigned at module scope."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names.extend(target.id for target in node.targets if isinstance(target, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.append(node.target.id)
    return names


def canonical_python_call(value: ast.expr | None) -> str:
    """Render a call signature with stable keyword ordering."""

    if value is None:
        return "<no-value>"
    if not isinstance(value, ast.Call):
        return f"<non-call:{ast.unparse(value)}>"
    arguments = [ast.unparse(argument) for argument in value.args]
    arguments.extend(
        (
            f"{keyword.arg}={ast.unparse(keyword.value)}"
            if keyword.arg is not None
            else f"**{ast.unparse(keyword.value)}"
        )
        for keyword in sorted(value.keywords, key=lambda keyword: keyword.arg or "")
    )
    return f"{ast.unparse(value.func)}({','.join(arguments)})"


def python_class_field_calls(source: str, class_name: str) -> dict[str, str] | None:
    """Return canonical direct field-constructor calls for a Python class."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        calls: dict[str, str] = {}
        for statement in node.body:
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name):
                        calls[target.id] = canonical_python_call(statement.value)
            elif isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                calls[statement.target.id] = canonical_python_call(statement.value)
        return calls
    return None


def python_class_method_decorator_calls(
    source: str,
    class_name: str,
    method_name: str,
) -> list[str] | None:
    """Return canonical decorators for one method on one top-level class."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                statement.name == method_name
            ):
                return [canonical_python_call(item) for item in statement.decorator_list]
        return None
    return None


def python_class_method_called_names(
    source: str,
    class_name: str,
    method_name: str,
) -> set[str] | None:
    """Return direct-name call targets inside one top-level class method."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                statement.name == method_name
            ):
                return {
                    call.func.id
                    for call in ast.walk(statement)
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                }
        return None
    return None


def python_extend_schema_success_responses(
    source: str,
) -> dict[tuple[str, str, int], str]:
    """Return success response expressions declared on class-based view methods."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {}
    responses: dict[tuple[str, str, int], str] = {}
    for class_node in tree.body:
        if not isinstance(class_node, ast.ClassDef):
            continue
        for method in class_node.body:
            if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in method.decorator_list:
                if not isinstance(decorator, ast.Call) or not (
                    isinstance(decorator.func, ast.Name) and decorator.func.id == "extend_schema"
                ):
                    continue
                response_keyword = next(
                    (item for item in decorator.keywords if item.arg == "responses"),
                    None,
                )
                if response_keyword is None or not isinstance(response_keyword.value, ast.Dict):
                    continue
                for key, value in zip(
                    response_keyword.value.keys,
                    response_keyword.value.values,
                    strict=True,
                ):
                    if (
                        isinstance(key, ast.Constant)
                        and isinstance(key.value, int)
                        and 200 <= key.value < 300
                    ):
                        responses[(class_node.name, method.name, key.value)] = ast.unparse(value)
    return responses
