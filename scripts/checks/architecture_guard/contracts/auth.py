"""Authentication contract-ownership architecture policy."""

from __future__ import annotations

import ast
import json
import re

from scripts.checks.architecture_guard.python_analysis import (
    canonical_python_call,
    python_class_field_calls,
    python_extend_schema_success_responses,
    python_top_level_class_names,
)
from scripts.checks.architecture_guard.repository import (
    BACKEND,
    FRONTEND_SRC,
    PY_SUFFIXES,
    ROOT,
    TS_SUFFIXES,
    iter_files,
    rel,
)
from scripts.checks.architecture_guard.typescript_analysis import (
    normalized_ts_type,
    resolve_ts_static_string_expression,
    strip_outer_ts_parentheses,
    strip_ts_comments,
    ts_exported_top_level_adapter_uses_access,
    ts_exported_type_aliases,
    ts_exports_tainted_binding,
    ts_interface_declarations,
    ts_member_access_aliases,
    ts_named_import_bindings,
    ts_namespace_import_bindings,
    ts_object_method_body,
    ts_object_type_alias_bodies,
    ts_object_type_field_names,
    ts_reexports_all_from_module,
    ts_reexports_named_binding,
    ts_response_forwarding_bindings,
    ts_static_string_bindings,
    ts_type_aliases,
)

AUTH_BACKEND_SERIALIZERS = "backend/accounts/serializers.py"
AUTH_BACKEND_VIEWS = "backend/accounts/views.py"
AUTH_COMMON_OPENAPI = "backend/common/openapi.py"
AUTH_FRONTEND_TYPES = "frontend/src/shared/auth/types.ts"
AUTH_FRONTEND_API = "frontend/src/shared/auth/authApi.ts"
AUTH_HTTP_CLIENT = "frontend/src/shared/api/httpClient.ts"
AUTH_GENERATED_OPENAPI = "frontend/src/shared/api/generated/openapi.json"
AUTH_OPERATION_IDS = (
    "auth_register_create",
    "auth_login_create",
    "auth_logout_create",
    "auth_refresh_create",
    "auth_me_retrieve",
    "auth_password_reset_request_create",
    "auth_password_reset_confirm_create",
    "auth_password_change_create",
    "auth_sessions_revoke_others_create",
    "auth_sessions_revoke_all_create",
)


def auth_contract_source_violations(
    *,
    serializers_source: str,
    views_source: str,
    common_openapi_source: str,
    auth_types_source: str,
    auth_api_source: str,
    http_client_source: str,
) -> list[str]:
    """Check the canonical backend and frontend Auth contract sources."""

    violations: list[str] = []
    expected_serializer_fields = {
        "UserSerializer": {
            "id": "serializers.IntegerField()",
            "username": "serializers.CharField()",
            "email": "serializers.EmailField()",
            "is_staff": "serializers.BooleanField()",
        },
        "RegisterResponseSerializer": {"user": "UserSerializer()"},
        "SessionResponseSerializer": {
            "access": "serializers.CharField()",
            "user": "UserSerializer()",
        },
        "AccessTokenResponseSerializer": {"access": "serializers.CharField()"},
        "DetailResponseSerializer": {"detail": "serializers.CharField()"},
    }
    class_names = python_top_level_class_names(serializers_source)
    for class_name, expected_calls in expected_serializer_fields.items():
        actual_calls = python_class_field_calls(serializers_source, class_name)
        if class_names.count(class_name) != 1 or actual_calls != expected_calls:
            violations.append(
                f"{AUTH_BACKEND_SERIALIZERS}: {class_name} must own its exact Auth fields"
            )

    response_serializer_names = set(expected_serializer_fields) - {"UserSerializer"}
    imported_from_owner: set[str] = set()
    try:
        views_tree = ast.parse(views_source)
    except SyntaxError:
        views_tree = ast.Module(body=[], type_ignores=[])
    for node in views_tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 0:
            if node.module == "accounts.serializers":
                imported_from_owner.update(item.name for item in node.names if item.asname is None)
            if node.module == "common.openapi" and any(
                item.name in response_serializer_names for item in node.names
            ):
                violations.append(
                    f"{AUTH_BACKEND_VIEWS}: Auth response serializers must not come from common.openapi"
                )
    missing_imports = sorted(response_serializer_names - imported_from_owner)
    if missing_imports:
        violations.append(
            f"{AUTH_BACKEND_VIEWS}: import canonical Auth response serializers from accounts; "
            f"missing={missing_imports}"
        )

    expected_view_responses = {
        ("RegisterAPIView", "post", 201): "RegisterResponseSerializer",
        ("LoginAPIView", "post", 200): "SessionResponseSerializer",
        ("RefreshAPIView", "post", 200): "AccessTokenResponseSerializer",
        ("LogoutAPIView", "post", 204): "None",
        ("PasswordResetRequestAPIView", "post", 200): "DetailResponseSerializer",
        ("PasswordResetConfirmAPIView", "post", 200): "DetailResponseSerializer",
        ("PasswordChangeAPIView", "post", 200): "SessionResponseSerializer",
        ("RevokeOtherSessionsAPIView", "post", 200): "DetailResponseSerializer",
        ("RevokeAllSessionsAPIView", "post", 204): "None",
        ("MeAPIView", "get", 200): "UserSerializer",
    }
    actual_view_responses = python_extend_schema_success_responses(views_source)
    for key, expected in expected_view_responses.items():
        if actual_view_responses.get(key) != expected:
            violations.append(
                f"{AUTH_BACKEND_VIEWS}: {key[0]}.{key[1]} {key[2]} must document {expected}"
            )

    displaced = {
        "DetailResponseSerializer",
        "AccessTokenResponseSerializer",
        "AuthUserResponseSerializer",
        "LoginResponseSerializer",
    }
    remaining = sorted(displaced & set(python_top_level_class_names(common_openapi_source)))
    if remaining:
        violations.append(
            f"{AUTH_COMMON_OPENAPI}: displaced Auth response contracts must stay deleted; "
            f"found={remaining}"
        )

    types_without_comments = strip_ts_comments(auth_types_source)
    type_aliases = ts_exported_type_aliases(types_without_comments)
    if {name: normalized_ts_type(body) for name, body in type_aliases.items()} != {
        "User": "ApiSchemas['User']"
    }:
        violations.append(
            f"{AUTH_FRONTEND_TYPES}: export only User derived exactly from ApiSchemas['User']"
        )
    if ts_interface_declarations(types_without_comments) or ts_object_type_alias_bodies(
        types_without_comments
    ):
        violations.append(f"{AUTH_FRONTEND_TYPES}: handwritten Auth response DTOs are not allowed")

    api_without_comments = strip_ts_comments(auth_api_source)
    expected_method_bodies = {
        "register": (
            "returnapiOperationRequest('auth_register_create','/auth/register/',{body:payload})"
        ),
        "login": ("returnapiOperationRequest('auth_login_create','/auth/login/',{body:payload})"),
        "logout": (
            "returnapiOperationRequest('auth_logout_create','/auth/logout/',{skipAuthRefresh:true})"
        ),
        "refresh": (
            "returnapiOperationRequest('auth_refresh_create','/auth/refresh/',"
            "{skipAuthRefresh:true})"
        ),
        "me": "returnapiOperationRequest('auth_me_retrieve','/auth/me/')",
        "requestPasswordReset": (
            "returnapiOperationRequest('auth_password_reset_request_create',"
            "'/auth/password-reset/request/',{body:payload,skipAuthRefresh:true})"
        ),
        "confirmPasswordReset": (
            "returnapiOperationRequest('auth_password_reset_confirm_create',"
            "'/auth/password-reset/confirm/',{body:payload,skipAuthRefresh:true})"
        ),
        "changePassword": (
            "returnapiOperationRequest('auth_password_change_create',"
            "'/auth/password-change/',{body:payload})"
        ),
        "revokeOtherSessions": (
            "returnapiOperationRequest('auth_sessions_revoke_others_create',"
            "'/auth/sessions/revoke-others/')"
        ),
        "revokeAllSessions": (
            "returnapiOperationRequest('auth_sessions_revoke_all_create',"
            "'/auth/sessions/revoke-all/')"
        ),
    }
    for method_name, expected_body in expected_method_bodies.items():
        body = ts_object_method_body(api_without_comments, method_name)
        actual_body = re.sub(
            r",(?=[})])",
            "",
            normalized_ts_type(body or "").replace(";", ""),
        )
        if actual_body != expected_body:
            violations.append(
                f"{AUTH_FRONTEND_API}: {method_name} must return its generated operation response directly"
            )
    for operation_id in AUTH_OPERATION_IDS:
        call = re.search(
            rf"\bapiOperationRequest(?P<generics>\s*<[^>]*>)?\s*\(\s*"
            rf"['\"]{operation_id}['\"]",
            api_without_comments,
            re.S,
        )
        if call is None:
            violations.append(f"{AUTH_FRONTEND_API}: missing generated {operation_id} request")
        elif call.group("generics"):
            violations.append(
                f"{AUTH_FRONTEND_API}: {operation_id} must not pass a custom response generic"
            )

    client_without_comments = strip_ts_comments(http_client_source)
    refresh_call = re.compile(
        r"\bapiRequest\s*<\s*ApiResponseBody\s*<\s*['\"]auth_refresh_create['\"]"
        r"\s*>\s*>\s*\(\s*['\"]/auth/refresh/['\"]",
        re.S,
    )
    auth_paths = re.findall(r"['\"]((?:/api)?/auth/[^'\"]*)['\"]", client_without_comments)
    if len(refresh_call.findall(client_without_comments)) != 1 or auth_paths != ["/auth/refresh/"]:
        violations.append(
            f"{AUTH_HTTP_CLIENT}: only refresh may use a raw Auth path and it must derive ApiResponseBody"
        )
    return violations


def is_auth_response_contract_symbol(name: str) -> bool:
    """Identify response-shaped Auth names without flagging state, messages, or props."""

    if name in {
        "User",
        "AuthResponse",
        "RegisterResponse",
        "SessionResponse",
        "RefreshResponse",
    }:
        return True
    if name.endswith(("State", "Message", "Props")):
        return False
    normalized = name.lower()
    return any(marker in normalized for marker in ("auth", "login", "session", "refresh")) and any(
        marker in normalized for marker in ("response", "result", "dto", "contract")
    )


def python_auth_response_contract_symbols(
    source: str,
    *,
    path_label: str | None = None,
) -> list[str]:
    """Find named, inherited, and aliased Auth response serializers."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    canonical = {
        "UserSerializer",
        "RegisterResponseSerializer",
        "SessionResponseSerializer",
        "AccessTokenResponseSerializer",
        "DetailResponseSerializer",
    }
    known_contracts = set(canonical)
    known_user_serializers = {"UserSerializer"}
    imported_contracts: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        absolute_owner = node.level == 0 and node.module == "accounts.serializers"
        relative_owner = (
            node.level == 1
            and node.module == "serializers"
            and path_label is not None
            and path_label.startswith("backend/accounts/")
        )
        if absolute_owner or relative_owner:
            local_contracts = {
                item.asname or item.name for item in node.names if item.name in canonical
            }
            imported_contracts.update(local_contracts)
            known_contracts.update(local_contracts)
            known_user_serializers.update(
                item.asname or item.name for item in node.names if item.name == "UserSerializer"
            )

    def references_contract(value: ast.expr | None) -> bool:
        if value is None:
            return False
        return any(
            (isinstance(child, ast.Name) and child.id in known_contracts)
            or (isinstance(child, ast.Attribute) and child.attr in canonical)
            for child in ast.walk(value)
        )

    symbols: list[str] = []
    symbol_set: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                normalized = node.name.lower()
                field_values: dict[str, ast.expr | None] = {}
                for statement in node.body:
                    if isinstance(statement, ast.Assign):
                        field_values.update(
                            {
                                target.id: statement.value
                                for target in statement.targets
                                if isinstance(target, ast.Name)
                            }
                        )
                    elif isinstance(statement, ast.AnnAssign) and isinstance(
                        statement.target,
                        ast.Name,
                    ):
                        field_values[statement.target.id] = statement.value
                field_calls = {
                    name: canonical_python_call(value) for name, value in field_values.items()
                }
                serializer_based = any(
                    "serializer" in ast.unparse(base).lower() for base in node.bases
                )
                exact_user_shape = serializer_based and field_calls == {
                    "id": "serializers.IntegerField()",
                    "username": "serializers.CharField()",
                    "email": "serializers.EmailField()",
                    "is_staff": "serializers.BooleanField()",
                }

                def is_canonical_user_field(value: ast.expr | None) -> bool:
                    return (
                        isinstance(value, ast.Call)
                        and not value.args
                        and not value.keywords
                        and (
                            isinstance(value.func, ast.Name)
                            and value.func.id in known_user_serializers
                            or isinstance(value.func, ast.Attribute)
                            and value.func.attr == "UserSerializer"
                        )
                    )

                has_canonical_user = is_canonical_user_field(field_values.get("user"))
                exact_register_shape = (
                    serializer_based and set(field_values) == {"user"} and has_canonical_user
                )
                exact_session_shape = (
                    serializer_based
                    and set(field_values) == {"access", "user"}
                    and field_calls.get("access") == "serializers.CharField()"
                    and has_canonical_user
                )
                auth_named = node.name in canonical or (
                    node.name.endswith("Serializer")
                    and any(
                        marker in normalized for marker in ("auth", "login", "session", "refresh")
                    )
                    and any(
                        marker in normalized for marker in ("response", "result", "dto", "contract")
                    )
                )
                owns_contract = (
                    auth_named
                    or any(references_contract(base) for base in node.bases)
                    or exact_user_shape
                    or exact_register_shape
                    or exact_session_shape
                )
                if owns_contract and node.name not in symbol_set:
                    symbols.append(node.name)
                    symbol_set.add(node.name)
                    known_contracts.add(node.name)
                    if exact_user_shape:
                        known_user_serializers.add(node.name)
                    changed = True
                continue

            names: list[str] = []
            value: ast.expr | None = None
            if isinstance(node, ast.Assign):
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names = [node.target.id]
                value = node.value
            if references_contract(value):
                for name in names:
                    if name not in symbol_set:
                        symbols.append(name)
                        symbol_set.add(name)
                        known_contracts.add(name)
                        changed = True
    exported_names: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        ):
            continue
        if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
            exported_names.update(
                item.value
                for item in node.value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            )
    for name in sorted(imported_contracts & exported_names):
        if name not in symbol_set:
            symbols.append(name)
    return symbols


def auth_secondary_backend_contract_violations(
    path_sources: dict[str, str],
) -> list[str]:
    """Reject Auth response serializers outside the Accounts contract owner."""

    violations: list[str] = []
    for path_label, source in sorted(path_sources.items()):
        for symbol in python_auth_response_contract_symbols(
            source,
            path_label=path_label,
        ):
            violations.append(
                f"{path_label}: secondary Auth response contract {symbol} is not allowed"
            )
    return violations


def auth_secondary_frontend_contract_violations(
    path_sources: dict[str, str],
) -> list[str]:
    """Reject secondary Auth response roots, operation wrappers, and raw endpoints."""

    violations: list[str] = []
    response_schemas = {
        "RegisterResponse",
        "SessionResponse",
        "AccessTokenResponse",
        "DetailResponse",
    }
    operation_pattern = "|".join(re.escape(item) for item in AUTH_OPERATION_IDS)
    for path_label, raw_source in sorted(path_sources.items()):
        source = strip_ts_comments(raw_source)
        api_module = "@/shared/auth/authApi"
        auth_members = {
            "register",
            "login",
            "logout",
            "refresh",
            "me",
            "requestPasswordReset",
            "confirmPasswordReset",
            "changePassword",
            "revokeOtherSessions",
            "revokeAllSessions",
        }
        api_bindings = {"authApi"} | ts_named_import_bindings(
            source,
            path_label=path_label,
            module=api_module,
            exported_names={"authApi"},
        )
        api_bindings.update(
            f"{namespace}.authApi"
            for namespace in ts_namespace_import_bindings(
                source,
                path_label=path_label,
                module=api_module,
            )
        )
        access_patterns, tainted_bindings = ts_member_access_aliases(
            source,
            object_bindings=api_bindings,
            member_names=auth_members,
        )
        response_forwarding_bindings = ts_response_forwarding_bindings(
            source,
            access_patterns,
        )
        aliases = ts_type_aliases(source)
        schema_bindings = ts_named_import_bindings(
            source,
            path_label=path_label,
            module="@/shared/api/generated/apiTypes",
            exported_names={"ApiSchemas"},
        ) or {"ApiSchemas"}
        tainted_aliases: set[str] = set()
        changed = True
        while changed:
            changed = False
            for name, body in aliases.items():
                normalized = normalized_ts_type(strip_outer_ts_parentheses(body))
                generated_root = any(
                    re.search(
                        rf"\b{re.escape(binding)}\['(?:{'|'.join(sorted(response_schemas))})'\]",
                        normalized,
                    )
                    for binding in schema_bindings
                )
                derived_root = any(
                    re.search(rf"\b{re.escape(alias)}\b", normalized) for alias in tainted_aliases
                )
                return_type_root = any(
                    re.search(
                        rf"ReturnType<typeof{re.escape(binding)}\."
                        rf"(?:{'|'.join(sorted(auth_members))})>",
                        normalized,
                    )
                    for binding in api_bindings
                ) or any(
                    re.search(
                        rf"ReturnType<typeof{re.escape(binding)}>",
                        normalized,
                    )
                    for binding in response_forwarding_bindings
                )
                if (
                    generated_root or derived_root or return_type_root
                ) and name not in tainted_aliases:
                    tainted_aliases.add(name)
                    changed = True

        object_aliases = ts_object_type_alias_bodies(source)
        interfaces = ts_interface_declarations(source)
        structural_contracts = {
            name
            for name, body in object_aliases.items()
            if not name.endswith(("State", "Message", "Props"))
            and ts_object_type_field_names(body) == {"access", "user"}
        }
        structural_contracts.update(
            name
            for name, (_, body) in interfaces.items()
            if not name.endswith(("State", "Message", "Props"))
            and ts_object_type_field_names(body) == {"access", "user"}
        )
        declared_names = set(aliases) | set(interfaces)
        named_contracts = {
            name for name in declared_names if is_auth_response_contract_symbol(name)
        }
        secondary_contracts = sorted(tainted_aliases | structural_contracts | named_contracts)
        if secondary_contracts:
            violations.append(
                f"{path_label}: secondary frontend Auth response contracts are not allowed; "
                f"found={secondary_contracts}"
            )
        if re.search(rf"['\"](?:{operation_pattern})['\"]", source):
            violations.append(
                f"{path_label}: Auth generated operation wrapper is owned by {AUTH_FRONTEND_API}"
            )
        string_bindings = ts_static_string_bindings(source)
        resolved_request_paths = {
            resolved
            for match in re.finditer(
                r"\b(?:apiRequest|fetch)(?:\s*<[^>]*>)?\s*\(\s*"
                r"(?P<expression>[^,\r\n)]+)",
                source,
                re.S,
            )
            if (
                resolved := resolve_ts_static_string_expression(
                    match.group("expression"),
                    string_bindings,
                )
            )
            is not None
        }
        raw_literal = re.search(r"['\"](?:/api)?/auth/[^'\"]*['\"]", source)
        static_request = any(
            path.startswith(("/auth/", "/api/auth/")) for path in resolved_request_paths
        )
        if raw_literal or static_request:
            violations.append(f"{path_label}: raw Auth endpoint request path is not allowed")

        arrow_bindings = set(
            re.findall(
                r"\b(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*=\s*"
                r"(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>",
                source,
            )
        )
        exported_adapter = (
            ts_exported_top_level_adapter_uses_access(source, access_patterns)
            or ts_exports_tainted_binding(
                source,
                tainted_bindings - arrow_bindings,
            )
            or ts_reexports_named_binding(
                source,
                path_label=path_label,
                module=api_module,
                exported_names={"authApi"},
            )
            or ts_reexports_all_from_module(
                source,
                path_label=path_label,
                module=api_module,
            )
        )
        if exported_adapter:
            violations.append(
                f"{path_label}: secondary exported Auth response adapter is not allowed"
            )
    return violations


def auth_openapi_contract_violations(schema: dict) -> list[str]:
    """Check exact Auth components, nested User references, and success responses."""

    violations: list[str] = []
    schemas = schema.get("components", {}).get("schemas", {})
    expected_components = {
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "is_staff": {"type": "boolean"},
            },
            "required": ["email", "id", "is_staff", "username"],
        },
        "RegisterResponse": {
            "type": "object",
            "properties": {"user": {"$ref": "#/components/schemas/User"}},
            "required": ["user"],
        },
        "SessionResponse": {
            "type": "object",
            "properties": {
                "access": {"type": "string"},
                "user": {"$ref": "#/components/schemas/User"},
            },
            "required": ["access", "user"],
        },
        "AccessTokenResponse": {
            "type": "object",
            "properties": {"access": {"type": "string"}},
            "required": ["access"],
        },
        "DetailResponse": {
            "type": "object",
            "properties": {"detail": {"type": "string"}},
            "required": ["detail"],
        },
    }
    for name, expected in expected_components.items():
        if schemas.get(name) != expected:
            violations.append(
                f"{AUTH_GENERATED_OPENAPI}: {name} component must be exact and closed"
            )
    for displaced in ("AuthUserResponse", "LoginResponse"):
        if displaced in schemas:
            violations.append(
                f"{AUTH_GENERATED_OPENAPI}: displaced {displaced} component must stay deleted"
            )

    expected_operations = {
        ("/api/auth/register/", "post", "201"): "RegisterResponse",
        ("/api/auth/login/", "post", "200"): "SessionResponse",
        ("/api/auth/refresh/", "post", "200"): "AccessTokenResponse",
        ("/api/auth/me/", "get", "200"): "User",
        ("/api/auth/password-reset/request/", "post", "200"): "DetailResponse",
        ("/api/auth/password-reset/confirm/", "post", "200"): "DetailResponse",
        ("/api/auth/password-change/", "post", "200"): "SessionResponse",
        ("/api/auth/sessions/revoke-others/", "post", "200"): "DetailResponse",
    }
    for (path, method, status_code), component_name in expected_operations.items():
        response = (
            schema.get("paths", {})
            .get(path, {})
            .get(method, {})
            .get("responses", {})
            .get(status_code, {})
        )
        response_schema = (
            response.get("content", {}).get("application/json", {}).get("schema", {})
            if isinstance(response, dict)
            else {}
        )
        if response_schema != {"$ref": f"#/components/schemas/{component_name}"}:
            violations.append(
                f"{AUTH_GENERATED_OPENAPI}: {method.upper()} {path} {status_code} must return {component_name}"
            )
    for path in ("/api/auth/logout/", "/api/auth/sessions/revoke-all/"):
        response = (
            schema.get("paths", {})
            .get(path, {})
            .get("post", {})
            .get("responses", {})
            .get("204", {})
        )
        if response != {"description": "No response body"}:
            violations.append(
                f"{AUTH_GENERATED_OPENAPI}: POST {path} 204 must have no response body"
            )
    return violations


def check_auth_contract_ownership() -> list[str]:
    """Keep Auth success contracts account-owned, generated, and one-way."""

    path_labels = (
        AUTH_BACKEND_SERIALIZERS,
        AUTH_BACKEND_VIEWS,
        AUTH_COMMON_OPENAPI,
        AUTH_FRONTEND_TYPES,
        AUTH_FRONTEND_API,
        AUTH_HTTP_CLIENT,
        AUTH_GENERATED_OPENAPI,
    )
    missing = [path for path in path_labels if not (ROOT / path).is_file()]
    if missing:
        return [f"{path}: required Auth contract owner is missing" for path in missing]

    violations = auth_contract_source_violations(
        serializers_source=(ROOT / AUTH_BACKEND_SERIALIZERS).read_text(encoding="utf-8"),
        views_source=(ROOT / AUTH_BACKEND_VIEWS).read_text(encoding="utf-8"),
        common_openapi_source=(ROOT / AUTH_COMMON_OPENAPI).read_text(encoding="utf-8"),
        auth_types_source=(ROOT / AUTH_FRONTEND_TYPES).read_text(encoding="utf-8"),
        auth_api_source=(ROOT / AUTH_FRONTEND_API).read_text(encoding="utf-8"),
        http_client_source=(ROOT / AUTH_HTTP_CLIENT).read_text(encoding="utf-8"),
    )
    secondary_backend_sources = {
        rel(path): path.read_text(encoding="utf-8", errors="ignore")
        for path in iter_files(BACKEND, PY_SUFFIXES)
        if rel(path) != AUTH_BACKEND_SERIALIZERS
        and not any(part in {"migrations", "tests"} for part in path.parts)
        and not path.name.startswith("test_")
    }
    violations.extend(auth_secondary_backend_contract_violations(secondary_backend_sources))
    secondary_frontend_sources = {
        rel(path): path.read_text(encoding="utf-8", errors="ignore")
        for path in iter_files(FRONTEND_SRC, TS_SUFFIXES)
        if rel(path) not in {AUTH_FRONTEND_TYPES, AUTH_FRONTEND_API, AUTH_HTTP_CLIENT}
        and "generated" not in path.parts
        and "preview" not in path.parts
        and ".test." not in path.name
        and ".spec." not in path.name
    }
    violations.extend(auth_secondary_frontend_contract_violations(secondary_frontend_sources))
    try:
        schema = json.loads((ROOT / AUTH_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        violations.append(f"{AUTH_GENERATED_OPENAPI}: invalid generated schema: {error}")
    else:
        violations.extend(auth_openapi_contract_violations(schema))
    return violations
