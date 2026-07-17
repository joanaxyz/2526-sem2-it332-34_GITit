// GENERATED FILE. DO NOT EDIT.
// Source: backend DRF/drf-spectacular OpenAPI schema.
// Regenerate with: python scripts/generate_api_contract.py

export type JsonPrimitive = string | number | boolean | null
export type JsonValue = JsonPrimitive | JsonObject | JsonValue[]
export type JsonObject = { [key: string]: JsonValue }

export type ApiSchemas = {
  "AccessTokenResponse": { "access": string }
  "AdventureCommandResponse": { "command_classification": string; "command_outcome": { [key: string]: JsonValue }; "exit_code": number; "run": { [key: string]: JsonValue }; "solved": boolean; "stderr": string; "stdout": string; "step": ApiSchemas["RuntimeStepResponse"]; "terminal_output": string }
  "AdventureLevelLibraryResponse": { "book": { [key: string]: JsonValue }; "run": ApiSchemas["AdventureRunResponse"] }
  "AdventureRunResponse": { "battle_stage"?: { [key: string]: JsonValue }; "chapter_id"?: number; "completed_at"?: string; "current_attempt"?: { [key: string]: JsonValue }; "current_level_index": number; "current_wave": number; "id": number; "is_passed": boolean; "library_opened": boolean; "mastery": { [key: string]: JsonValue }; "next_level"?: { [key: string]: JsonValue }; "progress": { [key: string]: JsonValue }; "replay": boolean; "results": Array<{ [key: string]: JsonValue }>; "selected_level"?: { [key: string]: JsonValue }; "stars": number; "status": string; "story"?: { [key: string]: JsonValue }; "total_levels": number; "total_waves": number }
  "AuthUserResponse": { "user": { [key: string]: JsonValue } }
  "ChallengeCommandResponse": { "command_family"?: string; "command_outcome": { [key: string]: JsonValue }; "diagnostic_metadata"?: Array<string>; "exit_code"?: number; "run": { [key: string]: JsonValue }; "stderr"?: string; "stdout"?: string; "step": ApiSchemas["RuntimeStepResponse"] }
  "ChallengeRunResponse": { "battle_stage"?: { [key: string]: JsonValue }; "challenge": { [key: string]: JsonValue }; "chapter": { [key: string]: JsonValue }; "completed_at"?: string; "completion"?: { [key: string]: JsonValue }; "counts": { [key: string]: JsonValue }; "difficulty"?: string; "expected_state"?: { [key: string]: JsonValue }; "failure_reason"?: string; "id": number; "mastery_progress": { [key: string]: JsonValue }; "next_difficulty"?: { [key: string]: JsonValue }; "policy": { [key: string]: JsonValue }; "replay": boolean; "repository_state": { [key: string]: JsonValue }; "reward_coins"?: number; "scaffolding": { [key: string]: JsonValue }; "scenario_context"?: { [key: string]: JsonValue }; "sibling_levels"?: Array<{ [key: string]: JsonValue }>; "stars": number; "status": string; "steps": Array<ApiSchemas["RuntimeStepResponse"]>; "variant": { [key: string]: JsonValue }; "visualization": { [key: string]: JsonValue } }
  "ChallengeRunStart": { "prior_run_id"?: number; "replay"?: boolean; "source_entry_point"?: ApiSchemas["SourceEntryPointEnum"] }
  "ChapterList": { "adventure_level_count": number; "challenge_count": number; "chest_schedule": Array<{ [key: string]: JsonValue }>; "command_skill_count": number; "description": string; "id": number; "is_playable"?: boolean; "level_completion": { [key: string]: JsonValue }; "lock_reason": string; "locked": boolean; "number": number; "slug": string; "sort_order"?: number; "story": { [key: string]: JsonValue }; "title": string }
  "ClientCommandExecution": { "client_run_revision"?: number; "command_family": string; "diagnostic": boolean; "diagnostic_metadata": Array<string>; "exit_code": number; "next_state": { [key: string]: JsonValue }; "normalized_command": string; "output": string; "processed": boolean; "stderr": string; "stdout": string }
  "CommandFormPreviewResponse": { "command_preview": { [key: string]: JsonValue }; "id": number; "is_playable": boolean; "label": string; "skill": ApiSchemas["CommandFormPreviewSkillResponse"]; "slug": string; "summary": string; "usage_form": string }
  "CommandFormPreviewSkillResponse": { "base_command": string; "id": number; "slug": string; "title": string }
  "CommandSubmit": { "command": string; "execution": ApiSchemas["ClientCommandExecution"] }
  "DashboardSummaryResponse": { "chapter_kpis": { [key: string]: JsonValue }; "completed_stories": Array<string>; "completed_story_slug"?: string; "counts": { [key: string]: JsonValue }; "kpis": { [key: string]: JsonValue }; "mastery": number; "perfect_clears": number; "retry_trends": { [key: string]: JsonValue }; "streak": { [key: string]: JsonValue } }
  "DetailResponse": { "detail": string }
  "DifficultyEnum": "beginner" | "intermediate" | "advanced"
  "KindEnum": "story" | "companion"
  "LearnedSkillResponse": { "base_command": string; "chapter_id"?: number; "chapter_number": number; "chapter_title": string; "id": number; "slug": string; "summary": string; "title": string }
  "LearnedSkillsResponse": { "results": Array<ApiSchemas["LearnedSkillResponse"]> }
  "Login": { "identifier": string; "password": string }
  "LoginResponse": { "access": string; "user": { [key: string]: JsonValue } }
  "MotionModeEnum": "system" | "reduced" | "full"
  "PasswordChange": { "current_password": string; "password": string; "password_confirm": string }
  "PasswordResetConfirm": { "password": string; "password_confirm": string; "token": string; "uid": string }
  "PasswordResetRequest": { "email": string }
  "PatchedPlayerPreferences": { "motion_mode"?: ApiSchemas["MotionModeEnum"] }
  "PatchedWorkspaceFile": { "content"?: string; "path"?: string }
  "PatchedWorkspaceFileCreate": { "content"?: string; "path"?: string }
  "PlayerPreferences": { "motion_mode"?: ApiSchemas["MotionModeEnum"] }
  "Register": { "email": string; "password": string; "password_confirm": string; "username": string }
  "RuntimeStepResponse": { "command_classification"?: string; "command_text": string; "contextual_feedback"?: string; "created_at"?: string; "id": number; "result_category"?: string; "terminal_output"?: string; "visualization_snapshot"?: { [key: string]: JsonValue } }
  "ShopEquipResponse": { "active_companion"?: string; "shop": ApiSchemas["ShopResponse"] }
  "ShopItemResponse": { "active": boolean; "kind": ApiSchemas["KindEnum"]; "label": string; "owned": boolean; "price": number; "slug": string; "unlocks_story"?: { [key: string]: JsonValue } }
  "ShopMutationRequest": { "kind": string; "slug": string }
  "ShopPurchaseResponse": { "owned": boolean; "shop": ApiSchemas["ShopResponse"]; "wallet": ApiSchemas["WalletSummaryResponse"] }
  "ShopResponse": { "active_companion"?: string; "items": Array<ApiSchemas["ShopItemResponse"]> }
  "SourceEntryPointEnum": "level_page" | "retry"
  "StatsSummaryResponse": { "activity": Array<{ [key: string]: JsonValue }>; "headlines": { [key: string]: JsonValue }; "skill_profile": Array<{ [key: string]: JsonValue }>; "totals"?: { [key: string]: JsonValue } }
  "Story": { "completed": boolean; "difficulty"?: ApiSchemas["DifficultyEnum"]; "id": number; "is_published"?: boolean; "lock_reason": string; "locked": boolean; "owned": boolean; "prerequisite_story": { [key: string]: JsonValue }; "price"?: number; "slug": string; "sort_order"?: number; "summary"?: string; "title": string; "world_slug"?: string }
  "User": { "email": string; "id": number; "is_staff": boolean; "username": string }
  "WalletSummaryResponse": { "balance": number }
  "WorkspaceFile": { "content"?: string; "path": string }
  "WorkspaceFileCreate": { "content"?: string; "path": string }
  "WorkspaceFileRename": { "new_path": string; "path": string }
}

export type ApiPath =
  | "/api/admin/analytics/"
  | "/api/admin/chapters/"
  | "/api/admin/chapters/{chapter_id}/"
  | "/api/admin/content/"
  | "/api/admin/economy/adjust/"
  | "/api/admin/economy/transactions/"
  | "/api/admin/moderation/"
  | "/api/admin/moderation/unpublish/"
  | "/api/admin/overview/"
  | "/api/admin/settings/"
  | "/api/admin/stories/"
  | "/api/admin/stories/{story_id}/"
  | "/api/admin/users/"
  | "/api/admin/users/{user_id}/"
  | "/api/admin/users/{user_id}/actions/"
  | "/api/adventure-levels/{level_id}/runs/"
  | "/api/adventure-runs/{run_id}/"
  | "/api/adventure-runs/{run_id}/files/"
  | "/api/adventure-runs/{run_id}/level-library/"
  | "/api/adventure-runs/{run_id}/submit-command/"
  | "/api/adventures/{adventure_slug}/runs/"
  | "/api/auth/login/"
  | "/api/auth/logout/"
  | "/api/auth/me/"
  | "/api/auth/password-change/"
  | "/api/auth/password-reset/confirm/"
  | "/api/auth/password-reset/request/"
  | "/api/auth/refresh/"
  | "/api/auth/register/"
  | "/api/auth/sessions/revoke-all/"
  | "/api/auth/sessions/revoke-others/"
  | "/api/authoring/chapters/"
  | "/api/authoring/chapters/{chapter_id}/"
  | "/api/authoring/command-forms/"
  | "/api/authoring/content-definitions/"
  | "/api/authoring/content-definitions/{definition_id}/"
  | "/api/authoring/content-definitions/{definition_id}/publish/"
  | "/api/authoring/content-definitions/{definition_id}/remix/"
  | "/api/authoring/content-definitions/{definition_id}/test-run/"
  | "/api/authoring/content-definitions/{definition_id}/validate/"
  | "/api/challenge-runs/{run_id}/"
  | "/api/challenge-runs/{run_id}/files/"
  | "/api/challenge-runs/{run_id}/retry/"
  | "/api/challenge-runs/{run_id}/submit-command/"
  | "/api/challenge-trials/{trial_id}/runs/"
  | "/api/chapters/"
  | "/api/chapters/{chapter_id}/book/"
  | "/api/chapters/{chapter_id}/overview/"
  | "/api/command-forms/{form_id}/preview/"
  | "/api/health/"
  | "/api/health/live/"
  | "/api/health/ready/"
  | "/api/player/loadout/companion/"
  | "/api/player/preferences/"
  | "/api/progress/dashboard/"
  | "/api/progress/stats/"
  | "/api/progress/wallet/"
  | "/api/schema/"
  | "/api/shop/catalog/"
  | "/api/shop/catalog/purchase/"
  | "/api/skills/learned/"
  | "/api/stories/"

export type ApiMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS'

export type ApiMethodByPath = {
  "/api/admin/analytics/": "GET"
  "/api/admin/chapters/": "GET"
  "/api/admin/chapters/{chapter_id}/": "PATCH"
  "/api/admin/content/": "GET"
  "/api/admin/economy/adjust/": "POST"
  "/api/admin/economy/transactions/": "GET"
  "/api/admin/moderation/": "GET"
  "/api/admin/moderation/unpublish/": "POST"
  "/api/admin/overview/": "GET"
  "/api/admin/settings/": "GET" | "POST"
  "/api/admin/stories/": "GET" | "POST"
  "/api/admin/stories/{story_id}/": "PATCH"
  "/api/admin/users/": "GET"
  "/api/admin/users/{user_id}/": "GET"
  "/api/admin/users/{user_id}/actions/": "POST"
  "/api/adventure-levels/{level_id}/runs/": "POST"
  "/api/adventure-runs/{run_id}/": "DELETE" | "GET"
  "/api/adventure-runs/{run_id}/files/": "DELETE" | "PATCH" | "POST" | "PUT"
  "/api/adventure-runs/{run_id}/level-library/": "POST"
  "/api/adventure-runs/{run_id}/submit-command/": "POST"
  "/api/adventures/{adventure_slug}/runs/": "POST"
  "/api/auth/login/": "POST"
  "/api/auth/logout/": "POST"
  "/api/auth/me/": "GET"
  "/api/auth/password-change/": "POST"
  "/api/auth/password-reset/confirm/": "POST"
  "/api/auth/password-reset/request/": "POST"
  "/api/auth/refresh/": "POST"
  "/api/auth/register/": "POST"
  "/api/auth/sessions/revoke-all/": "POST"
  "/api/auth/sessions/revoke-others/": "POST"
  "/api/authoring/chapters/": "GET" | "POST"
  "/api/authoring/chapters/{chapter_id}/": "DELETE" | "PATCH"
  "/api/authoring/command-forms/": "GET"
  "/api/authoring/content-definitions/": "GET" | "POST"
  "/api/authoring/content-definitions/{definition_id}/": "GET" | "PATCH"
  "/api/authoring/content-definitions/{definition_id}/publish/": "POST"
  "/api/authoring/content-definitions/{definition_id}/remix/": "POST"
  "/api/authoring/content-definitions/{definition_id}/test-run/": "POST"
  "/api/authoring/content-definitions/{definition_id}/validate/": "POST"
  "/api/challenge-runs/{run_id}/": "DELETE" | "GET"
  "/api/challenge-runs/{run_id}/files/": "DELETE" | "PATCH" | "POST" | "PUT"
  "/api/challenge-runs/{run_id}/retry/": "POST"
  "/api/challenge-runs/{run_id}/submit-command/": "POST"
  "/api/challenge-trials/{trial_id}/runs/": "POST"
  "/api/chapters/": "GET"
  "/api/chapters/{chapter_id}/book/": "GET"
  "/api/chapters/{chapter_id}/overview/": "GET"
  "/api/command-forms/{form_id}/preview/": "GET"
  "/api/health/": "GET"
  "/api/health/live/": "GET"
  "/api/health/ready/": "GET"
  "/api/player/loadout/companion/": "POST"
  "/api/player/preferences/": "GET" | "PATCH"
  "/api/progress/dashboard/": "GET"
  "/api/progress/stats/": "GET"
  "/api/progress/wallet/": "GET"
  "/api/schema/": "GET"
  "/api/shop/catalog/": "GET"
  "/api/shop/catalog/purchase/": "POST"
  "/api/skills/learned/": "GET"
  "/api/stories/": "GET"
}

export const apiOperations = {
  admin_analytics_retrieve: { method: "GET", path: "/api/admin/analytics/", operationId: "admin_analytics_retrieve", tags: ["admin"] },
  admin_chapters_retrieve: { method: "GET", path: "/api/admin/chapters/", operationId: "admin_chapters_retrieve", tags: ["admin"] },
  admin_chapters_partial_update: { method: "PATCH", path: "/api/admin/chapters/{chapter_id}/", operationId: "admin_chapters_partial_update", tags: ["admin"] },
  admin_content_retrieve: { method: "GET", path: "/api/admin/content/", operationId: "admin_content_retrieve", tags: ["admin"] },
  admin_economy_adjust_create: { method: "POST", path: "/api/admin/economy/adjust/", operationId: "admin_economy_adjust_create", tags: ["admin"] },
  admin_economy_transactions_retrieve: { method: "GET", path: "/api/admin/economy/transactions/", operationId: "admin_economy_transactions_retrieve", tags: ["admin"] },
  admin_moderation_retrieve: { method: "GET", path: "/api/admin/moderation/", operationId: "admin_moderation_retrieve", tags: ["admin"] },
  admin_moderation_unpublish_create: { method: "POST", path: "/api/admin/moderation/unpublish/", operationId: "admin_moderation_unpublish_create", tags: ["admin"] },
  admin_overview_retrieve: { method: "GET", path: "/api/admin/overview/", operationId: "admin_overview_retrieve", tags: ["admin"] },
  admin_settings_retrieve: { method: "GET", path: "/api/admin/settings/", operationId: "admin_settings_retrieve", tags: ["admin"] },
  admin_settings_create: { method: "POST", path: "/api/admin/settings/", operationId: "admin_settings_create", tags: ["admin"] },
  admin_stories_retrieve: { method: "GET", path: "/api/admin/stories/", operationId: "admin_stories_retrieve", tags: ["admin"] },
  admin_stories_create: { method: "POST", path: "/api/admin/stories/", operationId: "admin_stories_create", tags: ["admin"] },
  admin_stories_partial_update: { method: "PATCH", path: "/api/admin/stories/{story_id}/", operationId: "admin_stories_partial_update", tags: ["admin"] },
  admin_users_retrieve: { method: "GET", path: "/api/admin/users/", operationId: "admin_users_retrieve", tags: ["admin"] },
  admin_users_retrieve_2: { method: "GET", path: "/api/admin/users/{user_id}/", operationId: "admin_users_retrieve_2", tags: ["admin"] },
  admin_users_actions_create: { method: "POST", path: "/api/admin/users/{user_id}/actions/", operationId: "admin_users_actions_create", tags: ["admin"] },
  adventure_levels_runs_create: { method: "POST", path: "/api/adventure-levels/{level_id}/runs/", operationId: "adventure_levels_runs_create", tags: ["adventure-levels"] },
  adventure_runs_destroy: { method: "DELETE", path: "/api/adventure-runs/{run_id}/", operationId: "adventure_runs_destroy", tags: ["adventure-runs"] },
  adventure_runs_retrieve: { method: "GET", path: "/api/adventure-runs/{run_id}/", operationId: "adventure_runs_retrieve", tags: ["adventure-runs"] },
  adventure_runs_files_destroy: { method: "DELETE", path: "/api/adventure-runs/{run_id}/files/", operationId: "adventure_runs_files_destroy", tags: ["adventure-runs"] },
  adventure_runs_files_partial_update: { method: "PATCH", path: "/api/adventure-runs/{run_id}/files/", operationId: "adventure_runs_files_partial_update", tags: ["adventure-runs"] },
  adventure_runs_files_create: { method: "POST", path: "/api/adventure-runs/{run_id}/files/", operationId: "adventure_runs_files_create", tags: ["adventure-runs"] },
  adventure_runs_files_update: { method: "PUT", path: "/api/adventure-runs/{run_id}/files/", operationId: "adventure_runs_files_update", tags: ["adventure-runs"] },
  adventure_runs_level_library_create: { method: "POST", path: "/api/adventure-runs/{run_id}/level-library/", operationId: "adventure_runs_level_library_create", tags: ["adventure-runs"] },
  adventure_runs_submit_command_create: { method: "POST", path: "/api/adventure-runs/{run_id}/submit-command/", operationId: "adventure_runs_submit_command_create", tags: ["adventure-runs"] },
  adventures_runs_create: { method: "POST", path: "/api/adventures/{adventure_slug}/runs/", operationId: "adventures_runs_create", tags: ["adventures"] },
  auth_login_create: { method: "POST", path: "/api/auth/login/", operationId: "auth_login_create", tags: ["auth"] },
  auth_logout_create: { method: "POST", path: "/api/auth/logout/", operationId: "auth_logout_create", tags: ["auth"] },
  auth_me_retrieve: { method: "GET", path: "/api/auth/me/", operationId: "auth_me_retrieve", tags: ["auth"] },
  auth_password_change_create: { method: "POST", path: "/api/auth/password-change/", operationId: "auth_password_change_create", tags: ["auth"] },
  auth_password_reset_confirm_create: { method: "POST", path: "/api/auth/password-reset/confirm/", operationId: "auth_password_reset_confirm_create", tags: ["auth"] },
  auth_password_reset_request_create: { method: "POST", path: "/api/auth/password-reset/request/", operationId: "auth_password_reset_request_create", tags: ["auth"] },
  auth_refresh_create: { method: "POST", path: "/api/auth/refresh/", operationId: "auth_refresh_create", tags: ["auth"] },
  auth_register_create: { method: "POST", path: "/api/auth/register/", operationId: "auth_register_create", tags: ["auth"] },
  auth_sessions_revoke_all_create: { method: "POST", path: "/api/auth/sessions/revoke-all/", operationId: "auth_sessions_revoke_all_create", tags: ["auth"] },
  auth_sessions_revoke_others_create: { method: "POST", path: "/api/auth/sessions/revoke-others/", operationId: "auth_sessions_revoke_others_create", tags: ["auth"] },
  authoring_chapters_retrieve: { method: "GET", path: "/api/authoring/chapters/", operationId: "authoring_chapters_retrieve", tags: ["authoring"] },
  authoring_chapters_create: { method: "POST", path: "/api/authoring/chapters/", operationId: "authoring_chapters_create", tags: ["authoring"] },
  authoring_chapters_destroy: { method: "DELETE", path: "/api/authoring/chapters/{chapter_id}/", operationId: "authoring_chapters_destroy", tags: ["authoring"] },
  authoring_chapters_partial_update: { method: "PATCH", path: "/api/authoring/chapters/{chapter_id}/", operationId: "authoring_chapters_partial_update", tags: ["authoring"] },
  authoring_command_forms_retrieve: { method: "GET", path: "/api/authoring/command-forms/", operationId: "authoring_command_forms_retrieve", tags: ["authoring"] },
  authoring_content_definitions_retrieve: { method: "GET", path: "/api/authoring/content-definitions/", operationId: "authoring_content_definitions_retrieve", tags: ["authoring"] },
  authoring_content_definitions_create: { method: "POST", path: "/api/authoring/content-definitions/", operationId: "authoring_content_definitions_create", tags: ["authoring"] },
  authoring_content_definitions_retrieve_2: { method: "GET", path: "/api/authoring/content-definitions/{definition_id}/", operationId: "authoring_content_definitions_retrieve_2", tags: ["authoring"] },
  authoring_content_definitions_partial_update: { method: "PATCH", path: "/api/authoring/content-definitions/{definition_id}/", operationId: "authoring_content_definitions_partial_update", tags: ["authoring"] },
  authoring_content_definitions_publish_create: { method: "POST", path: "/api/authoring/content-definitions/{definition_id}/publish/", operationId: "authoring_content_definitions_publish_create", tags: ["authoring"] },
  authoring_content_definitions_remix_create: { method: "POST", path: "/api/authoring/content-definitions/{definition_id}/remix/", operationId: "authoring_content_definitions_remix_create", tags: ["authoring"] },
  authoring_content_definitions_test_run_create: { method: "POST", path: "/api/authoring/content-definitions/{definition_id}/test-run/", operationId: "authoring_content_definitions_test_run_create", tags: ["authoring"] },
  authoring_content_definitions_validate_create: { method: "POST", path: "/api/authoring/content-definitions/{definition_id}/validate/", operationId: "authoring_content_definitions_validate_create", tags: ["authoring"] },
  challenge_runs_destroy: { method: "DELETE", path: "/api/challenge-runs/{run_id}/", operationId: "challenge_runs_destroy", tags: ["challenge-runs"] },
  challenge_runs_retrieve: { method: "GET", path: "/api/challenge-runs/{run_id}/", operationId: "challenge_runs_retrieve", tags: ["challenge-runs"] },
  challenge_runs_files_destroy: { method: "DELETE", path: "/api/challenge-runs/{run_id}/files/", operationId: "challenge_runs_files_destroy", tags: ["challenge-runs"] },
  challenge_runs_files_partial_update: { method: "PATCH", path: "/api/challenge-runs/{run_id}/files/", operationId: "challenge_runs_files_partial_update", tags: ["challenge-runs"] },
  challenge_runs_files_create: { method: "POST", path: "/api/challenge-runs/{run_id}/files/", operationId: "challenge_runs_files_create", tags: ["challenge-runs"] },
  challenge_runs_files_update: { method: "PUT", path: "/api/challenge-runs/{run_id}/files/", operationId: "challenge_runs_files_update", tags: ["challenge-runs"] },
  challenge_runs_retry_create: { method: "POST", path: "/api/challenge-runs/{run_id}/retry/", operationId: "challenge_runs_retry_create", tags: ["challenge-runs"] },
  challenge_runs_submit_command_create: { method: "POST", path: "/api/challenge-runs/{run_id}/submit-command/", operationId: "challenge_runs_submit_command_create", tags: ["challenge-runs"] },
  challenge_trials_runs_create: { method: "POST", path: "/api/challenge-trials/{trial_id}/runs/", operationId: "challenge_trials_runs_create", tags: ["challenge-trials"] },
  chapters_list: { method: "GET", path: "/api/chapters/", operationId: "chapters_list", tags: ["chapters"] },
  chapters_book_retrieve: { method: "GET", path: "/api/chapters/{chapter_id}/book/", operationId: "chapters_book_retrieve", tags: ["chapters"] },
  chapters_overview_retrieve: { method: "GET", path: "/api/chapters/{chapter_id}/overview/", operationId: "chapters_overview_retrieve", tags: ["chapters"] },
  command_forms_preview_retrieve: { method: "GET", path: "/api/command-forms/{form_id}/preview/", operationId: "command_forms_preview_retrieve", tags: ["command-forms"] },
  health_retrieve: { method: "GET", path: "/api/health/", operationId: "health_retrieve", tags: ["health"] },
  health_live_retrieve: { method: "GET", path: "/api/health/live/", operationId: "health_live_retrieve", tags: ["health"] },
  health_ready_retrieve: { method: "GET", path: "/api/health/ready/", operationId: "health_ready_retrieve", tags: ["health"] },
  player_loadout_companion_create: { method: "POST", path: "/api/player/loadout/companion/", operationId: "player_loadout_companion_create", tags: ["player"] },
  player_preferences_retrieve: { method: "GET", path: "/api/player/preferences/", operationId: "player_preferences_retrieve", tags: ["player"] },
  player_preferences_partial_update: { method: "PATCH", path: "/api/player/preferences/", operationId: "player_preferences_partial_update", tags: ["player"] },
  progress_dashboard_retrieve: { method: "GET", path: "/api/progress/dashboard/", operationId: "progress_dashboard_retrieve", tags: ["progress"] },
  progress_stats_retrieve: { method: "GET", path: "/api/progress/stats/", operationId: "progress_stats_retrieve", tags: ["progress"] },
  progress_wallet_retrieve: { method: "GET", path: "/api/progress/wallet/", operationId: "progress_wallet_retrieve", tags: ["progress"] },
  schema_retrieve: { method: "GET", path: "/api/schema/", operationId: "schema_retrieve", tags: ["schema"] },
  shop_catalog_retrieve: { method: "GET", path: "/api/shop/catalog/", operationId: "shop_catalog_retrieve", tags: ["shop"] },
  shop_catalog_purchase_create: { method: "POST", path: "/api/shop/catalog/purchase/", operationId: "shop_catalog_purchase_create", tags: ["shop"] },
  skills_learned_retrieve: { method: "GET", path: "/api/skills/learned/", operationId: "skills_learned_retrieve", tags: ["skills"] },
  stories_list: { method: "GET", path: "/api/stories/", operationId: "stories_list", tags: ["stories"] },
} as const

export type ApiOperationId = keyof typeof apiOperations
export type ApiOperation = (typeof apiOperations)[ApiOperationId]

export type ApiRequestBodyByOperation = {
  admin_analytics_retrieve: null
  admin_chapters_retrieve: null
  admin_chapters_partial_update: { [key: string]: JsonValue }
  admin_content_retrieve: null
  admin_economy_adjust_create: { [key: string]: JsonValue }
  admin_economy_transactions_retrieve: null
  admin_moderation_retrieve: null
  admin_moderation_unpublish_create: { [key: string]: JsonValue }
  admin_overview_retrieve: null
  admin_settings_retrieve: null
  admin_settings_create: { [key: string]: JsonValue }
  admin_stories_retrieve: null
  admin_stories_create: { [key: string]: JsonValue }
  admin_stories_partial_update: { [key: string]: JsonValue }
  admin_users_retrieve: null
  admin_users_retrieve_2: null
  admin_users_actions_create: { [key: string]: JsonValue }
  adventure_levels_runs_create: null
  adventure_runs_destroy: null
  adventure_runs_retrieve: null
  adventure_runs_files_destroy: null
  adventure_runs_files_partial_update: ApiSchemas["PatchedWorkspaceFile"]
  adventure_runs_files_create: ApiSchemas["WorkspaceFile"]
  adventure_runs_files_update: ApiSchemas["WorkspaceFileRename"]
  adventure_runs_level_library_create: null
  adventure_runs_submit_command_create: ApiSchemas["CommandSubmit"]
  adventures_runs_create: null
  auth_login_create: ApiSchemas["Login"]
  auth_logout_create: null
  auth_me_retrieve: null
  auth_password_change_create: ApiSchemas["PasswordChange"]
  auth_password_reset_confirm_create: ApiSchemas["PasswordResetConfirm"]
  auth_password_reset_request_create: ApiSchemas["PasswordResetRequest"]
  auth_refresh_create: null
  auth_register_create: ApiSchemas["Register"]
  auth_sessions_revoke_all_create: null
  auth_sessions_revoke_others_create: null
  authoring_chapters_retrieve: null
  authoring_chapters_create: { [key: string]: JsonValue }
  authoring_chapters_destroy: null
  authoring_chapters_partial_update: { [key: string]: JsonValue }
  authoring_command_forms_retrieve: null
  authoring_content_definitions_retrieve: null
  authoring_content_definitions_create: { [key: string]: JsonValue }
  authoring_content_definitions_retrieve_2: null
  authoring_content_definitions_partial_update: { [key: string]: JsonValue }
  authoring_content_definitions_publish_create: { [key: string]: JsonValue }
  authoring_content_definitions_remix_create: { [key: string]: JsonValue }
  authoring_content_definitions_test_run_create: { [key: string]: JsonValue }
  authoring_content_definitions_validate_create: { [key: string]: JsonValue }
  challenge_runs_destroy: null
  challenge_runs_retrieve: null
  challenge_runs_files_destroy: null
  challenge_runs_files_partial_update: ApiSchemas["PatchedWorkspaceFileCreate"]
  challenge_runs_files_create: ApiSchemas["WorkspaceFileCreate"]
  challenge_runs_files_update: ApiSchemas["WorkspaceFileRename"]
  challenge_runs_retry_create: null
  challenge_runs_submit_command_create: ApiSchemas["CommandSubmit"]
  challenge_trials_runs_create: ApiSchemas["ChallengeRunStart"]
  chapters_list: null
  chapters_book_retrieve: null
  chapters_overview_retrieve: null
  command_forms_preview_retrieve: null
  health_retrieve: null
  health_live_retrieve: null
  health_ready_retrieve: null
  player_loadout_companion_create: ApiSchemas["ShopMutationRequest"]
  player_preferences_retrieve: null
  player_preferences_partial_update: ApiSchemas["PatchedPlayerPreferences"]
  progress_dashboard_retrieve: null
  progress_stats_retrieve: null
  progress_wallet_retrieve: null
  schema_retrieve: null
  shop_catalog_retrieve: null
  shop_catalog_purchase_create: ApiSchemas["ShopMutationRequest"]
  skills_learned_retrieve: null
  stories_list: null
}

export type ApiResponseBodyByOperation = {
  admin_analytics_retrieve: { [key: string]: JsonValue }
  admin_chapters_retrieve: { [key: string]: JsonValue }
  admin_chapters_partial_update: { [key: string]: JsonValue }
  admin_content_retrieve: { [key: string]: JsonValue }
  admin_economy_adjust_create: { [key: string]: JsonValue }
  admin_economy_transactions_retrieve: { [key: string]: JsonValue }
  admin_moderation_retrieve: { [key: string]: JsonValue }
  admin_moderation_unpublish_create: { [key: string]: JsonValue }
  admin_overview_retrieve: { [key: string]: JsonValue }
  admin_settings_retrieve: { [key: string]: JsonValue }
  admin_settings_create: { [key: string]: JsonValue }
  admin_stories_retrieve: { [key: string]: JsonValue }
  admin_stories_create: { [key: string]: JsonValue }
  admin_stories_partial_update: { [key: string]: JsonValue }
  admin_users_retrieve: { [key: string]: JsonValue }
  admin_users_retrieve_2: { [key: string]: JsonValue }
  admin_users_actions_create: { [key: string]: JsonValue }
  adventure_levels_runs_create: ApiSchemas["AdventureRunResponse"]
  adventure_runs_destroy: null
  adventure_runs_retrieve: ApiSchemas["AdventureRunResponse"]
  adventure_runs_files_destroy: ApiSchemas["AdventureRunResponse"]
  adventure_runs_files_partial_update: ApiSchemas["AdventureRunResponse"]
  adventure_runs_files_create: ApiSchemas["AdventureRunResponse"]
  adventure_runs_files_update: ApiSchemas["AdventureRunResponse"]
  adventure_runs_level_library_create: ApiSchemas["AdventureLevelLibraryResponse"]
  adventure_runs_submit_command_create: ApiSchemas["AdventureCommandResponse"]
  adventures_runs_create: ApiSchemas["AdventureRunResponse"]
  auth_login_create: ApiSchemas["LoginResponse"]
  auth_logout_create: null
  auth_me_retrieve: ApiSchemas["User"]
  auth_password_change_create: ApiSchemas["LoginResponse"]
  auth_password_reset_confirm_create: ApiSchemas["DetailResponse"]
  auth_password_reset_request_create: ApiSchemas["DetailResponse"]
  auth_refresh_create: ApiSchemas["AccessTokenResponse"]
  auth_register_create: ApiSchemas["AuthUserResponse"]
  auth_sessions_revoke_all_create: null
  auth_sessions_revoke_others_create: ApiSchemas["DetailResponse"]
  authoring_chapters_retrieve: { [key: string]: JsonValue }
  authoring_chapters_create: { [key: string]: JsonValue }
  authoring_chapters_destroy: null
  authoring_chapters_partial_update: { [key: string]: JsonValue }
  authoring_command_forms_retrieve: { [key: string]: JsonValue }
  authoring_content_definitions_retrieve: { [key: string]: JsonValue }
  authoring_content_definitions_create: { [key: string]: JsonValue }
  authoring_content_definitions_retrieve_2: { [key: string]: JsonValue }
  authoring_content_definitions_partial_update: { [key: string]: JsonValue }
  authoring_content_definitions_publish_create: { [key: string]: JsonValue }
  authoring_content_definitions_remix_create: { [key: string]: JsonValue }
  authoring_content_definitions_test_run_create: { [key: string]: JsonValue }
  authoring_content_definitions_validate_create: { [key: string]: JsonValue }
  challenge_runs_destroy: null
  challenge_runs_retrieve: ApiSchemas["ChallengeRunResponse"]
  challenge_runs_files_destroy: ApiSchemas["ChallengeRunResponse"]
  challenge_runs_files_partial_update: ApiSchemas["ChallengeRunResponse"]
  challenge_runs_files_create: ApiSchemas["ChallengeRunResponse"]
  challenge_runs_files_update: ApiSchemas["ChallengeRunResponse"]
  challenge_runs_retry_create: ApiSchemas["ChallengeRunResponse"]
  challenge_runs_submit_command_create: ApiSchemas["ChallengeCommandResponse"]
  challenge_trials_runs_create: ApiSchemas["ChallengeRunResponse"]
  chapters_list: Array<ApiSchemas["ChapterList"]>
  chapters_book_retrieve: { [key: string]: JsonValue }
  chapters_overview_retrieve: { [key: string]: JsonValue }
  command_forms_preview_retrieve: ApiSchemas["CommandFormPreviewResponse"]
  health_retrieve: { [key: string]: JsonValue }
  health_live_retrieve: { [key: string]: JsonValue }
  health_ready_retrieve: { [key: string]: JsonValue }
  player_loadout_companion_create: ApiSchemas["ShopEquipResponse"]
  player_preferences_retrieve: ApiSchemas["PlayerPreferences"]
  player_preferences_partial_update: ApiSchemas["PlayerPreferences"]
  progress_dashboard_retrieve: ApiSchemas["DashboardSummaryResponse"]
  progress_stats_retrieve: ApiSchemas["StatsSummaryResponse"]
  progress_wallet_retrieve: ApiSchemas["WalletSummaryResponse"]
  schema_retrieve: { [key: string]: JsonValue }
  shop_catalog_retrieve: ApiSchemas["ShopResponse"]
  shop_catalog_purchase_create: ApiSchemas["ShopPurchaseResponse"]
  skills_learned_retrieve: ApiSchemas["LearnedSkillsResponse"]
  stories_list: Array<ApiSchemas["Story"]>
}

export type ApiRequestBody<TOperation extends ApiOperationId> = ApiRequestBodyByOperation[TOperation]
export type ApiResponseBody<TOperation extends ApiOperationId> = ApiResponseBodyByOperation[TOperation]
