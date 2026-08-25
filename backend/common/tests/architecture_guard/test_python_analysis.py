"""Focused tests for reusable Python source-analysis helpers."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[4]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.python_analysis import (  # noqa: E402
    canonical_python_call,
    python_class_field_calls,
    python_class_fields,
    python_class_method_called_names,
    python_class_method_decorator_calls,
    python_extend_schema_success_responses,
    python_top_level_assignment_names,
    python_top_level_class_names,
)

del _TEST_IMPORT_ROOT


def test_python_declaration_parsers_preserve_order_and_scope() -> None:
    source = """
FIRST = object()
second: str = "value"

class Payload:
    plain = Field()
    annotated: str = Field(required=True)

    def method(self):
        nested = "ignored"

class Other:
    pass
"""

    assert python_top_level_class_names(source) == ["Payload", "Other"]
    assert python_top_level_assignment_names(source) == ["FIRST", "second"]
    assert python_class_fields(source, "Payload") == {"plain", "annotated"}
    assert python_class_fields(source, "Missing") is None


def test_python_call_parsers_canonicalize_fields_and_keyword_order() -> None:
    source = """
class Payload:
    plain = Field(required=True, allow_null=False)
    annotated: str = Nested(Item(), many=True)
    literal = "not a call"
"""

    calls = python_class_field_calls(source, "Payload")

    assert calls == {
        "plain": "Field(allow_null=False,required=True)",
        "annotated": "Nested(Item(),many=True)",
        "literal": "<non-call:'not a call'>",
    }
    expression = ast.parse("factory(value, z=3, a=1, **options)").body[0].value
    assert canonical_python_call(expression) == "factory(value,**options,a=1,z=3)"
    assert canonical_python_call(None) == "<no-value>"


def test_python_method_parsers_own_decorators_and_direct_calls() -> None:
    source = """
class View:
    @permission_classes([Allowed])
    @extend_schema(tags=["account"], operation_id="account_read")
    async def get(self):
        direct()
        service.execute()
        return finish()
"""

    assert python_class_method_decorator_calls(source, "View", "get") == [
        "permission_classes([Allowed])",
        "extend_schema(operation_id='account_read',tags=['account'])",
    ]
    assert python_class_method_called_names(source, "View", "get") == {
        "direct",
        "extend_schema",
        "finish",
        "permission_classes",
    }
    assert python_class_method_decorator_calls(source, "View", "post") is None


def test_python_schema_parser_extracts_only_integer_success_responses() -> None:
    source = """
class AccountView:
    @extend_schema(
        request=InputSerializer,
        responses={200: AccountSerializer, 201: Envelope(AccountSerializer), 400: Error},
    )
    def post(self):
        pass

    @extend_schema(responses={204: None})
    async def delete(self):
        pass

class IgnoredView:
    @other(responses={200: Wrong})
    def get(self):
        pass
"""

    assert python_extend_schema_success_responses(source) == {
        ("AccountView", "post", 200): "AccountSerializer",
        ("AccountView", "post", 201): "Envelope(AccountSerializer)",
        ("AccountView", "delete", 204): "None",
    }


def test_python_analysis_returns_safe_empty_results_for_invalid_source() -> None:
    source = "class Broken("

    assert python_class_fields(source, "Broken") is None
    assert python_class_field_calls(source, "Broken") is None
    assert python_class_method_decorator_calls(source, "Broken", "get") is None
    assert python_class_method_called_names(source, "Broken", "get") is None
    assert python_top_level_class_names(source) == []
    assert python_top_level_assignment_names(source) == []
    assert python_extend_schema_success_responses(source) == {}
