"""Focused tests for reusable TypeScript source-analysis helpers."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[4]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.typescript_analysis import (  # noqa: E402
    canonical_ts_module_reference,
    destructured_function_props,
    jsx_component_props,
    normalized_ts_module_reference,
    normalized_ts_type,
    resolve_ts_static_string_expression,
    strip_outer_ts_parentheses,
    strip_ts_comments,
    ts_balanced_brace_body,
    ts_clause_is_type_only,
    ts_exported_adapter_uses_access,
    ts_exported_top_level_adapter_uses_access,
    ts_exported_type_aliases,
    ts_exports_tainted_binding,
    ts_interface_declarations,
    ts_member_access_aliases,
    ts_module_matches,
    ts_module_matches_boundary,
    ts_module_specifiers,
    ts_named_import_bindings,
    ts_namespace_import_bindings,
    ts_object_method_body,
    ts_object_type_alias_bodies,
    ts_object_type_field_names,
    ts_recursive_statements,
    ts_reexports_all_from_module,
    ts_reexports_named_binding,
    ts_response_forwarding_bindings,
    ts_static_string_bindings,
    ts_top_level_statements,
    ts_type_aliases,
    ts_value_module_references,
)

del _TEST_IMPORT_ROOT


def test_typescript_module_parsers_distinguish_runtime_and_type_references() -> None:
    source = """
import type { Account } from "@/shared/account/types";
import { type Detail, load } from /* comment */ "@/shared/account/api";
import "./side-effect";
const lazy = import(`./lazy`);
const required = require("package/runtime");
"""

    assert ts_module_specifiers(source) == [
        "@/shared/account/types",
        "@/shared/account/api",
        "./side-effect",
        "./lazy",
        "package/runtime",
    ]
    assert ts_value_module_references(source) == [
        "@/shared/account/api",
        "./side-effect",
        "./lazy",
        "package/runtime",
    ]
    assert ts_clause_is_type_only("{ type Account, type Detail as D }")
    assert not ts_clause_is_type_only("{ type Account, load }")
    assert ts_module_matches_boundary("features/home/api", "features/home")
    assert not ts_module_matches_boundary("features/homepage", "features/home")


def test_typescript_component_and_balanced_body_parsers_are_quote_aware() -> None:
    source = """
function Panel({ title: heading, count = 0, onClose }: Props) {
  return <Card title={heading} data-id="primary" onClose={onClose} />;
}
const api = {
  load() { const marker = "}"; return { value: marker }; },
};
"""

    assert destructured_function_props(source, "Panel") == [
        "title",
        "count",
        "onClose",
    ]
    assert jsx_component_props(source, "Card") == (
        ["title", "data-id", "onClose"],
        'title={heading}data-id="primary"onClose={onClose}/',
    )
    method_body = ts_object_method_body(source, "load")
    assert method_body is not None
    assert "return { value: marker }" in method_body
    opening = source.index("{", source.index("load()"))
    assert ts_balanced_brace_body(source, opening) == method_body
    assert ts_balanced_brace_body(source, source.index("load")) is None
    assert strip_ts_comments("a/* hidden */b // tail\nc") == "ab \nc"


def test_typescript_statement_parsers_keep_nested_control_flow_bounded() -> None:
    body = """
const value = condition
  ? { nested: true }
  : fallback;
if (value) {
  const result = run();
  return result;
}
return null;
"""

    top_level = ts_top_level_statements(body)
    recursive = ts_recursive_statements(body)

    assert len(top_level) == 3
    assert top_level[0].startswith("const value = condition")
    assert "const result = run()" in recursive
    assert "return result" in recursive
    assert recursive[-1] == "return null"


def test_typescript_type_shape_parsers_cover_aliases_interfaces_and_fields() -> None:
    source = """
type Local = { ignored: string };
export type Result = ApiResult;
export interface Account extends BaseAccount, Timestamped {
  readonly id: string;
  displayName?: string;
  "data-key": number;
}
export type Payload = {
  account: Account;
  nested: { value: string };
};
"""

    interfaces = ts_interface_declarations(source)
    object_aliases = ts_object_type_alias_bodies(source)

    assert ts_exported_type_aliases(source)["Result"] == "ApiResult"
    assert ts_type_aliases(source)["Local"] == "{ ignored: string }"
    assert normalized_ts_type(' Array< "value" > ') == "Array<'value'>"
    assert interfaces["Account"][0] == "BaseAccount, Timestamped"
    assert ts_object_type_field_names(interfaces["Account"][1]) == {
        "id",
        "displayName",
        "data-key",
    }
    assert ts_object_type_field_names(object_aliases["Payload"]) == {
        "account",
        "nested",
    }
    assert strip_outer_ts_parentheses("(((Account | null)))") == "Account | null"


def test_typescript_import_binding_and_reexport_parsers_resolve_canonical_paths() -> None:
    frontend_root = "front" + "end/src"
    path_label = f"{frontend_root}/features/account/api/accountApi.ts"
    canonical = f"{frontend_root}/shared/account/contracts"
    source = """
import { Account as AccountContract, type AccountMeta, Other } from "@/shared/account/contracts";
import * as Contracts from "../../../shared/account/contracts.ts";
export * from "@/shared/account/contracts";
export { Account as PublicAccount, Other } from "../../../shared/account/contracts";
"""

    assert (
        canonical_ts_module_reference(module="@/shared/account/contracts.ts", path_label=path_label)
        == canonical
    )
    assert (
        normalized_ts_module_reference(path_label, "../../../shared/account/contracts.ts")
        == canonical
    )
    assert ts_module_matches(
        path_label=path_label,
        module="@/shared/account/contracts",
        canonical_module="../../../shared/account/contracts.ts",
    )
    assert ts_named_import_bindings(
        source,
        path_label=path_label,
        module=canonical,
        exported_names={"Account", "AccountMeta"},
    ) == {"AccountContract", "AccountMeta"}
    assert ts_namespace_import_bindings(source, path_label=path_label, module=canonical) == {
        "Contracts"
    }
    assert ts_reexports_all_from_module(source, path_label=path_label, module=canonical)
    assert ts_reexports_named_binding(
        source,
        path_label=path_label,
        module=canonical,
        exported_names={"Account"},
    )


def test_typescript_access_taint_parsers_follow_aliases_and_exports() -> None:
    source = """
const clientAlias = client;
const request = clientAlias.request;
const { mutate: runMutation } = clientAlias;
const wrapped = (payload: Input) => request(payload);
export { wrapped as submit };
"""

    patterns, tainted = ts_member_access_aliases(
        source,
        object_bindings={"client"},
        member_names={"request", "mutate"},
    )

    assert {"client", "clientAlias", "request", "runMutation", "wrapped"} <= tainted
    assert ts_exports_tainted_binding(source, tainted)
    assert ts_exported_adapter_uses_access(
        "export const submit = (payload: Input) => client.request(payload);",
        [r"\bclient\.request\b"],
    )
    assert not ts_exported_adapter_uses_access(
        "export const useSubmit = () => useQuery(client.request());",
        [r"\bclient\.request\b"],
    )
    assert any(re.search(pattern, "wrapped(payload)") for pattern in patterns)


def test_typescript_response_forwarding_detects_only_exported_top_level_adapters() -> None:
    access = [r"\bclient\.request\b"]
    source = """
const load = async () => client.request();
export { load };
"""

    assert ts_response_forwarding_bindings(source, access) == {"load"}
    assert ts_exported_top_level_adapter_uses_access(source, access)
    assert not ts_exported_top_level_adapter_uses_access(
        "export const Widget = () => <Button onClick={() => client.request()} />;",
        access,
    )


def test_typescript_static_string_parsers_resolve_fixed_points_safely() -> None:
    source = """
const VERSION = "v1";
const ROOT = "/api/" + VERSION;
const DETAIL = `${ROOT}/account`;
const UNKNOWN = `${MISSING}/account`;
const CALL = makePath(ROOT);
"""

    bindings = ts_static_string_bindings(source)

    assert bindings == {
        "VERSION": "v1",
        "ROOT": "/api/v1",
        "DETAIL": "/api/v1/account",
    }
    assert resolve_ts_static_string_expression("ROOT + '/sessions'", bindings) == (
        "/api/v1/sessions"
    )
    assert resolve_ts_static_string_expression("`${DETAIL}/current`", bindings) == (
        "/api/v1/account/current"
    )
    assert resolve_ts_static_string_expression("makePath(ROOT)", bindings) is None
