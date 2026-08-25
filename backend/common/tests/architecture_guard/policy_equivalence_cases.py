"""Stable synthetic cases captured before the architecture-guard cutover."""

_FRONTEND = "front" + "end"

POLICY_EQUIVALENCE_CASES = {
    "catalog": {
        "function": "catalog_secondary_backend_contract_violations",
        "args": [
            {
                "backend/example/catalog.py": (
                    "from curriculum.serializers import StorySerializer as Base\n"
                    "class StoryPrerequisiteV2Serializer(serializers.Serializer):\n"
                    "    pass\n"
                    "ChapterListV2Serializer = StoryPrerequisiteV2Serializer\n"
                    "class CatalogV2(Base):\n"
                    "    pass\n"
                )
            }
        ],
    },
    "auth": {
        "function": "auth_secondary_backend_contract_violations",
        "args": [
            {
                "backend/example/auth_contracts.py": (
                    "from accounts.serializers import SessionResponseSerializer as Base\n"
                    "class LoginResultSerializer(serializers.Serializer):\n"
                    "    pass\n"
                    "class SessionShadow(Base):\n"
                    "    pass\n"
                    "SessionAlias = Base\n"
                ),
                "backend/example/reexport.py": (
                    "from accounts.serializers import "
                    "SessionResponseSerializer as LoginContract\n"
                    "__all__ = ['LoginContract']\n"
                ),
            }
        ],
    },
    "progress": {
        "function": "progress_summary_secondary_backend_contract_violations",
        "args": [
            {
                "backend/example/dashboard_contracts.py": (
                    "class DashboardShadowSerializer:\n"
                    "    pass\n"
                    "DashboardSummaryV2Serializer = DashboardShadowSerializer\n"
                    "class HomeSummarySerializer:\n"
                    "    pass\n"
                    "HomeOverviewResponseSerializer = HomeSummarySerializer\n"
                )
            }
        ],
    },
    "gameplay": {
        "function": "gameplay_mutation_frontend_violations",
        "args": [
            {
                f"{_FRONTEND}/src/features/example/shadows.ts": (
                    "type CreateFileInput = { path: string; content: string }\n"
                    "interface RenameFileInput { path: string; newPath: string }\n"
                    "interface CommandExecutionPayload { processed: boolean }\n"
                    "type WorkspaceFileRequest = WorkspaceFileInput\n"
                    "export type { WorkspaceFileInput } "
                    "from '@/shared/level/workspaceFileTypes'\n"
                ),
                f"{_FRONTEND}/src/features/adventures/api/adventuresApi.ts": (
                    "import type { ApiRequestBody } "
                    "from '@/shared/api/generated/apiTypes'\n"
                    "const body = value as "
                    "ApiRequestBody<'adventure_runs_files_create'>\n"
                ),
            }
        ],
    },
}


PRE_CUTOVER_EXPECTED_VIOLATIONS = {
    "catalog": [
        "backend/example/catalog.py: secondary catalog response contract "
        "StoryPrerequisiteV2Serializer is not allowed",
        "backend/example/catalog.py: secondary catalog response contract "
        "ChapterListV2Serializer is not allowed",
        "backend/example/catalog.py: secondary catalog response contract CatalogV2 is not allowed",
    ],
    "auth": [
        "backend/example/auth_contracts.py: secondary Auth response contract "
        "LoginResultSerializer is not allowed",
        "backend/example/auth_contracts.py: secondary Auth response contract "
        "SessionShadow is not allowed",
        "backend/example/auth_contracts.py: secondary Auth response contract "
        "SessionAlias is not allowed",
        "backend/example/reexport.py: secondary Auth response contract "
        "LoginContract is not allowed",
    ],
    "progress": [
        "backend/example/dashboard_contracts.py: secondary Progress response contract "
        "DashboardShadowSerializer is not allowed",
        "backend/example/dashboard_contracts.py: secondary Progress response contract "
        "HomeSummarySerializer is not allowed",
        "backend/example/dashboard_contracts.py: secondary Progress response contract "
        "DashboardSummaryV2Serializer is not allowed",
        "backend/example/dashboard_contracts.py: secondary Progress response contract "
        "HomeOverviewResponseSerializer is not allowed",
    ],
    "gameplay": [
        f"{_FRONTEND}/src/features/challenges/api/challengeRunsApi.ts: required gameplay "
        "contract owner is missing",
        f"{_FRONTEND}/src/shared/level-runtime/runMutationInputs.ts: required gameplay "
        "contract owner is missing",
        f"{_FRONTEND}/src/shared/level/types.ts: required gameplay contract owner is missing",
        f"{_FRONTEND}/src/shared/level/workspaceFileTypes.ts: required gameplay contract "
        "owner is missing",
        f"{_FRONTEND}/src/features/example/shadows.ts: CreateFileInput duplicates or "
        "facades the shared workspace input",
        f"{_FRONTEND}/src/features/example/shadows.ts: RenameFileInput duplicates or "
        "facades the shared workspace input",
        f"{_FRONTEND}/src/features/example/shadows.ts: WorkspaceFileRequest duplicates or "
        "facades the shared workspace input",
        f"{_FRONTEND}/src/features/example/shadows.ts: CommandExecutionPayload belongs in "
        f"{_FRONTEND}/src/shared/level/types.ts",
        f"{_FRONTEND}/src/features/example/shadows.ts: gameplay contract type re-export "
        "facades are forbidden",
        f"{_FRONTEND}/src/features/adventures/api/adventuresApi.ts: gameplay API bodies must "
        "use the shared generated adapter",
        f"{_FRONTEND}/src/features/adventures/api/adventuresApi.ts: gameplay API must import "
        "the exact shared body adapters",
        f"{_FRONTEND}/src/features/adventures/api/adventuresApi.ts: submitCommand body must "
        "delegate to commandSubmitBody",
        f"{_FRONTEND}/src/features/adventures/api/adventuresApi.ts: createFile body must "
        "delegate to workspaceFileBody",
        f"{_FRONTEND}/src/features/adventures/api/adventuresApi.ts: writeFile body must "
        "delegate to workspaceFileBody",
        f"{_FRONTEND}/src/features/adventures/api/adventuresApi.ts: renameFile body must "
        "delegate to workspaceFileRenameBody",
    ],
}
