DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"
DIFFICULTIES = (DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD)

DIFFICULTY_MAX_COUNTED_COMMANDS = {
    DIFFICULTY_EASY: 12,
    DIFFICULTY_MEDIUM: 10,
    DIFFICULTY_HARD: 8,
}

# GitCoins granted once when an account is created - exactly the price of one
# starter companion (150), so a new player's first purchase is a real, single
# choice rather than a shopping spree. Awarded idempotently via WalletService
# (key ``signup:<player_id>``).
PLAN_SIGNUP_GRANT = 150

SESSION_STATUS_STARTED = "started"
SESSION_STATUS_COMPLETED = "completed"
SESSION_STATUS_FAILED = "failed"
SESSION_STATUS_ABANDONED = "abandoned"

RESULT_TARGET_MATCHED = "TargetMatched"
RESULT_TARGET_NOT_YET_MATCHED = "TargetNotYetMatched"
RESULT_UNPROCESSABLE = "Unprocessable"
RESULT_INVALID = "Invalid"

COMMAND_COUNTED = "counted_action"
COMMAND_DIAGNOSTIC = "non_counted_diagnostic"
COMMAND_UNPROCESSABLE = "unprocessable"

SOURCE_RETRY = "retry"
