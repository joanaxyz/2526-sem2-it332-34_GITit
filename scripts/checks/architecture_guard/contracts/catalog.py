"""Catalog contract-ownership architecture policy."""

from __future__ import annotations

import ast
import json
import re

from scripts.checks.architecture_guard.python_analysis import (
    python_class_field_calls,
    python_class_fields,
    python_class_method_decorator_calls,
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
    strip_outer_ts_parentheses,
    strip_ts_comments,
    ts_exported_adapter_uses_access,
    ts_exported_type_aliases,
    ts_exports_tainted_binding,
    ts_interface_declarations,
    ts_member_access_aliases,
    ts_named_import_bindings,
    ts_object_method_body,
    ts_object_type_alias_bodies,
    ts_object_type_field_names,
    ts_reexports_named_binding,
    ts_type_aliases,
)

CATALOG_BACKEND_SERIALIZERS = "backend/curriculum/serializers.py"
CATALOG_FRONTEND_TYPES = "frontend/src/features/story-map/types.ts"
CATALOG_FRONTEND_API = "frontend/src/features/story-map/api/storyMapApi.ts"
CATALOG_GENERATED_OPENAPI = "frontend/src/shared/api/generated/openapi.json"
CATALOG_STORY_FIELDS = frozenset(
    {
        "id",
        "slug",
        "title",
        "summary",
        "price",
        "sort_order",
        "is_published",
        "completed",
        "owned",
        "world_slug",
        "difficulty",
        "prerequisite_story",
        "locked",
        "lock_reason",
    }
)
CATALOG_CHAPTER_FIELDS = frozenset(
    {
        "id",
        "slug",
        "number",
        "title",
        "description",
        "sort_order",
        "is_playable",
        "command_skill_count",
        "challenge_count",
        "adventure_level_count",
        "level_completion",
        "story",
        "locked",
        "lock_reason",
        "chest_schedule",
    }
)
CATALOG_RESPONSE_FIELD_SETS = {CATALOG_STORY_FIELDS, CATALOG_CHAPTER_FIELDS}


def is_catalog_contract_symbol(name: str) -> bool:
    """Identify Story/Chapter catalog response-serializer symbols."""

    if name.startswith(("Admin", "Authoring")) or name.endswith(
        ("APIView", "View", "ViewSet", "Model", "Admin")
    ):
        return False
    normalized = name.lower()
    domain_named = "story" in normalized or "chapter" in normalized
    contract_named = any(
        marker in normalized
        for marker in (
            "serializer",
            "catalog",
            "response",
            "list",
            "prerequisite",
            "completion",
            "reward",
            "contract",
            "dto",
            "payload",
            "result",
        )
    )
    return domain_named and contract_named


def is_catalog_frontend_contract_symbol(name: str) -> bool:
    """Identify exact canonical frontend catalog names; structure handles shadows."""

    return name in {"Story", "LearningChapter"}


def is_catalog_root_type_expression(
    type_body: str,
    *,
    canonical_names: set[str] | None = None,
    schema_names: set[str] | None = None,
) -> bool:
    """Identify response aliases/refinements rooted in a canonical catalog type."""

    normalized = normalized_ts_type(strip_outer_ts_parentheses(type_body))
    names = canonical_names or {"Story", "LearningChapter"}
    schemas = schema_names or {"ApiSchemas"}
    named_root = "|".join(re.escape(name) for name in sorted(names))
    schema_root = "|".join(re.escape(name) for name in sorted(schemas))
    root = rf"(?:(?:{schema_root})\['(?:Story|ChapterList)'\]|(?:{named_root}))"
    return bool(
        re.fullmatch(root, normalized) or re.search(rf"(?:^|[&|]){root}(?:$|[&|])", normalized)
    )


def python_catalog_contract_symbols(
    source: str,
    *,
    path_label: str | None = None,
) -> list[str]:
    """Find named, structurally copied, and aliased catalog serializers."""

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    canonical_serializers = {
        "StorySerializer",
        "ChapterListSerializer",
        "StoryPrerequisiteSerializer",
        "ChapterStorySerializer",
        "ChapterLevelCompletionSerializer",
        "ChapterChestRewardSerializer",
    }
    known_contracts = set(canonical_serializers)
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        absolute_owner = node.level == 0 and node.module == "curriculum.serializers"
        relative_owner = (
            node.level == 1
            and node.module == "serializers"
            and path_label is not None
            and path_label.startswith("backend/curriculum/")
        )
        if not (absolute_owner or relative_owner):
            continue
        for imported in node.names:
            if imported.name in canonical_serializers:
                known_contracts.add(imported.asname or imported.name)

    def expression_references_contract(value: ast.expr | None) -> bool:
        if value is None:
            return False
        for child in ast.walk(value):
            if isinstance(child, ast.Name) and child.id in known_contracts:
                return True
            if isinstance(child, ast.Attribute) and child.attr in canonical_serializers:
                return True
        return False

    symbols: list[str] = []
    symbol_set: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                fields: set[str] = set()
                for statement in node.body:
                    if isinstance(statement, ast.Assign):
                        fields.update(
                            target.id
                            for target in statement.targets
                            if isinstance(target, ast.Name)
                        )
                    elif isinstance(statement, ast.AnnAssign) and isinstance(
                        statement.target, ast.Name
                    ):
                        fields.add(statement.target.id)
                catalog_base = any(expression_references_contract(base) for base in node.bases)
                serializer_based = catalog_base or any(
                    "serializer" in ast.unparse(base).lower() for base in node.bases
                )
                structural_copy = serializer_based and any(
                    fields >= expected for expected in CATALOG_RESPONSE_FIELD_SETS
                )
                owns_contract = serializer_based and (
                    catalog_base or is_catalog_contract_symbol(node.name) or structural_copy
                )
                if owns_contract and node.name not in symbol_set:
                    symbols.append(node.name)
                    symbol_set.add(node.name)
                    known_contracts.add(node.name)
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
            if names and expression_references_contract(value):
                for name in names:
                    if name not in symbol_set and name not in canonical_serializers:
                        symbols.append(name)
                        symbol_set.add(name)
                        known_contracts.add(name)
                        changed = True
    return symbols


def catalog_secondary_backend_contract_violations(
    path_sources: dict[str, str],
) -> list[str]:
    """Reject Story/Chapter catalog serializers outside the Curriculum owner."""

    violations: list[str] = []
    for path_label, source in sorted(path_sources.items()):
        for symbol in python_catalog_contract_symbols(source, path_label=path_label):
            violations.append(
                f"{path_label}: secondary catalog response contract {symbol} is not allowed"
            )
    return violations


def catalog_secondary_frontend_contract_violations(
    path_sources: dict[str, str],
) -> list[str]:
    """Reject secondary catalog DTOs, operation wrappers, and endpoint clients."""

    violations: list[str] = []
    for path_label, source in sorted(path_sources.items()):
        without_comments = strip_ts_comments(source)
        canonical_names = {"Story", "LearningChapter"} | ts_named_import_bindings(
            without_comments,
            path_label=path_label,
            module="@/features/story-map/types",
            exported_names={"Story", "LearningChapter"},
        )
        schema_names = {"ApiSchemas"} | ts_named_import_bindings(
            without_comments,
            path_label=path_label,
            module="@/shared/api/generated/apiTypes",
            exported_names={"ApiSchemas"},
        )
        aliases = ts_type_aliases(without_comments)
        object_aliases = ts_object_type_alias_bodies(without_comments)
        interfaces = ts_interface_declarations(without_comments)
        contract_names = {
            name
            for name, body in aliases.items()
            if is_catalog_frontend_contract_symbol(name)
            or is_catalog_root_type_expression(
                body,
                canonical_names=canonical_names,
                schema_names=schema_names,
            )
            or any(
                ts_object_type_field_names(object_aliases.get(name, "")) >= expected
                for expected in CATALOG_RESPONSE_FIELD_SETS
            )
        }
        contract_names.update(
            name
            for name, (extends, body) in interfaces.items()
            if is_catalog_frontend_contract_symbol(name)
            or any(
                re.search(rf"\b{re.escape(canonical)}\b", extends) for canonical in canonical_names
            )
            or any(
                ts_object_type_field_names(body) >= expected
                for expected in CATALOG_RESPONSE_FIELD_SETS
            )
        )
        for name in sorted(contract_names):
            violations.append(
                f"{path_label}: secondary frontend catalog contract {name} is not allowed"
            )
        operation_ids = sorted(
            set(re.findall(r"\b(?:stories_list|chapters_list)\b", without_comments))
        )
        for operation_id in operation_ids:
            violations.append(
                f"{path_label}: secondary catalog operation wrapper {operation_id} is not allowed"
            )
        catalog_path = r"['\"`]/(?:api/)?(?:stories|chapters)/"
        endpoint_bindings = {
            match.group("name")
            for match in re.finditer(
                rf"\b(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*"
                rf"{catalog_path}",
                without_comments,
            )
        }
        path_aliases = [
            (match.group("name"), match.group("expression").strip())
            for match in re.finditer(
                r"\b(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*"
                r"(?P<expression>[A-Za-z_$][\w$]*)\s*;?",
                without_comments,
            )
        ]
        changed = True
        while changed:
            changed = False
            for name, expression in path_aliases:
                if expression in endpoint_bindings and name not in endpoint_bindings:
                    endpoint_bindings.add(name)
                    changed = True
        direct_endpoint = re.search(
            rf"\b(?:apiRequest|fetch)(?:\s*<[^>]*>)?\s*\(\s*{catalog_path}",
            without_comments,
            re.S,
        )
        bound_endpoint = any(
            re.search(
                rf"\b(?:apiRequest|fetch)(?:\s*<[^>]*>)?\s*\(\s*"
                rf"{re.escape(binding)}\b",
                without_comments,
                re.S,
            )
            for binding in endpoint_bindings
        )
        if direct_endpoint or bound_endpoint:
            violations.append(
                f"{path_label}: secondary catalog endpoint request path is not allowed"
            )

        api_module = "@/features/story-map/api/storyMapApi"
        api_bindings = {"storyMapApi"} | ts_named_import_bindings(
            without_comments,
            path_label=path_label,
            module=api_module,
            exported_names={"storyMapApi"},
        )
        access_patterns, tainted_bindings = ts_member_access_aliases(
            without_comments,
            object_bindings=api_bindings,
            member_names={"listStories", "listChapters"},
        )
        exported_adapter = (
            ts_exported_adapter_uses_access(without_comments, access_patterns)
            or ts_exports_tainted_binding(without_comments, tainted_bindings)
            or ts_reexports_named_binding(
                without_comments,
                path_label=path_label,
                module=api_module,
                exported_names={"storyMapApi"},
            )
        )
        if exported_adapter:
            violations.append(
                f"{path_label}: secondary exported catalog response adapter is not allowed"
            )
    return violations


def catalog_contract_source_violations(
    *,
    serializers_source: str,
    story_types_source: str,
    story_api_source: str,
) -> list[str]:
    """Enforce exact Curriculum ownership and generated-only catalog consumers."""

    violations: list[str] = []
    expected_serializer_fields = {
        "StoryPrerequisiteSerializer": {
            "slug": "serializers.CharField()",
            "title": "serializers.CharField()",
            "completed": "serializers.BooleanField()",
        },
        "ChapterStorySerializer": {
            "id": "serializers.IntegerField()",
            "slug": "serializers.CharField()",
            "title": "serializers.CharField()",
            "world_slug": "serializers.CharField()",
        },
        "ChapterLevelCompletionSerializer": {
            "value": "serializers.FloatField()",
            "numerator": "serializers.IntegerField()",
            "denominator": "serializers.IntegerField()",
        },
        "ChapterChestRewardSerializer": {
            "threshold": "serializers.IntegerField()",
            "coins": "serializers.IntegerField()",
        },
        "StorySerializer": {
            "id": "serializers.IntegerField(read_only=True)",
            "slug": "serializers.CharField(read_only=True)",
            "title": "serializers.CharField(read_only=True)",
            "summary": "serializers.CharField(read_only=True)",
            "price": "serializers.IntegerField(read_only=True)",
            "sort_order": "serializers.IntegerField(read_only=True)",
            "is_published": "serializers.BooleanField(read_only=True)",
            "completed": "serializers.SerializerMethodField()",
            "owned": "serializers.SerializerMethodField()",
            "world_slug": "serializers.CharField(read_only=True)",
            "difficulty": (
                "serializers.ChoiceField(choices=Story.DIFFICULTY_CHOICES,read_only=True)"
            ),
            "prerequisite_story": "serializers.SerializerMethodField()",
            "locked": "serializers.SerializerMethodField()",
            "lock_reason": "serializers.SerializerMethodField()",
        },
        "ChapterListSerializer": {
            "id": "serializers.IntegerField(read_only=True)",
            "slug": "serializers.CharField(read_only=True)",
            "number": "serializers.IntegerField(read_only=True)",
            "title": "serializers.CharField(read_only=True)",
            "description": "serializers.CharField(read_only=True)",
            "sort_order": "serializers.IntegerField(read_only=True)",
            "is_playable": "serializers.BooleanField(read_only=True)",
            "command_skill_count": "serializers.IntegerField(read_only=True)",
            "challenge_count": "serializers.IntegerField(read_only=True)",
            "adventure_level_count": "serializers.IntegerField(read_only=True)",
            "level_completion": "serializers.SerializerMethodField()",
            "story": "serializers.SerializerMethodField()",
            "locked": "serializers.SerializerMethodField()",
            "lock_reason": "serializers.SerializerMethodField()",
            "chest_schedule": "serializers.SerializerMethodField()",
        },
    }
    class_names = python_top_level_class_names(serializers_source)
    for class_name, expected_calls in expected_serializer_fields.items():
        fields = python_class_fields(serializers_source, class_name)
        if fields is None or class_names.count(class_name) != 1:
            violations.append(
                f"{CATALOG_BACKEND_SERIALIZERS}: require exactly one canonical {class_name}"
            )
        elif fields != set(expected_calls):
            violations.append(
                f"{CATALOG_BACKEND_SERIALIZERS}: {class_name} fields must be exactly "
                f"{sorted(expected_calls)}; found {sorted(fields)}"
            )
        elif python_class_field_calls(serializers_source, class_name) != expected_calls:
            violations.append(
                f"{CATALOG_BACKEND_SERIALIZERS}: {class_name} field signatures must be exact"
            )

    expected_decorators = {
        ("StorySerializer", "get_prerequisite_story"): (
            "extend_schema_field(StoryPrerequisiteSerializer(allow_null=True))"
        ),
        ("ChapterListSerializer", "get_level_completion"): (
            "extend_schema_field(ChapterLevelCompletionSerializer())"
        ),
        ("ChapterListSerializer", "get_story"): (
            "extend_schema_field(ChapterStorySerializer(allow_null=True))"
        ),
        ("ChapterListSerializer", "get_chest_schedule"): (
            "extend_schema_field(ChapterChestRewardSerializer(many=True))"
        ),
    }
    for (class_name, method_name), expected_decorator in expected_decorators.items():
        decorators = python_class_method_decorator_calls(
            serializers_source,
            class_name,
            method_name,
        )
        if decorators != [expected_decorator]:
            violations.append(
                f"{CATALOG_BACKEND_SERIALIZERS}: {class_name}.{method_name} must use "
                f"exactly @{expected_decorator}"
            )

    allowed_contracts = set(expected_serializer_fields)
    for name in python_catalog_contract_symbols(serializers_source):
        if name not in allowed_contracts:
            violations.append(
                f"{CATALOG_BACKEND_SERIALIZERS}: secondary catalog contract {name} is not allowed"
            )

    types_without_comments = strip_ts_comments(story_types_source)
    aliases = ts_exported_type_aliases(types_without_comments)
    expected_aliases = {
        "Story": "ApiSchemas['Story']",
        "LearningChapter": "ApiSchemas['ChapterList']",
    }
    for name, expected in expected_aliases.items():
        if normalized_ts_type(aliases.get(name, "")) != normalized_ts_type(expected):
            violations.append(
                f"{CATALOG_FRONTEND_TYPES}: {name} must derive exactly from {expected}"
            )
    all_aliases = ts_type_aliases(types_without_comments)
    object_aliases = ts_object_type_alias_bodies(types_without_comments)
    interfaces = ts_interface_declarations(types_without_comments)
    for displaced in ("ChapterLevelMetric", "ChestReward"):
        if displaced in all_aliases:
            violations.append(
                f"{CATALOG_FRONTEND_TYPES}: displaced catalog DTO {displaced} must stay deleted"
            )
    extra_catalog_aliases = sorted(
        name
        for name, body in all_aliases.items()
        if name not in expected_aliases
        and (
            is_catalog_frontend_contract_symbol(name)
            or is_catalog_root_type_expression(body)
            or any(
                ts_object_type_field_names(object_aliases.get(name, "")) >= expected
                for expected in CATALOG_RESPONSE_FIELD_SETS
            )
        )
    )
    extra_catalog_interfaces = sorted(
        name
        for name, (extends, body) in interfaces.items()
        if is_catalog_frontend_contract_symbol(name)
        or bool(re.search(r"\b(?:Story|LearningChapter)\b", extends))
        or any(
            ts_object_type_field_names(body) >= expected for expected in CATALOG_RESPONSE_FIELD_SETS
        )
    )
    if extra_catalog_aliases or extra_catalog_interfaces:
        violations.append(
            f"{CATALOG_FRONTEND_TYPES}: secondary catalog DTOs are not allowed; "
            f"aliases={extra_catalog_aliases}, interfaces={extra_catalog_interfaces}"
        )

    api_without_comments = strip_ts_comments(story_api_source)
    expected_method_bodies = {
        "listStories": ("returnapiOperationRequest('stories_list','/stories/')"),
        "listChapters": (
            "constquery=storySlug?`?story=${encodeURIComponent(storySlug)}`:''"
            "returnapiOperationRequest('chapters_list',`/chapters/${query}`)"
        ),
    }
    for method_name, expected_body in expected_method_bodies.items():
        body = ts_object_method_body(api_without_comments, method_name)
        actual_body = normalized_ts_type(body).replace(";", "") if body is not None else ""
        if actual_body != expected_body:
            violations.append(
                f"{CATALOG_FRONTEND_API}: {method_name} must return the generated operation "
                "response directly"
            )
    for operation_id in ("stories_list", "chapters_list"):
        call = re.search(
            rf"\bapiOperationRequest(?P<generics>\s*<[^>]*>)?\s*\(\s*"
            rf"['\"]{operation_id}['\"]",
            api_without_comments,
            re.S,
        )
        if call is None:
            violations.append(f"{CATALOG_FRONTEND_API}: missing generated {operation_id} request")
        elif call.group("generics") and "," in call.group("generics"):
            violations.append(
                f"{CATALOG_FRONTEND_API}: {operation_id} must not pass a custom response generic"
            )
    return violations


def catalog_openapi_contract_violations(schema: dict) -> list[str]:
    """Check exact catalog component fields, nested schemas, and operations."""

    violations: list[str] = []
    schemas = schema.get("components", {}).get("schemas", {})
    expected_properties = {
        "StoryPrerequisite": {
            "slug": {"type": "string"},
            "title": {"type": "string"},
            "completed": {"type": "boolean"},
        },
        "Story": {
            "id": {"type": "integer", "readOnly": True},
            "slug": {"type": "string", "readOnly": True},
            "title": {"type": "string", "readOnly": True},
            "summary": {"type": "string", "readOnly": True},
            "price": {"type": "integer", "readOnly": True},
            "sort_order": {"type": "integer", "readOnly": True},
            "is_published": {"type": "boolean", "readOnly": True},
            "completed": {"type": "boolean", "readOnly": True},
            "owned": {"type": "boolean", "readOnly": True},
            "world_slug": {"type": "string", "readOnly": True},
            "difficulty": {
                "allOf": [{"$ref": "#/components/schemas/DifficultyEnum"}],
                "readOnly": True,
            },
            "prerequisite_story": {
                "allOf": [{"$ref": "#/components/schemas/StoryPrerequisite"}],
                "nullable": True,
                "readOnly": True,
            },
            "locked": {"type": "boolean", "readOnly": True},
            "lock_reason": {"type": "string", "readOnly": True},
        },
        "ChapterStory": {
            "id": {"type": "integer"},
            "slug": {"type": "string"},
            "title": {"type": "string"},
            "world_slug": {"type": "string"},
        },
        "ChapterLevelCompletion": {
            "value": {"type": "number", "format": "double"},
            "numerator": {"type": "integer"},
            "denominator": {"type": "integer"},
        },
        "ChapterChestReward": {
            "threshold": {"type": "integer"},
            "coins": {"type": "integer"},
        },
        "ChapterList": {
            "id": {"type": "integer", "readOnly": True},
            "slug": {"type": "string", "readOnly": True},
            "number": {"type": "integer", "readOnly": True},
            "title": {"type": "string", "readOnly": True},
            "description": {"type": "string", "readOnly": True},
            "sort_order": {"type": "integer", "readOnly": True},
            "is_playable": {"type": "boolean", "readOnly": True},
            "command_skill_count": {"type": "integer", "readOnly": True},
            "challenge_count": {"type": "integer", "readOnly": True},
            "adventure_level_count": {"type": "integer", "readOnly": True},
            "level_completion": {
                "allOf": [{"$ref": "#/components/schemas/ChapterLevelCompletion"}],
                "readOnly": True,
            },
            "story": {
                "allOf": [{"$ref": "#/components/schemas/ChapterStory"}],
                "nullable": True,
                "readOnly": True,
            },
            "locked": {"type": "boolean", "readOnly": True},
            "lock_reason": {"type": "string", "readOnly": True},
            "chest_schedule": {
                "type": "array",
                "items": {"$ref": "#/components/schemas/ChapterChestReward"},
                "readOnly": True,
            },
        },
    }
    for schema_name, expected in expected_properties.items():
        component = schemas.get(schema_name)
        actual = component.get("properties", {}) if isinstance(component, dict) else {}
        required = set(component.get("required", [])) if isinstance(component, dict) else set()
        if (
            not isinstance(component, dict)
            or component.get("type") != "object"
            or set(actual) != set(expected)
            or required != set(expected)
        ):
            violations.append(
                f"{CATALOG_GENERATED_OPENAPI}: {schema_name} properties/required must be "
                f"exactly {sorted(expected)}"
            )
        if actual != expected:
            violations.append(
                f"{CATALOG_GENERATED_OPENAPI}: {schema_name} property schemas must be exact"
            )

    for path, item_schema in (
        ("/api/stories/", "Story"),
        ("/api/chapters/", "ChapterList"),
    ):
        response_schema = (
            schema.get("paths", {})
            .get(path, {})
            .get("get", {})
            .get("responses", {})
            .get("200", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        expected_response = {
            "type": "array",
            "items": {"$ref": f"#/components/schemas/{item_schema}"},
        }
        if response_schema != expected_response:
            violations.append(
                f"{CATALOG_GENERATED_OPENAPI}: {path} must return an array of {item_schema}"
            )
    return violations


def check_catalog_contract_ownership() -> list[str]:
    """Keep Story/Chapter catalog runtime and generated contracts one-way."""

    path_labels = (
        CATALOG_BACKEND_SERIALIZERS,
        CATALOG_FRONTEND_TYPES,
        CATALOG_FRONTEND_API,
        CATALOG_GENERATED_OPENAPI,
    )
    missing = [path for path in path_labels if not (ROOT / path).is_file()]
    if missing:
        return [f"{path}: required catalog contract owner is missing" for path in missing]

    serializers_source = (ROOT / CATALOG_BACKEND_SERIALIZERS).read_text(encoding="utf-8")
    violations = catalog_contract_source_violations(
        serializers_source=serializers_source,
        story_types_source=(ROOT / CATALOG_FRONTEND_TYPES).read_text(encoding="utf-8"),
        story_api_source=(ROOT / CATALOG_FRONTEND_API).read_text(encoding="utf-8"),
    )
    secondary_backend_sources = {
        rel(path): path.read_text(encoding="utf-8", errors="ignore")
        for path in iter_files(BACKEND, PY_SUFFIXES)
        if rel(path) != CATALOG_BACKEND_SERIALIZERS
        and not any(part in {"migrations", "tests"} for part in path.parts)
        and not path.name.startswith("test_")
    }
    violations.extend(catalog_secondary_backend_contract_violations(secondary_backend_sources))
    secondary_frontend_sources = {
        rel(path): path.read_text(encoding="utf-8", errors="ignore")
        for path in iter_files(FRONTEND_SRC, TS_SUFFIXES)
        if rel(path) not in {CATALOG_FRONTEND_TYPES, CATALOG_FRONTEND_API}
        and "generated" not in path.parts
        and "preview" not in path.parts
        and ".test." not in path.name
        and ".spec." not in path.name
    }
    violations.extend(catalog_secondary_frontend_contract_violations(secondary_frontend_sources))
    try:
        schema = json.loads((ROOT / CATALOG_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        violations.append(f"{CATALOG_GENERATED_OPENAPI}: invalid generated schema: {error}")
    else:
        violations.extend(catalog_openapi_contract_violations(schema))
    return violations
