"""Auth architecture contract-policy tests."""

import json
import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[4]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.contracts.auth import (  # noqa: E402
    AUTH_BACKEND_SERIALIZERS,
    AUTH_BACKEND_VIEWS,
    AUTH_COMMON_OPENAPI,
    AUTH_FRONTEND_API,
    AUTH_FRONTEND_TYPES,
    AUTH_GENERATED_OPENAPI,
    AUTH_HTTP_CLIENT,
    auth_contract_source_violations,
    auth_openapi_contract_violations,
    auth_secondary_backend_contract_violations,
    auth_secondary_frontend_contract_violations,
    check_auth_contract_ownership,
)
from scripts.checks.architecture_guard.repository import (  # noqa: E402
    ROOT,
)

del _TEST_IMPORT_ROOT

_FRONTEND = "front" + "end"


def test_auth_contract_guard_rejects_wrong_owners_and_manual_overrides():
    root = ROOT

    def source(path: str) -> str:
        return (root / path).read_text(encoding="utf-8")

    violations = auth_contract_source_violations(
        serializers_source=source(AUTH_BACKEND_SERIALIZERS).replace(
            "user = UserSerializer()", "user = serializers.DictField()", 1
        ),
        views_source=source(AUTH_BACKEND_VIEWS).replace(
            "responses={201: RegisterResponseSerializer}", "responses={201: UserSerializer}"
        ),
        common_openapi_source=source(AUTH_COMMON_OPENAPI)
        + "\nclass LoginResponseSerializer(serializers.Serializer):\n    pass\n",
        auth_types_source=source(AUTH_FRONTEND_TYPES).replace(
            "export type User = ApiSchemas['User']",
            "export type User = { id: number }\nexport type AuthResponse = { access: string; user: User }",
        ),
        auth_api_source=source(AUTH_FRONTEND_API).replace(
            "apiOperationRequest('auth_login_create'",
            "apiOperationRequest<'auth_login_create', AuthResponse>('auth_login_create'",
        ),
        http_client_source=source(AUTH_HTTP_CLIENT).replace(
            "apiRequest<ApiResponseBody<'auth_refresh_create'>>", "apiRequest<{ access: string }>"
        ),
    )
    assert any("RegisterResponseSerializer must own its exact" in row for row in violations)
    assert any("RegisterAPIView.post 201 must document" in row for row in violations)
    assert any("displaced Auth response contracts" in row for row in violations)
    assert any("export only User derived exactly" in row for row in violations)
    assert any("handwritten Auth response DTOs" in row for row in violations)
    assert any("auth_login_create must not pass" in row for row in violations)
    assert any("only refresh may use a raw Auth path" in row for row in violations)


def test_auth_contract_guard_rejects_secondary_backend_shadows():
    violations = auth_secondary_backend_contract_violations(
        {
            "backend/example/auth_contracts.py": "from accounts.serializers import SessionResponseSerializer as Base\nfrom accounts.serializers import UserSerializer\nclass LoginResultSerializer(serializers.Serializer):\n    pass\nclass SessionShadow(Base):\n    pass\nSessionAlias = Base\nclass TokenEnvelopeSerializer(serializers.Serializer):\n    access = serializers.CharField()\n    user = UserSerializer()\n",
            "backend/example/common.py": "class SessionResponseSerializer(serializers.Serializer):\n    pass\n",
            "backend/example/reexport.py": "from accounts.serializers import SessionResponseSerializer as LoginContract\n__all__ = ['LoginContract']\n",
        }
    )
    assert any("LoginResultSerializer" in row for row in violations)
    assert any("SessionShadow" in row for row in violations)
    assert any("SessionAlias" in row for row in violations)
    assert any("SessionResponseSerializer" in row for row in violations)
    assert any("TokenEnvelopeSerializer" in row for row in violations)
    assert any("LoginContract" in row for row in violations)


def test_auth_contract_guard_rejects_aliases_wrappers_and_raw_paths():
    violations = auth_secondary_frontend_contract_violations(
        {
            f"{_FRONTEND}/src/features/example/authClient.ts": "import type { ApiSchemas as Wire } from '@/shared/api/generated/apiTypes'\ntype Base = Wire['SessionResponse']\nexport type LoginEnvelope = Base & { legacy: true }\nexport type Handwritten = { access: string; user: { id: number } }\nexport const login = () => apiOperationRequest('auth_login_create', '/auth/login/')\n",
            f"{_FRONTEND}/src/features/example/authAlias.ts": "import { authApi } from '@/shared/auth/authApi'\nexport const sessionApi = authApi\n",
            f"{_FRONTEND}/src/features/example/authMethod.ts": "import { authApi as api } from '@/shared/auth/authApi'\nexport const login = api.login\n",
            f"{_FRONTEND}/src/features/example/authReexport.ts": "export { authApi as alternateAuthApi } from '@/shared/auth/authApi'\n",
            f"{_FRONTEND}/src/features/example/authWildcard.ts": "export * from '@/shared/auth/authApi'\n",
            f"{_FRONTEND}/src/features/example/authNamespace.ts": "import * as auth from '@/shared/auth/authApi'\nexport const login = auth.authApi.login\n",
            f"{_FRONTEND}/src/features/example/authObject.ts": "import { authApi } from '@/shared/auth/authApi'\nexport const session = { login: authApi.login }\n",
            f"{_FRONTEND}/src/features/example/authExportListArrow.ts": "import { authApi } from '@/shared/auth/authApi'\nconst login = (payload: unknown) => authApi.login(payload)\nexport { login }\n",
            f"{_FRONTEND}/src/features/example/authReturnedObject.ts": "import { authApi } from '@/shared/auth/authApi'\nexport function useSessionActions() {\n  return { login: authApi.login }\n}\n",
            f"{_FRONTEND}/src/features/example/authReturnType.ts": "import { authApi } from '@/shared/auth/authApi'\nexport type SessionData = Awaited<ReturnType<typeof authApi.login>>\n",
            f"{_FRONTEND}/src/features/example/authAliasReturnType.ts": "import { authApi } from '@/shared/auth/authApi'\nconst login = authApi.login\nexport type SessionData = Awaited<ReturnType<typeof login>>\n",
            f"{_FRONTEND}/src/features/example/authBlockExportList.ts": "import { authApi } from '@/shared/auth/authApi'\nconst login = (payload: unknown) => {\n  return authApi.login(payload)\n}\nexport { login }\n",
            f"{_FRONTEND}/src/features/example/authObjectExportList.ts": "import { authApi } from '@/shared/auth/authApi'\nconst session = { login: authApi.login }\nexport { session }\n",
            f"{_FRONTEND}/src/features/example/authConciseObject.ts": "import { authApi } from '@/shared/auth/authApi'\nexport const useSessionActions = () => ({ login: authApi.login })\n",
            f"{_FRONTEND}/src/features/example/authFunctionExportList.ts": "import { authApi } from '@/shared/auth/authApi'\nfunction login(payload: unknown) {\n  return authApi.login(payload)\n}\nexport { login }\n",
            f"{_FRONTEND}/src/features/example/composedPath.ts": "const root = '/auth'\nconst endpoint = root + '/login/'\nexport const login = () => fetch(endpoint)\n",
            f"{_FRONTEND}/src/features/example/templatePath.ts": "const root = '/auth'\nconst endpoint = `${root}/login/`\nexport const login = () => fetch(endpoint)\n",
        }
    )
    assert any("LoginEnvelope" in row and "Handwritten" in row for row in violations)
    assert any("Auth generated operation wrapper" in row for row in violations)
    assert any("raw Auth endpoint request path" in row for row in violations)
    for path_name in (
        "authAlias.ts",
        "authMethod.ts",
        "authReexport.ts",
        "authWildcard.ts",
        "authNamespace.ts",
        "authObject.ts",
        "authExportListArrow.ts",
        "authReturnedObject.ts",
        "authBlockExportList.ts",
        "authObjectExportList.ts",
        "authConciseObject.ts",
        "authFunctionExportList.ts",
    ):
        assert any(
            path_name in row and "secondary exported Auth response adapter" in row
            for row in violations
        )
    assert any("authReturnType.ts" in row and "SessionData" in row for row in violations)
    assert any("authAliasReturnType.ts" in row and "SessionData" in row for row in violations)
    assert any(
        "composedPath.ts" in row and "raw Auth endpoint request path" in row for row in violations
    )
    assert any(
        "templatePath.ts" in row and "raw Auth endpoint request path" in row for row in violations
    )


def test_auth_contract_guard_allows_state_messages_and_error_props():
    violations = auth_secondary_frontend_contract_violations(
        {
            f"{_FRONTEND}/src/features/example/authState.ts": "import type { User } from '@/shared/auth/types'\nimport { authApi } from '@/shared/auth/authApi'\ntype AuthState = { access: string | null; user: User | null }\ntype AuthChannelMessage = { type: 'logout' | 'token-refreshed' }\ntype AuthErrorProps = { detail: string; onRetry: () => void }\ntype AuthResponsePanelProps = { response: string; onClose: () => void }\ntype LoginResultMessage = { text: string; tone: 'error' | 'success' }\ntype RefreshResultState = { pending: boolean; error: string | null }\nexport async function submit(payload: unknown) {\n  await authApi.login(payload)\n  reportSuccess()\n}\nconst submitAndReport = async (payload: unknown) => {\n  await authApi.login(payload)\n  reportSuccess()\n}\nexport type SubmitReturn = Awaited<ReturnType<typeof submitAndReport>>\n"
        }
    )
    assert violations == []


def test_auth_openapi_guard_rejects_open_nested_and_body_drift():
    schema = json.loads((ROOT / AUTH_GENERATED_OPENAPI).read_text(encoding="utf-8"))
    schemas = schema["components"]["schemas"]
    schemas["User"]["required"].remove("email")
    schemas["RegisterResponse"]["properties"]["user"] = {
        "type": "object",
        "additionalProperties": {},
    }
    schema["paths"]["/api/auth/login/"]["post"]["responses"]["200"]["content"]["application/json"][
        "schema"
    ] = {"$ref": "#/components/schemas/User"}
    schema["paths"]["/api/auth/logout/"]["post"]["responses"]["204"]["content"] = {
        "application/json": {"schema": {"type": "object"}}
    }
    violations = auth_openapi_contract_violations(schema)
    assert any("User component must be exact" in row for row in violations)
    assert any("RegisterResponse component must be exact" in row for row in violations)
    assert any("POST /api/auth/login/ 200 must return SessionResponse" in row for row in violations)
    assert any("POST /api/auth/logout/ 204 must have no response body" in row for row in violations)


def test_auth_contract_runtime_obeys_account_owned_generated_contracts():
    assert check_auth_contract_ownership() == []
