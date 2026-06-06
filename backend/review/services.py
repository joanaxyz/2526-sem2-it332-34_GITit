from common.constants import SESSION_MODE_REVIEW
from common.exceptions import Locked
from scenarios.models import CommandDrill, CompletionRecord
from scenarios.services import PracticeSessionService


class ReviewModeService:
    def start_review_session(self, *, user, problem):
        filters = {"user": user}
        if isinstance(problem, CommandDrill):
            filters["command_drill"] = problem
        else:
            filters["workflow_level"] = problem
        if not CompletionRecord.objects.filter(**filters).exists():
            raise Locked("Review Mode is available only after completing this practice item.")
        return PracticeSessionService().start_session(
            user=user,
            problem=problem,
            source_entry_point="review",
            mode=SESSION_MODE_REVIEW,
        )
