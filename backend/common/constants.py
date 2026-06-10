DIFFICULTY_EASY = "easy"
DIFFICULTY_MEDIUM = "medium"
DIFFICULTY_HARD = "hard"
DIFFICULTIES = (DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD)

DIFFICULTY_MAX_COUNTED_COMMANDS = {
    DIFFICULTY_EASY: 12,
    DIFFICULTY_MEDIUM: 10,
    DIFFICULTY_HARD: 8,
}

SESSION_MODE_PRIMARY = "primary"
SESSION_MODE_REVIEW = "review"
# Adventure free-play: a playable but uncounted re-run of an already-passed
# adventure. Never touches mastery, progress, or KPIs (mirrors review for
# challenges, but player-facing it is "Play again", never "Review").
SESSION_MODE_REPLAY = "replay"

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
SOURCE_REVIEW = "review"

COMMAND_ACCURACY_PROGRESS_THRESHOLD = 70
COMMAND_ACCURACY_MASTERY_THRESHOLD = 100
