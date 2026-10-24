// GENERATED FILE. DO NOT EDIT.
// Source: backend DRF/drf-spectacular OpenAPI schema.
// Regenerate with: python scripts/generate_api_contract.py

export type JsonPrimitive = string | number | boolean | null
export type JsonValue = JsonPrimitive | JsonObject | JsonValue[]
export type JsonObject = { [key: string]: JsonValue }

export type ApiSchemas = {
  "AccessTokenResponse": { "access": string }
  "ActivityWindowEnum": "month" | "week" | "year"
  "AdminAnalyticsResponse": { "active_learners_30d": number; "completions": ApiSchemas["AdminCompletions"]; "kpi_range": ApiSchemas["AdminKpiRange"]; "objectives": { [key: string]: ApiSchemas["RateMetric"] }; "per_story": Array<ApiSchemas["AdminStoryAnalytics"]>; "runebound_performance": ApiSchemas["PerformanceSummaryResponse"]; "runs": ApiSchemas["AdminRuns"] }
  "AdminChapter": { "battle_stage": { [key: string]: JsonValue }; "description": string; "id": number; "is_playable": boolean; "is_published": boolean; "management_source": string; "number": number; "slug": string; "sort_order": number; "story_id": number | null; "title": string }
  "AdminChapterCreateRequest": { "battle_stage"?: { [key: string]: JsonValue }; "description"?: string; "is_playable"?: boolean; "is_published"?: boolean; "number": number; "slug": string; "sort_order"?: number; "story_id": number; "title": string }
  "AdminChapterListResponse": { "results": Array<ApiSchemas["AdminChapter"]> }
  "AdminCompletions": { "adventure": number; "challenge": number; "total": number }
  "AdminEconomyAdjustRequest": { "amount": number; "reason": string; "request_id": string; "user_id": number }
  "AdminEconomyAdjustResponse": { "applied": boolean; "wallet": ApiSchemas["WalletSummary"] }
  "AdminFeatureFlag": { "description": string; "enabled": boolean; "key": ApiSchemas["KeyEnum"]; "label": string }
  "AdminFeatureFlagUpdateRequest": { "enabled": boolean; "key": ApiSchemas["KeyEnum"] }
  "AdminKpiRange": { "end_date": string | null; "start_date": string | null; "timezone": string }
  "AdminOverviewEconomy": { "coins_in_circulation": number; "coins_spent": number; "signup_grant": number }
  "AdminOverviewResponse": { "economy": ApiSchemas["AdminOverviewEconomy"]; "recent_admin_actions": Array<ApiSchemas["AdminRecentAction"]>; "recent_purchases": Array<ApiSchemas["AdminRecentPurchase"]>; "recent_signups": Array<ApiSchemas["AdminUserBrief"]>; "users": ApiSchemas["AdminOverviewUsers"] }
  "AdminOverviewUsers": { "new_30d": number; "new_7d": number; "total": number }
  "AdminRecentAction": { "action": string; "actor": string | null; "created_at": string; "id": number; "target_label": string }
  "AdminRecentPurchase": { "amount": number; "created_at": string; "reason": string; "user_id": number; "username": string }
  "AdminRunBreakdown": { "by_status": { [key: string]: number }; "passed": number; "total": number }
  "AdminRuns": { "adventure": ApiSchemas["AdminRunBreakdown"]; "by_status": { [key: string]: number }; "challenge": ApiSchemas["AdminRunBreakdown"]; "passed": number; "total": number }
  "AdminSettingsResponse": { "feature_flags": Array<ApiSchemas["AdminFeatureFlag"]> }
  "AdminStory": { "chapter_count": number; "difficulty": ApiSchemas["DifficultyEnum"]; "id": number; "is_published": boolean; "management_source": string; "prerequisite_story": ApiSchemas["AdminStoryPrerequisite"] | null; "slug": string; "sort_order": number; "summary": string; "title": string; "world_slug": string }
  "AdminStoryAnalytics": { "adventure_runs": number; "challenge_runs": number; "passed": number; "runs": number; "slug": string; "title": string }
  "AdminStoryCreateRequest": { "difficulty"?: ApiSchemas["DifficultyEnum"]; "is_published"?: boolean; "prerequisite_story"?: number | null; "slug": string; "sort_order"?: number; "summary"?: string; "title": string; "world_slug": string }
  "AdminStoryListResponse": { "results": Array<ApiSchemas["AdminStory"]>; "world_options": Array<string> }
  "AdminStoryPrerequisite": { "id": number; "slug": string; "title": string }
  "AdminTransaction": { "amount": number; "created_at": string; "id": number; "reason": string; "user_id": number; "username": string }
  "AdminTransactionListResponse": { "results": Array<ApiSchemas["AdminTransaction"]> }
  "AdminUserActionRequest": { "action": ApiSchemas["AdminUserActionRequestActionEnum"]; "amount"?: number; "reason"?: string; "request_id"?: string; "value"?: boolean }
  "AdminUserActionRequestActionEnum": "grant_coins" | "set_staff" | "set_active"
  "AdminUserBrief": { "date_joined": string; "email": string; "id": number; "is_active": boolean; "is_staff": boolean; "username": string }
  "AdminUserDetail": { "date_joined": string; "email": string; "entitlement_count": number; "id": number; "is_active": boolean; "is_staff": boolean; "last_login": string | null; "username": string; "wallet": ApiSchemas["WalletSummary"] }
  "AdminUserKpisResponse": { "has_data": boolean; "kpis": ApiSchemas["PerformanceKpiSet"] | null; "modules": Array<ApiSchemas["PerformanceModule"]> }
  "AdminUserListResponse": { "results": Array<ApiSchemas["AdminUserBrief"]> }
  "AdventureLevelTierCommandResponse": { "command_family": string; "command_outcome": { [key: string]: JsonValue }; "diagnostic_metadata": Array<string>; "exit_code": number; "learned_skills"?: Array<ApiSchemas["LearnedSkillResponse"]>; "run": ApiSchemas["AdventureLevelTierCommandRunResponse"]; "stderr": string; "stdout": string; "step": ApiSchemas["AdventureLevelTierCommandStepResponse"] }
  "AdventureLevelTierCommandRunResponse": { "completed_at": string | null; "completion"?: { [key: string]: JsonValue } | null; "counts": { [key: string]: JsonValue }; "failure_reason": string | null; "id": number; "next_difficulty"?: { [key: string]: JsonValue } | null; "progress"?: { [key: string]: JsonValue }; "replay": boolean; "repository_state": { [key: string]: JsonValue }; "rewards"?: { [key: string]: JsonValue } | null; "stars": number; "status": ApiSchemas["GameplayRunStatus"]; "tutor": ApiSchemas["CommandIntroductionResponse"] | null; "visualization": { [key: string]: JsonValue } }
  "AdventureLevelTierCommandStepResponse": { "command_classification": string; "command_text": string; "contextual_feedback": string; "created_at": string; "evaluation_result": string; "id": number; "result_category": string; "terminal_output": string; "visualization_snapshot": { [key: string]: JsonValue } }
  "AdventureLevelTierRewardResponse": { "claimed": boolean; "coins": number }
  "AdventureLevelTierRunResponse": { "chapter": { [key: string]: JsonValue } | null; "completed_at": string | null; "completion": { [key: string]: JsonValue } | null; "counts": { [key: string]: JsonValue }; "difficulty": string | null; "expected_state": { [key: string]: JsonValue } | null; "failure_reason": string | null; "id": number; "next_difficulty": { [key: string]: JsonValue } | null; "policy": { [key: string]: JsonValue }; "progress": { [key: string]: JsonValue }; "replay": boolean; "repository_state": { [key: string]: JsonValue }; "reward": ApiSchemas["AdventureLevelTierRewardResponse"]; "scaffolding": { [key: string]: JsonValue }; "scenario": ApiSchemas["AdventureLevelTierScenarioPositionResponse"]; "scenario_context": { [key: string]: JsonValue }; "stars": number; "status": ApiSchemas["GameplayRunStatus"]; "steps": Array<ApiSchemas["AdventureLevelTierRunStepResponse"]>; "story": { [key: string]: JsonValue } | null; "tier": { [key: string]: JsonValue }; "transfer"?: boolean; "tutor": ApiSchemas["CommandIntroductionResponse"] | null; "variant": { [key: string]: JsonValue }; "visualization": { [key: string]: JsonValue } }
  "AdventureLevelTierRunStart": { "prior_run_id"?: number | null; "replay"?: boolean; "source_entry_point"?: ApiSchemas["SourceEntryPointEnum"]; "transfer"?: boolean }
  "AdventureLevelTierRunStepResponse": { "command_classification": string; "command_text": string; "contextual_feedback": string; "created_at": string; "id": number; "result_category": string; "terminal_output": string; "visualization_snapshot": { [key: string]: JsonValue } }
  "AdventureLevelTierScenarioPositionResponse": { "index": number | null; "title": string; "total": number }
  "ChallengeCommandResponse": { "command_family": string; "command_outcome": { [key: string]: JsonValue }; "diagnostic_metadata": Array<string>; "exit_code": number; "run": ApiSchemas["ChallengeCommandRunResponse"]; "stderr": string; "stdout": string; "step": ApiSchemas["ChallengeCommandStepResponse"] }
  "ChallengeCommandRunResponse": { "completed_at": string | null; "completion"?: { [key: string]: JsonValue } | null; "counts": { [key: string]: JsonValue }; "failure_reason": string | null; "id": number; "mastery_progress"?: { [key: string]: JsonValue }; "next_difficulty"?: { [key: string]: JsonValue } | null; "replay": boolean; "repository_state": { [key: string]: JsonValue }; "sibling_levels"?: Array<{ [key: string]: JsonValue }>; "stars": number; "status": ApiSchemas["GameplayRunStatus"]; "visualization": { [key: string]: JsonValue } }
  "ChallengeCommandStepResponse": { "command_classification": string; "command_text": string; "contextual_feedback": string; "created_at": string; "evaluation_result": string; "id": number; "result_category": string; "terminal_output": string; "visualization_snapshot": { [key: string]: JsonValue } }
  "ChallengeRunResponse": { "challenge": { [key: string]: JsonValue }; "chapter": { [key: string]: JsonValue }; "completed_at": string | null; "completion": { [key: string]: JsonValue } | null; "counts": { [key: string]: JsonValue }; "difficulty": string | null; "expected_state": { [key: string]: JsonValue } | null; "failure_reason": string | null; "id": number; "mastery_progress": { [key: string]: JsonValue }; "next_difficulty": { [key: string]: JsonValue } | null; "policy": { [key: string]: JsonValue }; "replay": boolean; "repository_state": { [key: string]: JsonValue }; "reward_coins": number; "scaffolding": { [key: string]: JsonValue }; "scenario_context": { [key: string]: JsonValue }; "sibling_levels": Array<{ [key: string]: JsonValue }>; "stars": number; "status": ApiSchemas["GameplayRunStatus"]; "steps": Array<ApiSchemas["ChallengeRunStepResponse"]>; "story": { [key: string]: JsonValue } | null; "variant": { [key: string]: JsonValue }; "visualization": { [key: string]: JsonValue } }
  "ChallengeRunStart": { "prior_run_id"?: number | null; "replay"?: boolean; "source_entry_point"?: ApiSchemas["SourceEntryPointEnum"] }
  "ChallengeRunStepResponse": { "command_classification": string; "command_text": string; "contextual_feedback": string; "created_at": string; "id": number; "result_category": string; "terminal_output": string; "visualization_snapshot": { [key: string]: JsonValue } }
  "ChapterChestOpen": { "threshold": number }
  "ChapterChestReward": { "coins": number; "threshold": number }
  "ChapterChestRewards": { "balance": number; "coins_awarded": number; "results": Array<ApiSchemas["ChapterChestState"]> }
  "ChapterChestState": { "claimed": boolean; "coins": number; "threshold": number; "unlocked": boolean }
  "ChapterLevelCompletion": { "denominator": number; "numerator": number; "value": number }
  "ChapterList": { "adventure_level_count": number; "challenge_count": number; "chest_schedule": Array<ApiSchemas["ChapterChestReward"]>; "command_skill_count": number; "description": string; "id": number; "is_orientation": boolean; "is_playable": boolean; "level_completion": ApiSchemas["ChapterLevelCompletion"]; "lock_reason": string; "locked": boolean; "number": number; "slug": string; "sort_order": number; "story": ApiSchemas["ChapterStory"] | null; "title": string }
  "ChapterOrientationComplete": { "highest_step_seen": number }
  "ChapterOrientationLessonDetail": { "content_html": string; "highest_step_seen": number; "id": number; "interaction_steps": JsonValue; "is_complete": boolean; "scoped_css": string; "slug": string; "sort_order": number; "subtitle": string; "title": string }
  "ChapterOrientationLessonList": { "id": number; "is_complete": boolean; "slug": string; "sort_order": number; "subtitle": string; "title": string }
  "ChapterStory": { "id": number; "slug": string; "title": string; "world_slug": string }
  "ClientCommandExecution": { "client_run_revision"?: number | null; "command_family": string; "cwd"?: string; "diagnostic": boolean; "diagnostic_metadata": Array<string>; "exit_code": number; "next_state": { [key: string]: JsonValue }; "normalized_command": string; "output": string; "processed": boolean; "stderr": string; "stdout": string }
  "CommandFormPreviewResponse": { "command_preview": { [key: string]: JsonValue }; "id": number; "is_playable": boolean; "label": string; "skill": ApiSchemas["CommandFormPreviewSkillResponse"]; "slug": string; "summary": string; "usage_form": string }
  "CommandFormPreviewSkillResponse": { "base_command": string; "id": number; "slug": string; "title": string }
  "CommandIntroductionForm": { "label": string; "summary": string; "teaching_key": string; "usage_form": string }
  "CommandIntroductionResponse": { "anatomy": Array<ApiSchemas["SyntaxPart"]>; "changes": Array<ApiSchemas["RepositoryChange"]>; "command_form": ApiSchemas["CommandIntroductionForm"]; "completion_token": string | null; "concepts": Array<ApiSchemas["Concept"]>; "context_id": string; "explanation": string | null; "help_token": string; "needs": Array<ApiSchemas["RepositoryChange"]>; "phase": ApiSchemas["PhaseEnum"]; "run_revision": number; "teaching_key": string; "title": string; "verdict": ApiSchemas["VerdictEnum"] | ApiSchemas["NullEnum"] | null }
  "CommandKnowledgeResponse": { "command": string; "id": string; "kind": ApiSchemas["CommandKnowledgeResponseKindEnum"]; "syntax": string; "text": string; "title": string; "token": string; "when_to_use": string }
  "CommandKnowledgeResponseKindEnum": "command" | "option" | "argument"
  "CommandSubmit": { "command": string; "execution": ApiSchemas["ClientCommandExecution"] }
  "Concept": { "key": string; "text": string; "title": string }
  "DashboardCounts": { "abandoned": number; "completed": number; "failed": number; "started": number }
  "DashboardKpiSet": { "arc": ApiSchemas["RateMetric"]; "hlcr": ApiSchemas["RateMetric"]; "scr": ApiSchemas["RateMetric"] }
  "DashboardRetryTrend": { "attempts": number; "label": string; "level_title": string; "retries": number }
  "DashboardSummaryResponse": { "chapter_kpis": { [key: string]: ApiSchemas["DashboardKpiSet"] }; "completed_stories": Array<string>; "completed_story_slug": string | null; "counts": ApiSchemas["DashboardCounts"]; "kpis": ApiSchemas["DashboardKpiSet"]; "mastery": number; "perfect_clears": number; "retry_trends": Array<ApiSchemas["DashboardRetryTrend"]> }
  "DetailResponse": { "detail": string }
  "DifficultyEnum": "beginner" | "intermediate" | "advanced"
  "DrillBlank": { "answer": string; "index": number; "options": Array<ApiSchemas["DrillChoice"]> }
  "DrillCard": { "bank": Array<string>; "base_command": string; "blank": ApiSchemas["DrillBlank"] | null; "command": string; "command_choices": Array<ApiSchemas["DrillChoice"]>; "intent": string; "intent_choices": Array<ApiSchemas["DrillChoice"]>; "key": string; "summary": string; "tokens": Array<string> }
  "DrillChoice": { "gloss": string; "value": string }
  "DrillLevel": { "chapter_id": number | null; "chapter_number": number | null; "chapter_title": string; "description": string; "id": number; "slug": string; "story_slug": string; "story_title": string; "title": string }
  "DrillProgress": { "best_accuracy": number; "cleared": boolean; "clears": number; "first_cleared_at": string | null; "last_accuracy": number; "last_played_at": string | null; "sessions": number; "shaky_form_keys": Array<string> }
  "DrillReport": { "answers_correct": number; "answers_total": number; "completed": boolean; "shaky_form_keys"?: Array<string> }
  "DrillReportResponse": { "progress": ApiSchemas["DrillProgress"] }
  "DrillResume": { "answered": number; "correct": number; "id": number; "queue_state": { [key: string]: JsonValue }; "updated_at": string }
  "DrillRunState": { "answered": number; "cards": { [key: string]: { [key: string]: JsonValue } }; "correct": number; "queue": Array<string>; "sequence_pending"?: boolean }
  "DrillRunStateResponse": { "resume": ApiSchemas["DrillResume"] | null }
  "DrillSequence": { "label": string; "steps": Array<string>; "task": string }
  "EmailVerificationConfirm": { "code": string; "email": string }
  "EmailVerificationRequired": { "code": ApiSchemas["EmailVerificationRequiredCodeEnum"]; "detail": string; "email": string }
  "EmailVerificationRequiredCodeEnum": "email_unverified"
  "EmailVerificationResend": { "email": string }
  "GameplayRunStatus": "started" | "completed" | "failed" | "abandoned"
  "IntroductionComplete": { "token": string }
  "IntroductionCompleteResponse": { "tutor": ApiSchemas["CommandIntroductionResponse"] | null }
  "KeyEnum": "shop-purchases"
  "LearnedSkillResponse": { "base_command": string; "chapter_id"?: number | null; "chapter_number": number; "chapter_title": string; "id": number; "knowledge"?: Array<ApiSchemas["CommandKnowledgeResponse"]>; "learned_at": string; "slug": string; "summary": string; "title": string }
  "LearnedSkillsResponse": { "results": Array<ApiSchemas["LearnedSkillResponse"]> }
  "LevelDrillPlanResponse": { "available": boolean; "cards": Array<ApiSchemas["DrillCard"]>; "level": ApiSchemas["DrillLevel"]; "progress": ApiSchemas["DrillProgress"]; "resume": ApiSchemas["DrillResume"] | null; "sequence": ApiSchemas["DrillSequence"] | null }
  "Login": { "identifier": string; "password": string }
  "MotionModeEnum": "system" | "reduced" | "full"
  "NullEnum": null
  "OAuthTicketExchange": { "ticket": string }
  "OnboardingPhaseEnum": "welcome" | "orientation" | "stories" | "shop" | "purchase" | "home" | "equip" | "done"
  "PasswordChange": { "current_password": string; "password": string; "password_confirm": string }
  "PasswordResetConfirm": { "password": string; "password_confirm": string; "token": string; "uid": string }
  "PasswordResetRequest": { "email": string }
  "PatchedAdminChapterUpdateRequest": { "battle_stage"?: { [key: string]: JsonValue }; "description"?: string; "is_playable"?: boolean; "is_published"?: boolean; "number"?: number; "sort_order"?: number; "title"?: string }
  "PatchedAdminStoryUpdateRequest": { "difficulty"?: ApiSchemas["DifficultyEnum"]; "is_published"?: boolean; "prerequisite_story"?: number | null; "sort_order"?: number; "summary"?: string; "title"?: string; "world_slug"?: string }
  "PatchedPlayerPreferences": { "motion_mode"?: ApiSchemas["MotionModeEnum"]; "onboarding_phase"?: ApiSchemas["OnboardingPhaseEnum"] }
  "PerformanceKpiSet": { "arc": ApiSchemas["RateMetric"]; "car": ApiSchemas["RateMetric"]; "hlcr": ApiSchemas["RateMetric"]; "retry_success_rate": ApiSchemas["RateMetric"]; "rta": ApiSchemas["RateMetric"]; "rtr"?: ApiSchemas["RateMetric"]; "scr": ApiSchemas["RateMetric"] }
  "PerformanceModule": { "arc": ApiSchemas["RateMetric"]; "car": ApiSchemas["RateMetric"]; "hlcr": ApiSchemas["RateMetric"]; "number": number; "retry_success_rate": ApiSchemas["RateMetric"]; "rta": ApiSchemas["RateMetric"]; "rtr"?: ApiSchemas["RateMetric"]; "scr": ApiSchemas["RateMetric"]; "title": string }
  "PerformanceSamples": { "attempted_tiers": number; "car_missing": number; "car_scored": number; "in_progress_tiers": number; "mastered_tiers": number; "mastery_missing": number; "participants": number; "transfer_assigned": number; "transfer_missing": number; "transfer_pending": number }
  "PerformanceSummaryResponse": { "completed_sessions": number; "kpis": ApiSchemas["PerformanceKpiSet"]; "modules": Array<ApiSchemas["PerformanceModule"]>; "samples": ApiSchemas["PerformanceSamples"]; "transfers": Array<ApiSchemas["TransferCheckpoint"]> }
  "PhaseEnum": "introduction" | "feedback"
  "PlayerPreferences": { "motion_mode"?: ApiSchemas["MotionModeEnum"]; "onboarding_phase"?: ApiSchemas["OnboardingPhaseEnum"] }
  "RateMetric": { "denominator": number; "numerator": number; "unit"?: ApiSchemas["UnitEnum"]; "value": number | null }
  "Register": { "email": string; "password": string; "password_confirm": string; "username": string }
  "RegisterResponse": { "user": ApiSchemas["User"] }
  "RepositoryChange": { "action"?: ApiSchemas["RepositoryChangeActionEnum"]; "kind": ApiSchemas["RepositoryChangeKindEnum"]; "ref"?: string; "subjects"?: Array<string>; "text": string }
  "RepositoryChangeActionEnum": "create" | "delete" | "move" | "add" | "remove" | "set" | "start" | "finish"
  "RepositoryChangeKindEnum": "repository" | "commit" | "branch" | "head" | "staging" | "working_tree" | "conflict" | "tag" | "remote" | "config" | "stash" | "operation"
  "ResponseKindEnum": "answer" | "guarded" | "unavailable"
  "RoleEnum": "user" | "assistant"
  "SessionResponse": { "access": string; "user": ApiSchemas["User"] }
  "ShopEquipResponse": { "active_companion": string | null; "shop": ApiSchemas["ShopResponse"] }
  "ShopItemResponse": { "active": boolean; "kind": ApiSchemas["ShopItemResponseKindEnum"]; "label": string; "owned": boolean; "price": number; "slug": string }
  "ShopItemResponseKindEnum": "companion"
  "ShopMutationRequest": { "kind": string; "slug": string }
  "ShopPurchaseResponse": { "owned": boolean; "shop": ApiSchemas["ShopResponse"]; "wallet": ApiSchemas["WalletSummaryResponse"] }
  "ShopResponse": { "active_companion": string | null; "items": Array<ApiSchemas["ShopItemResponse"]>; "purchases_enabled": boolean }
  "SourceEntryPointEnum": "level_page" | "retry"
  "StatsActivityResponse": { "activity_trend": Array<ApiSchemas["StatsTrendPoint"]>; "activity_window": ApiSchemas["ActivityWindowEnum"] }
  "StatsHeadline": { "accuracy": number | null; "comebacks": ApiSchemas["StatsScopedCount"]; "commands_run": number; "finish_rate": ApiSchemas["RateMetric"]; "gate_trial_clears": number; "gitcoins": number; "gitcoins_earned": number; "hard_gate_trial_clears": number; "hard_tier_clears": ApiSchemas["StatsScopedCount"]; "levels_completed": number; "perfect_clears": number }
  "StatsScopedCount": { "scope": string; "value": number }
  "StatsSkillAxis": { "command": string; "hint": string; "key": string; "label": string; "value": number | null }
  "StatsSummaryResponse": { "activity_trend": Array<ApiSchemas["StatsTrendPoint"]>; "activity_window": ApiSchemas["ActivityWindowEnum"]; "headline": ApiSchemas["StatsHeadline"]; "skill_profile": Array<ApiSchemas["StatsSkillAxis"]> }
  "StatsTrendPoint": { "commands_run": number; "date": string; "levels_completed": number }
  "Story": { "completed": boolean; "difficulty": ApiSchemas["DifficultyEnum"]; "id": number; "is_published": boolean; "lock_reason": string; "locked": boolean; "prerequisite_story": ApiSchemas["StoryPrerequisite"] | null; "slug": string; "sort_order": number; "summary": string; "title": string; "world_slug": string }
  "StoryPrerequisite": { "completed": boolean; "slug": string; "title": string }
  "SurfaceEnum": "home" | "command_guide"
  "SyntaxPart": { "text": string; "token": string }
  "TransferCheckpoint": { "run_id": number | null; "tier_id": number; "title": string }
  "TutorChatContext": { "guide_token"?: string; "run_id"?: number; "surface": ApiSchemas["SurfaceEnum"]; "teaching_key"?: string; "usage_form"?: string }
  "TutorChatRequest": { "context": ApiSchemas["TutorChatContext"]; "history"?: Array<ApiSchemas["TutorChatTurn"]>; "message": string }
  "TutorChatResponse": { "reply": string; "response_kind": ApiSchemas["ResponseKindEnum"]; "scenario_related": boolean; "suggested_topics": Array<ApiSchemas["TutorTopic"]> }
  "TutorChatTurn": { "role": ApiSchemas["RoleEnum"]; "text": string }
  "TutorTopic": { "id": string; "title": string }
  "UnitEnum": "participants"
  "User": { "email": string; "id": number; "is_staff": boolean; "username": string }
  "VerdictEnum": "correct" | "incorrect"
  "WalletSummary": { "balance": number }
  "WalletSummaryResponse": { "balance": number }
  "WorkspaceFile": { "content"?: string; "path": string }
  "WorkspaceFileRename": { "new_path": string; "path": string }
}

export type ApiPath =
  | "/api/admin/analytics/"
  | "/api/admin/chapters/"
  | "/api/admin/chapters/{chapter_id}/"
  | "/api/admin/economy/adjust/"
  | "/api/admin/economy/transactions/"
  | "/api/admin/overview/"
  | "/api/admin/settings/"
  | "/api/admin/stories/"
  | "/api/admin/stories/{story_id}/"
  | "/api/admin/users/"
  | "/api/admin/users/{user_id}/"
  | "/api/admin/users/{user_id}/actions/"
  | "/api/admin/users/{user_id}/kpis/"
  | "/api/adventure-level-tiers/{tier_id}/runs/"
  | "/api/adventure-levels/{level_id}/drill/"
  | "/api/adventure-levels/{level_id}/drill/results/"
  | "/api/adventure-levels/{level_id}/drill/run/"
  | "/api/adventure-tier-runs/{run_id}/"
  | "/api/adventure-tier-runs/{run_id}/files/"
  | "/api/adventure-tier-runs/{run_id}/introduction/complete/"
  | "/api/adventure-tier-runs/{run_id}/retry/"
  | "/api/adventure-tier-runs/{run_id}/submit-command/"
  | "/api/auth/email-verification/confirm/"
  | "/api/auth/email-verification/resend/"
  | "/api/auth/login/"
  | "/api/auth/logout/"
  | "/api/auth/me/"
  | "/api/auth/oauth/exchange/"
  | "/api/auth/password-change/"
  | "/api/auth/password-reset/confirm/"
  | "/api/auth/password-reset/request/"
  | "/api/auth/refresh/"
  | "/api/auth/register/"
  | "/api/auth/sessions/revoke-all/"
  | "/api/auth/sessions/revoke-others/"
  | "/api/challenge-runs/{run_id}/"
  | "/api/challenge-runs/{run_id}/files/"
  | "/api/challenge-runs/{run_id}/retry/"
  | "/api/challenge-runs/{run_id}/submit-command/"
  | "/api/challenge-trials/{trial_id}/runs/"
  | "/api/chapters/"
  | "/api/chapters/{chapter_id}/book/"
  | "/api/chapters/{chapter_id}/chests/"
  | "/api/chapters/{chapter_id}/orientation/"
  | "/api/chapters/{chapter_id}/overview/"
  | "/api/command-forms/{form_id}/preview/"
  | "/api/health/"
  | "/api/health/live/"
  | "/api/health/ready/"
  | "/api/orientation-lessons/{lesson_id}/"
  | "/api/orientation-lessons/{lesson_id}/complete/"
  | "/api/player/loadout/companion/"
  | "/api/player/preferences/"
  | "/api/progress/dashboard/"
  | "/api/progress/performance/"
  | "/api/progress/stats/"
  | "/api/progress/stats/activity/"
  | "/api/progress/wallet/"
  | "/api/schema/"
  | "/api/shop/catalog/"
  | "/api/shop/catalog/purchase/"
  | "/api/skills/learned/"
  | "/api/stories/"
  | "/api/tutoring/chat/"

export type ApiMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS'

export type ApiMethodByPath = {
  "/api/admin/analytics/": "GET"
  "/api/admin/chapters/": "GET" | "POST"
  "/api/admin/chapters/{chapter_id}/": "PATCH"
  "/api/admin/economy/adjust/": "POST"
  "/api/admin/economy/transactions/": "GET"
  "/api/admin/overview/": "GET"
  "/api/admin/settings/": "GET" | "POST"
  "/api/admin/stories/": "GET" | "POST"
  "/api/admin/stories/{story_id}/": "PATCH"
  "/api/admin/users/": "GET"
  "/api/admin/users/{user_id}/": "GET"
  "/api/admin/users/{user_id}/actions/": "POST"
  "/api/admin/users/{user_id}/kpis/": "GET"
  "/api/adventure-level-tiers/{tier_id}/runs/": "POST"
  "/api/adventure-levels/{level_id}/drill/": "GET"
  "/api/adventure-levels/{level_id}/drill/results/": "POST"
  "/api/adventure-levels/{level_id}/drill/run/": "DELETE" | "PUT"
  "/api/adventure-tier-runs/{run_id}/": "DELETE" | "GET"
  "/api/adventure-tier-runs/{run_id}/files/": "DELETE" | "PATCH" | "POST" | "PUT"
  "/api/adventure-tier-runs/{run_id}/introduction/complete/": "POST"
  "/api/adventure-tier-runs/{run_id}/retry/": "POST"
  "/api/adventure-tier-runs/{run_id}/submit-command/": "POST"
  "/api/auth/email-verification/confirm/": "POST"
  "/api/auth/email-verification/resend/": "POST"
  "/api/auth/login/": "POST"
  "/api/auth/logout/": "POST"
  "/api/auth/me/": "GET"
  "/api/auth/oauth/exchange/": "POST"
  "/api/auth/password-change/": "POST"
  "/api/auth/password-reset/confirm/": "POST"
  "/api/auth/password-reset/request/": "POST"
  "/api/auth/refresh/": "POST"
  "/api/auth/register/": "POST"
  "/api/auth/sessions/revoke-all/": "POST"
  "/api/auth/sessions/revoke-others/": "POST"
  "/api/challenge-runs/{run_id}/": "DELETE" | "GET"
  "/api/challenge-runs/{run_id}/files/": "DELETE" | "PATCH" | "POST" | "PUT"
  "/api/challenge-runs/{run_id}/retry/": "POST"
  "/api/challenge-runs/{run_id}/submit-command/": "POST"
  "/api/challenge-trials/{trial_id}/runs/": "POST"
  "/api/chapters/": "GET"
  "/api/chapters/{chapter_id}/book/": "GET"
  "/api/chapters/{chapter_id}/chests/": "GET" | "POST"
  "/api/chapters/{chapter_id}/orientation/": "GET"
  "/api/chapters/{chapter_id}/overview/": "GET"
  "/api/command-forms/{form_id}/preview/": "GET"
  "/api/health/": "GET"
  "/api/health/live/": "GET"
  "/api/health/ready/": "GET"
  "/api/orientation-lessons/{lesson_id}/": "GET"
  "/api/orientation-lessons/{lesson_id}/complete/": "POST"
  "/api/player/loadout/companion/": "POST"
  "/api/player/preferences/": "GET" | "PATCH"
  "/api/progress/dashboard/": "GET"
  "/api/progress/performance/": "GET"
  "/api/progress/stats/": "GET"
  "/api/progress/stats/activity/": "GET"
  "/api/progress/wallet/": "GET"
  "/api/schema/": "GET"
  "/api/shop/catalog/": "GET"
  "/api/shop/catalog/purchase/": "POST"
  "/api/skills/learned/": "GET"
  "/api/stories/": "GET"
  "/api/tutoring/chat/": "POST"
}

export const apiOperations = {
  admin_analytics_retrieve: { method: "GET", path: "/api/admin/analytics/", operationId: "admin_analytics_retrieve", tags: ["admin"] },
  admin_chapters_retrieve: { method: "GET", path: "/api/admin/chapters/", operationId: "admin_chapters_retrieve", tags: ["admin"] },
  admin_chapters_create: { method: "POST", path: "/api/admin/chapters/", operationId: "admin_chapters_create", tags: ["admin"] },
  admin_chapters_partial_update: { method: "PATCH", path: "/api/admin/chapters/{chapter_id}/", operationId: "admin_chapters_partial_update", tags: ["admin"] },
  admin_economy_adjust_create: { method: "POST", path: "/api/admin/economy/adjust/", operationId: "admin_economy_adjust_create", tags: ["admin"] },
  admin_economy_transactions_retrieve: { method: "GET", path: "/api/admin/economy/transactions/", operationId: "admin_economy_transactions_retrieve", tags: ["admin"] },
  admin_overview_retrieve: { method: "GET", path: "/api/admin/overview/", operationId: "admin_overview_retrieve", tags: ["admin"] },
  admin_settings_retrieve: { method: "GET", path: "/api/admin/settings/", operationId: "admin_settings_retrieve", tags: ["admin"] },
  admin_settings_create: { method: "POST", path: "/api/admin/settings/", operationId: "admin_settings_create", tags: ["admin"] },
  admin_stories_retrieve: { method: "GET", path: "/api/admin/stories/", operationId: "admin_stories_retrieve", tags: ["admin"] },
  admin_stories_create: { method: "POST", path: "/api/admin/stories/", operationId: "admin_stories_create", tags: ["admin"] },
  admin_stories_partial_update: { method: "PATCH", path: "/api/admin/stories/{story_id}/", operationId: "admin_stories_partial_update", tags: ["admin"] },
  admin_users_retrieve: { method: "GET", path: "/api/admin/users/", operationId: "admin_users_retrieve", tags: ["admin"] },
  admin_users_retrieve_2: { method: "GET", path: "/api/admin/users/{user_id}/", operationId: "admin_users_retrieve_2", tags: ["admin"] },
  admin_users_actions_create: { method: "POST", path: "/api/admin/users/{user_id}/actions/", operationId: "admin_users_actions_create", tags: ["admin"] },
  admin_users_kpis_retrieve: { method: "GET", path: "/api/admin/users/{user_id}/kpis/", operationId: "admin_users_kpis_retrieve", tags: ["admin"] },
  adventure_level_tiers_runs_create: { method: "POST", path: "/api/adventure-level-tiers/{tier_id}/runs/", operationId: "adventure_level_tiers_runs_create", tags: ["adventure-level-tiers"] },
  adventure_levels_drill_retrieve: { method: "GET", path: "/api/adventure-levels/{level_id}/drill/", operationId: "adventure_levels_drill_retrieve", tags: ["adventure-levels"] },
  adventure_levels_drill_results_create: { method: "POST", path: "/api/adventure-levels/{level_id}/drill/results/", operationId: "adventure_levels_drill_results_create", tags: ["adventure-levels"] },
  adventure_levels_drill_run_destroy: { method: "DELETE", path: "/api/adventure-levels/{level_id}/drill/run/", operationId: "adventure_levels_drill_run_destroy", tags: ["adventure-levels"] },
  adventure_levels_drill_run_update: { method: "PUT", path: "/api/adventure-levels/{level_id}/drill/run/", operationId: "adventure_levels_drill_run_update", tags: ["adventure-levels"] },
  adventure_tier_runs_destroy: { method: "DELETE", path: "/api/adventure-tier-runs/{run_id}/", operationId: "adventure_tier_runs_destroy", tags: ["adventure-tier-runs"] },
  adventure_tier_runs_retrieve: { method: "GET", path: "/api/adventure-tier-runs/{run_id}/", operationId: "adventure_tier_runs_retrieve", tags: ["adventure-tier-runs"] },
  adventure_tier_runs_files_destroy: { method: "DELETE", path: "/api/adventure-tier-runs/{run_id}/files/", operationId: "adventure_tier_runs_files_destroy", tags: ["adventure-tier-runs"] },
  adventure_tier_runs_files_partial_update: { method: "PATCH", path: "/api/adventure-tier-runs/{run_id}/files/", operationId: "adventure_tier_runs_files_partial_update", tags: ["adventure-tier-runs"] },
  adventure_tier_runs_files_create: { method: "POST", path: "/api/adventure-tier-runs/{run_id}/files/", operationId: "adventure_tier_runs_files_create", tags: ["adventure-tier-runs"] },
  adventure_tier_runs_files_update: { method: "PUT", path: "/api/adventure-tier-runs/{run_id}/files/", operationId: "adventure_tier_runs_files_update", tags: ["adventure-tier-runs"] },
  command_introduction_complete: { method: "POST", path: "/api/adventure-tier-runs/{run_id}/introduction/complete/", operationId: "command_introduction_complete", tags: ["adventure-tier-runs"] },
  adventure_tier_runs_retry_create: { method: "POST", path: "/api/adventure-tier-runs/{run_id}/retry/", operationId: "adventure_tier_runs_retry_create", tags: ["adventure-tier-runs"] },
  adventure_tier_runs_submit_command_create: { method: "POST", path: "/api/adventure-tier-runs/{run_id}/submit-command/", operationId: "adventure_tier_runs_submit_command_create", tags: ["adventure-tier-runs"] },
  auth_email_verification_confirm_create: { method: "POST", path: "/api/auth/email-verification/confirm/", operationId: "auth_email_verification_confirm_create", tags: ["auth"] },
  auth_email_verification_resend_create: { method: "POST", path: "/api/auth/email-verification/resend/", operationId: "auth_email_verification_resend_create", tags: ["auth"] },
  auth_login_create: { method: "POST", path: "/api/auth/login/", operationId: "auth_login_create", tags: ["auth"] },
  auth_logout_create: { method: "POST", path: "/api/auth/logout/", operationId: "auth_logout_create", tags: ["auth"] },
  auth_me_retrieve: { method: "GET", path: "/api/auth/me/", operationId: "auth_me_retrieve", tags: ["auth"] },
  auth_oauth_exchange_create: { method: "POST", path: "/api/auth/oauth/exchange/", operationId: "auth_oauth_exchange_create", tags: ["auth"] },
  auth_password_change_create: { method: "POST", path: "/api/auth/password-change/", operationId: "auth_password_change_create", tags: ["auth"] },
  auth_password_reset_confirm_create: { method: "POST", path: "/api/auth/password-reset/confirm/", operationId: "auth_password_reset_confirm_create", tags: ["auth"] },
  auth_password_reset_request_create: { method: "POST", path: "/api/auth/password-reset/request/", operationId: "auth_password_reset_request_create", tags: ["auth"] },
  auth_refresh_create: { method: "POST", path: "/api/auth/refresh/", operationId: "auth_refresh_create", tags: ["auth"] },
  auth_register_create: { method: "POST", path: "/api/auth/register/", operationId: "auth_register_create", tags: ["auth"] },
  auth_sessions_revoke_all_create: { method: "POST", path: "/api/auth/sessions/revoke-all/", operationId: "auth_sessions_revoke_all_create", tags: ["auth"] },
  auth_sessions_revoke_others_create: { method: "POST", path: "/api/auth/sessions/revoke-others/", operationId: "auth_sessions_revoke_others_create", tags: ["auth"] },
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
  chapters_chests_retrieve: { method: "GET", path: "/api/chapters/{chapter_id}/chests/", operationId: "chapters_chests_retrieve", tags: ["chapters"] },
  chapters_chests_create: { method: "POST", path: "/api/chapters/{chapter_id}/chests/", operationId: "chapters_chests_create", tags: ["chapters"] },
  chapters_orientation_list: { method: "GET", path: "/api/chapters/{chapter_id}/orientation/", operationId: "chapters_orientation_list", tags: ["chapters"] },
  chapters_overview_retrieve: { method: "GET", path: "/api/chapters/{chapter_id}/overview/", operationId: "chapters_overview_retrieve", tags: ["chapters"] },
  command_forms_preview_retrieve: { method: "GET", path: "/api/command-forms/{form_id}/preview/", operationId: "command_forms_preview_retrieve", tags: ["command-forms"] },
  health_retrieve: { method: "GET", path: "/api/health/", operationId: "health_retrieve", tags: ["health"] },
  health_live_retrieve: { method: "GET", path: "/api/health/live/", operationId: "health_live_retrieve", tags: ["health"] },
  health_ready_retrieve: { method: "GET", path: "/api/health/ready/", operationId: "health_ready_retrieve", tags: ["health"] },
  orientation_lessons_retrieve: { method: "GET", path: "/api/orientation-lessons/{lesson_id}/", operationId: "orientation_lessons_retrieve", tags: ["orientation-lessons"] },
  orientation_lessons_complete_create: { method: "POST", path: "/api/orientation-lessons/{lesson_id}/complete/", operationId: "orientation_lessons_complete_create", tags: ["orientation-lessons"] },
  player_loadout_companion_create: { method: "POST", path: "/api/player/loadout/companion/", operationId: "player_loadout_companion_create", tags: ["player"] },
  player_preferences_retrieve: { method: "GET", path: "/api/player/preferences/", operationId: "player_preferences_retrieve", tags: ["player"] },
  player_preferences_partial_update: { method: "PATCH", path: "/api/player/preferences/", operationId: "player_preferences_partial_update", tags: ["player"] },
  progress_dashboard_retrieve: { method: "GET", path: "/api/progress/dashboard/", operationId: "progress_dashboard_retrieve", tags: ["progress"] },
  progress_performance_retrieve: { method: "GET", path: "/api/progress/performance/", operationId: "progress_performance_retrieve", tags: ["progress"] },
  progress_stats_retrieve: { method: "GET", path: "/api/progress/stats/", operationId: "progress_stats_retrieve", tags: ["progress"] },
  progress_stats_activity_retrieve: { method: "GET", path: "/api/progress/stats/activity/", operationId: "progress_stats_activity_retrieve", tags: ["progress"] },
  progress_wallet_retrieve: { method: "GET", path: "/api/progress/wallet/", operationId: "progress_wallet_retrieve", tags: ["progress"] },
  schema_retrieve: { method: "GET", path: "/api/schema/", operationId: "schema_retrieve", tags: ["schema"] },
  shop_catalog_retrieve: { method: "GET", path: "/api/shop/catalog/", operationId: "shop_catalog_retrieve", tags: ["shop"] },
  shop_catalog_purchase_create: { method: "POST", path: "/api/shop/catalog/purchase/", operationId: "shop_catalog_purchase_create", tags: ["shop"] },
  skills_learned_retrieve: { method: "GET", path: "/api/skills/learned/", operationId: "skills_learned_retrieve", tags: ["skills"] },
  stories_list: { method: "GET", path: "/api/stories/", operationId: "stories_list", tags: ["stories"] },
  tutor_chat: { method: "POST", path: "/api/tutoring/chat/", operationId: "tutor_chat", tags: ["tutoring"] },
} as const

export type ApiOperationId = keyof typeof apiOperations
export type ApiOperation = (typeof apiOperations)[ApiOperationId]

export type ApiRequestBodyByOperation = {
  admin_analytics_retrieve: null
  admin_chapters_retrieve: null
  admin_chapters_create: ApiSchemas["AdminChapterCreateRequest"]
  admin_chapters_partial_update: ApiSchemas["PatchedAdminChapterUpdateRequest"]
  admin_economy_adjust_create: ApiSchemas["AdminEconomyAdjustRequest"]
  admin_economy_transactions_retrieve: null
  admin_overview_retrieve: null
  admin_settings_retrieve: null
  admin_settings_create: ApiSchemas["AdminFeatureFlagUpdateRequest"]
  admin_stories_retrieve: null
  admin_stories_create: ApiSchemas["AdminStoryCreateRequest"]
  admin_stories_partial_update: ApiSchemas["PatchedAdminStoryUpdateRequest"]
  admin_users_retrieve: null
  admin_users_retrieve_2: null
  admin_users_actions_create: ApiSchemas["AdminUserActionRequest"]
  admin_users_kpis_retrieve: null
  adventure_level_tiers_runs_create: ApiSchemas["AdventureLevelTierRunStart"]
  adventure_levels_drill_retrieve: null
  adventure_levels_drill_results_create: ApiSchemas["DrillReport"]
  adventure_levels_drill_run_destroy: null
  adventure_levels_drill_run_update: ApiSchemas["DrillRunState"]
  adventure_tier_runs_destroy: null
  adventure_tier_runs_retrieve: null
  adventure_tier_runs_files_destroy: null
  adventure_tier_runs_files_partial_update: ApiSchemas["WorkspaceFile"]
  adventure_tier_runs_files_create: ApiSchemas["WorkspaceFile"]
  adventure_tier_runs_files_update: ApiSchemas["WorkspaceFileRename"]
  command_introduction_complete: ApiSchemas["IntroductionComplete"]
  adventure_tier_runs_retry_create: null
  adventure_tier_runs_submit_command_create: ApiSchemas["CommandSubmit"]
  auth_email_verification_confirm_create: ApiSchemas["EmailVerificationConfirm"]
  auth_email_verification_resend_create: ApiSchemas["EmailVerificationResend"]
  auth_login_create: ApiSchemas["Login"]
  auth_logout_create: null
  auth_me_retrieve: null
  auth_oauth_exchange_create: ApiSchemas["OAuthTicketExchange"]
  auth_password_change_create: ApiSchemas["PasswordChange"]
  auth_password_reset_confirm_create: ApiSchemas["PasswordResetConfirm"]
  auth_password_reset_request_create: ApiSchemas["PasswordResetRequest"]
  auth_refresh_create: null
  auth_register_create: ApiSchemas["Register"]
  auth_sessions_revoke_all_create: null
  auth_sessions_revoke_others_create: null
  challenge_runs_destroy: null
  challenge_runs_retrieve: null
  challenge_runs_files_destroy: null
  challenge_runs_files_partial_update: ApiSchemas["WorkspaceFile"]
  challenge_runs_files_create: ApiSchemas["WorkspaceFile"]
  challenge_runs_files_update: ApiSchemas["WorkspaceFileRename"]
  challenge_runs_retry_create: null
  challenge_runs_submit_command_create: ApiSchemas["CommandSubmit"]
  challenge_trials_runs_create: ApiSchemas["ChallengeRunStart"]
  chapters_list: null
  chapters_book_retrieve: null
  chapters_chests_retrieve: null
  chapters_chests_create: ApiSchemas["ChapterChestOpen"]
  chapters_orientation_list: null
  chapters_overview_retrieve: null
  command_forms_preview_retrieve: null
  health_retrieve: null
  health_live_retrieve: null
  health_ready_retrieve: null
  orientation_lessons_retrieve: null
  orientation_lessons_complete_create: ApiSchemas["ChapterOrientationComplete"]
  player_loadout_companion_create: ApiSchemas["ShopMutationRequest"]
  player_preferences_retrieve: null
  player_preferences_partial_update: ApiSchemas["PatchedPlayerPreferences"]
  progress_dashboard_retrieve: null
  progress_performance_retrieve: null
  progress_stats_retrieve: null
  progress_stats_activity_retrieve: null
  progress_wallet_retrieve: null
  schema_retrieve: null
  shop_catalog_retrieve: null
  shop_catalog_purchase_create: ApiSchemas["ShopMutationRequest"]
  skills_learned_retrieve: null
  stories_list: null
  tutor_chat: ApiSchemas["TutorChatRequest"]
}

export type ApiResponseBodyByOperation = {
  admin_analytics_retrieve: ApiSchemas["AdminAnalyticsResponse"]
  admin_chapters_retrieve: ApiSchemas["AdminChapterListResponse"]
  admin_chapters_create: ApiSchemas["AdminChapter"]
  admin_chapters_partial_update: ApiSchemas["AdminChapter"]
  admin_economy_adjust_create: ApiSchemas["AdminEconomyAdjustResponse"]
  admin_economy_transactions_retrieve: ApiSchemas["AdminTransactionListResponse"]
  admin_overview_retrieve: ApiSchemas["AdminOverviewResponse"]
  admin_settings_retrieve: ApiSchemas["AdminSettingsResponse"]
  admin_settings_create: ApiSchemas["AdminFeatureFlag"]
  admin_stories_retrieve: ApiSchemas["AdminStoryListResponse"]
  admin_stories_create: ApiSchemas["AdminStory"]
  admin_stories_partial_update: ApiSchemas["AdminStory"]
  admin_users_retrieve: ApiSchemas["AdminUserListResponse"]
  admin_users_retrieve_2: ApiSchemas["AdminUserDetail"]
  admin_users_actions_create: ApiSchemas["AdminUserDetail"]
  admin_users_kpis_retrieve: ApiSchemas["AdminUserKpisResponse"]
  adventure_level_tiers_runs_create: ApiSchemas["AdventureLevelTierRunResponse"]
  adventure_levels_drill_retrieve: ApiSchemas["LevelDrillPlanResponse"]
  adventure_levels_drill_results_create: ApiSchemas["DrillReportResponse"]
  adventure_levels_drill_run_destroy: ApiSchemas["DrillRunStateResponse"]
  adventure_levels_drill_run_update: ApiSchemas["DrillRunStateResponse"]
  adventure_tier_runs_destroy: null
  adventure_tier_runs_retrieve: ApiSchemas["AdventureLevelTierRunResponse"]
  adventure_tier_runs_files_destroy: ApiSchemas["AdventureLevelTierRunResponse"]
  adventure_tier_runs_files_partial_update: ApiSchemas["AdventureLevelTierRunResponse"]
  adventure_tier_runs_files_create: ApiSchemas["AdventureLevelTierRunResponse"]
  adventure_tier_runs_files_update: ApiSchemas["AdventureLevelTierRunResponse"]
  command_introduction_complete: ApiSchemas["IntroductionCompleteResponse"]
  adventure_tier_runs_retry_create: ApiSchemas["AdventureLevelTierRunResponse"]
  adventure_tier_runs_submit_command_create: ApiSchemas["AdventureLevelTierCommandResponse"]
  auth_email_verification_confirm_create: ApiSchemas["SessionResponse"]
  auth_email_verification_resend_create: ApiSchemas["DetailResponse"]
  auth_login_create: ApiSchemas["SessionResponse"]
  auth_logout_create: null
  auth_me_retrieve: ApiSchemas["User"]
  auth_oauth_exchange_create: ApiSchemas["SessionResponse"]
  auth_password_change_create: ApiSchemas["SessionResponse"]
  auth_password_reset_confirm_create: ApiSchemas["DetailResponse"]
  auth_password_reset_request_create: ApiSchemas["DetailResponse"]
  auth_refresh_create: ApiSchemas["AccessTokenResponse"]
  auth_register_create: ApiSchemas["RegisterResponse"]
  auth_sessions_revoke_all_create: null
  auth_sessions_revoke_others_create: ApiSchemas["DetailResponse"]
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
  chapters_chests_retrieve: ApiSchemas["ChapterChestRewards"]
  chapters_chests_create: ApiSchemas["ChapterChestRewards"]
  chapters_orientation_list: Array<ApiSchemas["ChapterOrientationLessonList"]>
  chapters_overview_retrieve: { [key: string]: JsonValue }
  command_forms_preview_retrieve: ApiSchemas["CommandFormPreviewResponse"]
  health_retrieve: { [key: string]: JsonValue }
  health_live_retrieve: { [key: string]: JsonValue }
  health_ready_retrieve: { [key: string]: JsonValue }
  orientation_lessons_retrieve: ApiSchemas["ChapterOrientationLessonDetail"]
  orientation_lessons_complete_create: ApiSchemas["ChapterOrientationLessonDetail"]
  player_loadout_companion_create: ApiSchemas["ShopEquipResponse"]
  player_preferences_retrieve: ApiSchemas["PlayerPreferences"]
  player_preferences_partial_update: ApiSchemas["PlayerPreferences"]
  progress_dashboard_retrieve: ApiSchemas["DashboardSummaryResponse"]
  progress_performance_retrieve: ApiSchemas["PerformanceSummaryResponse"]
  progress_stats_retrieve: ApiSchemas["StatsSummaryResponse"]
  progress_stats_activity_retrieve: ApiSchemas["StatsActivityResponse"]
  progress_wallet_retrieve: ApiSchemas["WalletSummaryResponse"]
  schema_retrieve: { [key: string]: JsonValue }
  shop_catalog_retrieve: ApiSchemas["ShopResponse"]
  shop_catalog_purchase_create: ApiSchemas["ShopPurchaseResponse"]
  skills_learned_retrieve: ApiSchemas["LearnedSkillsResponse"]
  stories_list: Array<ApiSchemas["Story"]>
  tutor_chat: ApiSchemas["TutorChatResponse"]
}

export type ApiRequestBody<TOperation extends ApiOperationId> = ApiRequestBodyByOperation[TOperation]
export type ApiResponseBody<TOperation extends ApiOperationId> = ApiResponseBodyByOperation[TOperation]
