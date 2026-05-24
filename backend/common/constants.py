DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"
DIFFICULTIES = (DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD)

SESSION_MODE_PRIMARY = "primary"
SESSION_MODE_REVIEW = "review"

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

COMPLETION_STATE_BASED = "state_based"
# State-based scenarios may use detailed target rules, but they still evaluate
# through the normal state-based evaluator.
COMPLETION_EXPANDED_STATE_BASED = "expanded_state_based"
COMPLETION_TYPES = (
    COMPLETION_STATE_BASED,
    COMPLETION_EXPANDED_STATE_BASED,
)

SOURCE_LESSON = "lesson"
SOURCE_UNIT_CARD = "unit_card"
SOURCE_RETRY = "retry"
SOURCE_REVIEW = "review"
