from __future__ import annotations

from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from learning.models import Lesson, OrientationLessonSession
from simulator.command_engine import GitCommandExecutor

def _step_by_id(lesson: Lesson, step_id: str) -> dict | None:
    for step in lesson.interaction_steps or []:
        if step.get("id") == step_id:
            return step
    return None


def _command_matches(step: dict, normalized: str) -> bool:
    normalized = normalized.lower().strip()
    for prefix in step.get("accept_prefixes") or []:
        if normalized.startswith(prefix.lower().strip()):
            return True
    for exact in step.get("accept_exact") or []:
        if normalized == exact.lower().strip():
            return True
    return False


class OrientationSessionService:
    def __init__(self) -> None:
        self.executor = GitCommandExecutor()

    def get_or_create_session(self, *, user, lesson: Lesson) -> OrientationLessonSession:
        if not lesson.unit.is_orientation:
            raise ValidationError("Lesson is not an orientation lesson.")
        existing = (
            OrientationLessonSession.objects.filter(user=user, lesson=lesson)
            .order_by("-updated_at")
            .first()
        )
        if existing:
            return existing
        initial_state = {}
        for step in lesson.interaction_steps or []:
            if step.get("kind") == "git_command" and step.get("initial_state"):
                initial_state = step["initial_state"]
                break
        return OrientationLessonSession.objects.create(
            user=user,
            lesson=lesson,
            repository_state=initial_state,
        )

    def session_payload(self, session: OrientationLessonSession) -> dict:
        return {
            "id": session.id,
            "lesson_id": session.lesson_id,
            "repository_state": session.repository_state,
            "command_log": session.command_log,
        }

    @transaction.atomic
    def submit_command(
        self,
        *,
        user,
        session: OrientationLessonSession,
        command: str,
        step_id: str,
    ) -> dict:
        if session.user_id != user.id:
            raise NotFound()
        lesson = session.lesson
        step = _step_by_id(lesson, step_id)
        if not step or step.get("kind") != "git_command":
            raise ValidationError("Invalid orientation step for command submission.")

        result = self.executor.execute(session.repository_state, command)
        normalized = result.normalized_command
        accepted = _command_matches(step, normalized)
        if accepted and step.get("require_processed", True):
            accepted = result.processed
        if accepted and not result.processed and step.get("success_output"):
            result_output = step["success_output"]
            result_stderr = ""
            result_exit_code = 0
        else:
            result_output = result.stdout or result.output
            result_stderr = result.stderr
            result_exit_code = result.exit_code or 0
        log_entry = {
            "command": command,
            "normalized_command": normalized,
            "stdout": result_output,
            "stderr": result_stderr,
            "exit_code": result_exit_code,
            "processed": result.processed,
            "accepted": accepted,
        }
        session.repository_state = result.state
        session.command_log = [*session.command_log, log_entry]
        session.save(update_fields=["repository_state", "command_log", "updated_at"])

        hint = None if accepted else step.get("hint") or "Re-read the step goal and try a diagnostic or action command."
        return {
            "accepted": accepted,
            "hint": hint,
            "session": self.session_payload(session),
            "output": result_output,
            "stderr": result_stderr,
            "exit_code": result_exit_code,
            "normalized_command": normalized,
        }

    @transaction.atomic
    def reset_for_step(self, *, user, session: OrientationLessonSession, step_id: str) -> OrientationLessonSession:
        if session.user_id != user.id:
            raise NotFound()
        lesson = session.lesson
        step = _step_by_id(lesson, step_id)
        if not step:
            raise ValidationError("Unknown orientation step.")
        initial_state = step.get("initial_state")
        if initial_state is not None:
            session.repository_state = initial_state
            session.save(update_fields=["repository_state", "updated_at"])
        return session
