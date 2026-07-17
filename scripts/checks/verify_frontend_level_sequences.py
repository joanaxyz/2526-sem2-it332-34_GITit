"""Generate the all-level cheat sheet and verify sequences through the live UI.

The browser portion only drives the rendered frontend with ``agent-browser``.
Database reads identify the exact variant selected by the backend so the command
submitted to the terminal is deterministic. Database writes are limited to the
named disposable QA player: story entitlements, prerequisite mastery, and
challenge completions are added only to cross progression gates that are outside
this adventure-level regression scope.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
DEFAULT_CHEAT_SHEET = ROOT / "LEVEL_CHEAT_SHEET.md"
DEFAULT_OUTPUT = ROOT / "dogfood-output"
BROWSER_BIN = (
    Path(os.environ.get("APPDATA", ""))
    / "npm"
    / "node_modules"
    / "agent-browser"
    / "bin"
    / "agent-browser-win32-x64.exe"
)

os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from django.utils import timezone  # noqa: E402
from django.db import OperationalError, connection  # noqa: E402

from adventures.models import AdventureLevel, AdventureRun, SkillMastery  # noqa: E402
from adventures.services.selectors import form_solve_targets  # noqa: E402
from challenges.models import ChallengeLevel  # noqa: E402
from curriculum.models import Chapter, Story  # noqa: E402
from players.models import Player  # noqa: E402
from progress.models import (  # noqa: E402
    AdventureLevelCompletion,
    ChallengeLevelCompletion,
    ChallengeTrialCompletion,
)
from practice.models import CommandStep  # noqa: E402
from shop.models import Entitlement  # noqa: E402


STORY_ORDER = ("arcane-spire", "frostbound-citadel", "neon-backstreets")
RUN_URL_RE = re.compile(r"/adventure-runs/(\d+)(?:$|[/?#])")
# Local SQLite and the rendered UI can briefly lag while the full matrix is
# writing progress and refreshing several dashboard queries at once. A short
# observation window misclassified a successfully stored frontend submission
# as missing, so allow the same headroom used by the browser operations.
LOCAL_UI_UPDATE_TIMEOUT = 12


def workspace_path(value: str | Path) -> Path:
    """Resolve CLI artifact paths against the repository, not Django's cwd."""

    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def published_levels() -> list[AdventureLevel]:
    return list(
        AdventureLevel.objects.filter(
            is_published=True,
            chapter__is_published=True,
            chapter__story__is_published=True,
        )
        .select_related("chapter", "chapter__story")
        .prefetch_related("waves__variants")
        .order_by(
            "chapter__story__sort_order",
            "chapter__sort_order",
            "chapter__number",
            "sort_order",
            "id",
        )
    )


def md_code(command: str) -> str:
    command = command.replace("|", "\\|")
    fence = "``" if "`" in command else "`"
    return f"{fence}{command}{fence}"


def format_sequence(
    commands: Iterable[str],
    workspace_files: Iterable[dict] = (),
) -> str:
    commands = list(commands)
    actions_by_index: dict[int, list[dict]] = defaultdict(list)
    for action in workspace_files:
        actions_by_index[int(action.get("after_command_index", 0))].append(action)

    values: list[str] = []

    def append_workspace_actions(index: int) -> None:
        for action in actions_by_index.get(index, []):
            path = str(action.get("path") or "")
            content = json.dumps(str(action.get("content") or ""), ensure_ascii=False)
            values.append(
                f"**Project Files:** edit {md_code(path)}, set content to "
                f"{md_code(content)}, and click **Save**"
            )

    append_workspace_actions(0)
    for index, command in enumerate(commands, start=1):
        values.append(md_code(command))
        append_workspace_actions(index)

    if not values:
        return "_No terminal command_"
    return " → ".join(values)


def generate_cheat_sheet(path: Path) -> dict[str, int]:
    levels = published_levels()
    by_story: dict[str, list[AdventureLevel]] = defaultdict(list)
    for level in levels:
        by_story[level.chapter.story.slug].append(level)

    wave_total = sum(level.waves.filter(is_published=True).count() for level in levels)
    variant_total = sum(
        wave.variants.filter(is_published=True).count()
        for level in levels
        for wave in level.waves.filter(is_published=True)
    )
    lines = [
        "# GIT it! — All-level command cheat sheet",
        "",
        (
            f"Generated from the live seeded curriculum on {datetime.now().date().isoformat()}. "
            f"Covers **{len(levels)} levels**, **{wave_total} waves**, and "
            f"**{variant_total} authored variants** across all three stories."
        ),
        "",
        "Use the sequence for the variant whose story details, file names, branch names, "
        "commit IDs, or URLs match the level shown in the frontend. Commands on one row "
        "must be submitted left-to-right.",
        "",
        "## Quick totals",
        "",
        "| Story | Levels | Waves |",
        "|---|---:|---:|",
    ]
    for story_slug in STORY_ORDER:
        story = Story.objects.get(slug=story_slug)
        story_levels = by_story[story_slug]
        story_waves = sum(level.waves.filter(is_published=True).count() for level in story_levels)
        lines.append(f"| {story.title} | {len(story_levels)} | {story_waves} |")

    for story_slug in STORY_ORDER:
        story = Story.objects.get(slug=story_slug)
        story_levels = by_story[story_slug]
        lines.extend(["", f"## {story.title}", ""])
        chapters = list(
            Chapter.objects.filter(story=story, is_published=True).order_by("sort_order", "number", "id")
        )
        for chapter in chapters:
            chapter_levels = [level for level in story_levels if level.chapter_id == chapter.id]
            lines.extend([f"### Chapter {chapter.number:02d}: {chapter.title}", ""])
            for level_index, level in enumerate(chapter_levels, start=1):
                lines.extend(
                    [
                        f"#### Level {level_index}: {level.title}",
                        "",
                        "| Wave | Variant | Command sequence |",
                        "|---:|---|---|",
                    ]
                )
                waves = level.waves.filter(is_published=True).order_by("sort_order", "id")
                for wave_index, wave in enumerate(waves, start=1):
                    grouped: dict[tuple[tuple[str, ...], str], list[str]] = defaultdict(list)
                    variants = wave.variants.filter(is_published=True).order_by("id")
                    for variant in variants:
                        workspace_files = list(
                            (variant.parameter_context or {}).get("solution_workspace_files") or []
                        )
                        key = (
                            tuple(variant.solution_commands or []),
                            json.dumps(workspace_files, ensure_ascii=False, sort_keys=True),
                        )
                        grouped[key].append(
                            variant.label or variant.case_id or variant.slug
                        )
                    for sequence_index, ((commands, workspace_json), labels) in enumerate(grouped.items()):
                        wave_cell = f"{wave_index}. {wave.title}" if sequence_index == 0 else ""
                        variant_cell = "All variants" if len(grouped) == 1 else " / ".join(labels)
                        lines.append(
                            f"| {wave_cell} | {variant_cell.replace('|', '\\|')} | "
                            f"{format_sequence(commands, json.loads(workspace_json))} |"
                        )
                lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"levels": len(levels), "waves": wave_total, "variants": variant_total}


@dataclass
class BrowserResult:
    returncode: int
    output: str


class Browser:
    def __init__(self, session: str) -> None:
        self.session = session

    def run(self, *args: str, timeout: int = 30, attempts: int = 2) -> BrowserResult:
        command = [str(BROWSER_BIN), "--session", self.session, *args]
        last_output = ""
        for attempt in range(attempts):
            try:
                completed = subprocess.run(
                    command,
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else exc.stdout
                stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else exc.stderr
                last_output = "\n".join(value for value in (stdout, stderr) if value)
                if attempt + 1 < attempts:
                    time.sleep(0.5)
                    continue
                return BrowserResult(124, last_output or f"Timed out: {' '.join(command)}")
            output = "\n".join(value for value in (completed.stdout, completed.stderr) if value).strip()
            if completed.returncode == 0:
                return BrowserResult(0, output)
            last_output = output
            if attempt + 1 < attempts:
                time.sleep(0.5)
        return BrowserResult(completed.returncode, last_output)

    def require(self, *args: str, timeout: int = 30, attempts: int = 2) -> str:
        result = self.run(*args, timeout=timeout, attempts=attempts)
        if result.returncode != 0:
            raise RuntimeError(f"Browser command failed ({' '.join(args)}): {result.output}")
        return result.output

    def url(self) -> str:
        return self.require("get", "url", timeout=10).strip()

    def open(self, url: str) -> None:
        self.require("open", url, timeout=20)

    def pushstate(self, url: str) -> None:
        self.require("pushstate", url, timeout=20)

    def click_button(self, name: str) -> None:
        self.require("find", "role", "button", "click", "--name", name, timeout=15)

    def scroll_aria_label_into_view(self, name: str) -> bool:
        quoted = json.dumps(name)
        expression = (
            "(() => { const el = Array.from(document.querySelectorAll('button'))"
            f".find((node) => node.getAttribute('aria-label') === {quoted}); "
            "if (!el) return false; el.scrollIntoView({block: 'center', inline: 'center'}); return true; })()"
        )
        result = self.run("eval", expression, timeout=10, attempts=1)
        return result.returncode == 0 and "true" in result.output.lower()

    def fill_terminal(self, command: str) -> None:
        last = ""
        for _ in range(30):
            result = self.run("fill", "[data-command-input=true]", command, timeout=8, attempts=1)
            if result.returncode == 0:
                return
            last = result.output
            time.sleep(0.4)
        raise RuntimeError(f"Terminal input did not become ready: {last}")

    def submit_terminal(self, command: str) -> None:
        self.fill_terminal(command)
        self.require("press", "Enter", timeout=10)

    def wait_for_terminal_settle(self) -> None:
        """Wait for the rendered mutation cycle before submitting again."""

        self.require(
            "wait",
            "--fn",
            (
                "(() => { const input = document.querySelector('[data-command-input=true]'); "
                "return Boolean(input && !input.disabled && input.value === ''); })()"
            ),
            timeout=15,
            attempts=1,
        )
        # React Query can make the input available in the same paint that swaps
        # the optimistic run state for the server response. Give event handlers
        # one more frame before driving the next command in a long sequence.
        time.sleep(0.2)

    def write_workspace_file(self, path: str, content: str) -> None:
        self.require(
            "find",
            "role",
            "button",
            "click",
            "--name",
            f"Open {path}",
            timeout=15,
        )
        self.require("fill", 'textarea[aria-label="File content"]', content, timeout=15)
        self.require(
            "find",
            "role",
            "button",
            "click",
            "--name",
            "Save",
            timeout=15,
        )
        self.require(
            "wait",
            "--fn",
            (
                "(() => { const dialog = document.querySelector("
                "'[aria-label=\"Workspace file editor\"]'); "
                "const save = Array.from(dialog?.querySelectorAll('button') ?? [])"
                ".find((button) => button.textContent?.trim() === 'Save'); "
                "return Boolean(save?.disabled); })()"
            ),
            timeout=15,
            attempts=1,
        )
        self.require(
            "find",
            "role",
            "button",
            "click",
            "--name",
            "Close editor",
            timeout=15,
        )

    def screenshot(self, path: Path, *, annotate: bool = False) -> None:
        args = ["screenshot"]
        if annotate:
            args.append("--annotate")
        args.append(str(path))
        self.run(*args, timeout=20, attempts=1)


def parse_run_id(url: str) -> int | None:
    match = RUN_URL_RE.search(url)
    return int(match.group(1)) if match else None


def wait_for_run_update(run_id: int, *, previous_wave_id: int, previous_count: int) -> AdventureRun:
    deadline = time.monotonic() + LOCAL_UI_UPDATE_TIMEOUT
    while time.monotonic() < deadline:
        run = AdventureRun.objects.select_related("current_wave", "selected_variant", "level").get(pk=run_id)
        if run.status != "started":
            return run
        if run.current_wave_id != previous_wave_id or run.command_count > previous_count:
            return run
        time.sleep(0.2)
    return AdventureRun.objects.select_related("current_wave", "selected_variant", "level").get(pk=run_id)


def wait_for_command_step(run_id: int, *, previous_step_id: int) -> CommandStep:
    deadline = time.monotonic() + LOCAL_UI_UPDATE_TIMEOUT
    while time.monotonic() < deadline:
        step = (
            CommandStep.objects.filter(attempt_id=run_id, id__gt=previous_step_id)
            .order_by("id")
            .first()
        )
        if step is not None:
            return step
        time.sleep(0.2)
    raise RuntimeError("Terminal submission did not create a command-step record.")


def wait_for_workspace_update(
    run_id: int,
    *,
    wave_id: int,
    path: str,
    content: str,
) -> AdventureRun:
    deadline = time.monotonic() + LOCAL_UI_UPDATE_TIMEOUT
    while time.monotonic() < deadline:
        run = AdventureRun.objects.select_related("current_wave", "selected_variant", "level").get(
            pk=run_id
        )
        if run.status != "started" or run.current_wave_id != wave_id:
            return run
        entry = (run.repository_state.get("working_tree") or {}).get(path)
        actual = entry.get("content") if isinstance(entry, dict) else entry
        if actual == content:
            return run
        time.sleep(0.2)
    raise RuntimeError(f"Saving {path!r} through Project Files did not update the run worktree.")


def current_player(username: str) -> Player:
    return Player.objects.select_related("user").get(user__username=username)


def grant_story_entitlement(player: Player, story_slug: str) -> None:
    story = Story.objects.get(slug=story_slug)
    if story.price <= 0:
        return
    Entitlement.objects.get_or_create(player=player, kind="story", slug=story_slug)


def grant_prerequisite_story_mastery(player: Player, story: Story) -> int:
    """Cross a story gate without rewriting any frontend-sequence result.

    The real story gate is command-form mastery, so zero-star QA bypass rows for
    confirmed failures are intentionally insufficient. This grants mastery only
    to the disposable player after the prerequisite story matrix has run.
    """
    prerequisite = story.prerequisite_story
    if prerequisite is None:
        return 0
    form_ids = set(
        AdventureLevel.objects.filter(
            chapter__story=prerequisite,
            chapter__is_published=True,
            is_published=True,
            is_required=True,
            command_forms__is_published=True,
            command_forms__is_playable=True,
        ).values_list("command_forms", flat=True)
    )
    form_ids.discard(None)
    targets = form_solve_targets(form_ids)
    for form_id in form_ids:
        row, created = SkillMastery.objects.get_or_create(
            player=player,
            command_form_id=form_id,
            defaults={
                "learned_at": timezone.now(),
                "solves": targets.get(form_id, 1),
                "mastered": True,
            },
        )
        if created:
            continue
        updates: list[str] = []
        target = targets.get(form_id, 1)
        if row.learned_at is None:
            row.learned_at = timezone.now()
            updates.append("learned_at")
        if row.solves < target:
            row.solves = target
            updates.append("solves")
        if not row.mastered:
            row.mastered = True
            updates.append("mastered")
        if updates:
            row.save(update_fields=[*updates, "updated_at"])
    return len(form_ids)


def grant_chapter_trial_gate(player: Player, chapter: Chapter) -> tuple[int, int]:
    trial_count = 0
    level_count = 0
    levels = ChallengeLevel.objects.filter(chapter=chapter, is_published=True).prefetch_related("trials")
    for challenge_level in levels:
        for trial in challenge_level.trials.filter(is_published=True):
            ChallengeTrialCompletion.objects.get_or_create(
                player=player,
                challenge_trial=trial,
                defaults={
                    "completed_at": timezone.now(),
                    "stars": 3,
                    "counted_action_total": 0,
                    "challenge_run": None,
                },
            )
            trial_count += 1
        ChallengeLevelCompletion.objects.get_or_create(
            player=player,
            challenge_level=challenge_level,
            defaults={"completed_at": timezone.now()},
        )
        level_count += 1
    return level_count, trial_count


def bypass_failed_level(player: Player, level: AdventureLevel, run: AdventureRun | None) -> None:
    for attempt in range(6):
        try:
            AdventureLevelCompletion.objects.get_or_create(
                player=player,
                adventure_level=level,
                defaults={
                    "completed_at": timezone.now(),
                    "stars": 0,
                    "counted_action_total": 0,
                    "adventure_run": run if run and run.status == "completed" else None,
                },
            )
            return
        except OperationalError as exc:
            if "locked" not in str(exc).lower() or attempt == 5:
                raise
            connection.close()
            time.sleep(0.5 * (attempt + 1))


def start_level(
    browser: Browser,
    *,
    player: Player,
    story_slug: str,
    level_index: int,
    level: AdventureLevel,
) -> AdventureRun:
    # A confirmed failure is bypassed in the disposable QA database so later
    # levels can be exercised. Reload the map here so React Query sees that
    # progression change before the next level action is resolved.
    browser.open(f"http://localhost:5173/stories/{story_slug}?chapter={level.chapter_id}")
    time.sleep(0.5)
    level_name = f"Level {level_index}: {level.title}. Open play action."
    level_error = ""
    for _ in range(30):
        if not browser.scroll_aria_label_into_view(level_name):
            time.sleep(0.3)
            continue
        result = browser.run(
            "find",
            "role",
            "button",
            "click",
            "--name",
            level_name,
            timeout=8,
            attempts=1,
        )
        if result.returncode == 0:
            break
        level_error = result.output
        time.sleep(0.3)
    else:
        raise RuntimeError(f"Level action did not render for {level.title!r}: {level_error}")
    play_error = ""
    for _ in range(20):
        result = browser.run(
            "find",
            "role",
            "button",
            "click",
            "--name",
            f"Play {level.title}",
            timeout=8,
            attempts=1,
        )
        if result.returncode == 0:
            break
        play_error = result.output
        time.sleep(0.3)
    else:
        raise RuntimeError(f"Play action did not render for {level.title!r}: {play_error}")

    deadline = time.monotonic() + 20
    run_id = None
    while time.monotonic() < deadline:
        run_id = parse_run_id(browser.url())
        if run_id is not None:
            break
        time.sleep(0.3)
    if run_id is None:
        raise RuntimeError(f"Starting {level.title!r} did not navigate to an adventure run.")
    run = AdventureRun.objects.select_related("current_wave", "selected_variant", "level").get(
        pk=run_id,
        player=player,
    )
    if run.level_id != level.id:
        raise RuntimeError(
            f"Expected level {level.slug!r}, but frontend started {run.level.slug!r} (run {run.id})."
        )
    return run


def active_run_for(browser: Browser, player: Player, level: AdventureLevel) -> AdventureRun | None:
    run_id = parse_run_id(browser.url())
    run = None
    if run_id is not None:
        run = (
            AdventureRun.objects.select_related("current_wave", "selected_variant", "level")
            .filter(pk=run_id, player=player, level=level, status="started")
            .first()
        )
    if run is None:
        run = (
            AdventureRun.objects.select_related("current_wave", "selected_variant", "level")
            .filter(player=player, level=level, status="started")
            .order_by("-id")
            .first()
        )
        if run is None:
            return None
        browser.open(f"http://localhost:5173/adventure-runs/{run.id}")
        time.sleep(0.5)
    return run


def exercise_run(browser: Browser, run: AdventureRun) -> tuple[bool, str, AdventureRun]:
    run_id = run.id
    while run.status == "started":
        if run.current_wave_id is None or run.selected_variant_id is None:
            return False, "Run has no current wave or selected variant.", run

        wave_id = run.current_wave_id
        variant = run.selected_variant
        commands = list(variant.solution_commands or [])
        workspace_actions: dict[int, list[dict]] = defaultdict(list)
        for action in (variant.parameter_context or {}).get("solution_workspace_files") or []:
            workspace_actions[int(action.get("after_command_index", 0))].append(action)
        start_at = min(run.command_count, len(commands))
        if not commands:
            return False, f"Variant {variant.case_id} has no solution commands.", run

        # Reapply the edit at the current sequence boundary. This covers actions
        # before the first command and safely resumes a run that stopped after a
        # terminal submission but before its Project Files save completed.
        for action in workspace_actions.get(start_at, []):
            path = str(action.get("path") or "")
            content = str(action.get("content") or "")
            browser.write_workspace_file(path, content)
            run = wait_for_workspace_update(
                run_id,
                wave_id=wave_id,
                path=path,
                content=content,
            )

        for command_index, command in enumerate(commands, start=1):
            if command_index <= start_at:
                continue
            before_count = run.command_count
            previous_step_id = (
                CommandStep.objects.filter(attempt_id=run_id)
                .order_by("-id")
                .values_list("id", flat=True)
                .first()
                or 0
            )
            browser.submit_terminal(command)
            run = wait_for_run_update(
                run_id,
                previous_wave_id=wave_id,
                previous_count=before_count,
            )
            step = wait_for_command_step(
                run_id,
                previous_step_id=previous_step_id,
            )
            if step.command_text != command:
                return (
                    False,
                    f"Frontend submitted {step.command_text!r}; expected {command!r}.",
                    run,
                )
            if not step.was_processable:
                output = (step.terminal_output or "").strip().replace("\n", " ")
                return (
                    False,
                    f"Command {command!r} was unprocessable in the visible terminal: {output}",
                    run,
                )
            transitioned = run.status != "started" or run.current_wave_id != wave_id
            if transitioned:
                if command_index < len(commands):
                    omitted = commands[command_index:]
                    return (
                        False,
                        f"Wave advanced after a strict prefix; omitted authored commands: {omitted!r}.",
                        run,
                    )
                if workspace_actions.get(command_index):
                    return (
                        False,
                        "Wave advanced before its final authored Project Files action could be saved.",
                        run,
                    )
                break
            if run.command_count <= before_count:
                return False, f"Submitting {command!r} produced no backend command update.", run
            browser.wait_for_terminal_settle()
            for action in workspace_actions.get(command_index, []):
                path = str(action.get("path") or "")
                content = str(action.get("content") or "")
                browser.write_workspace_file(path, content)
                run = wait_for_workspace_update(
                    run_id,
                    wave_id=wave_id,
                    path=path,
                    content=content,
                )

        deadline = time.monotonic() + LOCAL_UI_UPDATE_TIMEOUT
        while time.monotonic() < deadline:
            run = AdventureRun.objects.select_related("current_wave", "selected_variant", "level").get(pk=run_id)
            if run.status != "started" or run.current_wave_id != wave_id:
                break
            time.sleep(0.25)
        if run.status == "started" and run.current_wave_id == wave_id:
            return (
                False,
                f"Authored sequence for wave {run.current_wave.slug!r} did not advance the run.",
                run,
            )

    audit_ok, audit_detail = audit_completed_run(run)
    if not audit_ok:
        return False, audit_detail, run

    completion_exists = AdventureLevelCompletion.objects.filter(
        player=run.player,
        adventure_level=run.level,
    ).exists()
    if run.status == "completed" and (completion_exists or run.is_replay):
        outcome = (
            "Adventure replay completed."
            if run.is_replay
            else "Adventure level completion recorded."
        )
        return True, f"{outcome} {audit_detail}", run
    return False, f"Run ended with status {run.status!r} and completion={completion_exists}.", run


def audit_completed_run(run: AdventureRun) -> tuple[bool, str]:
    """Prove each wave used its complete selected solution with no hidden errors."""

    run_waves = list(
        run.run_waves.select_related("wave", "selected_variant").order_by(
            "wave__sort_order",
            "id",
        )
    )
    steps = list(CommandStep.objects.filter(attempt_id=run.id).order_by("id"))
    grouped_steps: list[list[CommandStep]] = []
    current: list[CommandStep] = []
    for step in steps:
        current.append(step)
        if step.result_category == CommandStep.ResultCategory.TARGET_MATCHED:
            grouped_steps.append(current)
            current = []

    if current:
        return False, "Strict audit found command steps after the last completed wave."
    if len(grouped_steps) != len(run_waves):
        return (
            False,
            f"Strict audit found {len(grouped_steps)} command groups for {len(run_waves)} waves.",
        )

    command_total = 0
    for run_wave, wave_steps in zip(run_waves, grouped_steps, strict=True):
        expected = list(run_wave.selected_variant.solution_commands or [])
        actual = [step.command_text for step in wave_steps]
        if actual != expected:
            return (
                False,
                f"Strict audit mismatch in wave {run_wave.wave.slug!r}: "
                f"expected {expected!r}, got {actual!r}.",
            )
        failed_steps = [step.command_text for step in wave_steps if not step.was_processable]
        if failed_steps:
            return (
                False,
                f"Strict audit found unprocessable commands in wave "
                f"{run_wave.wave.slug!r}: {failed_steps!r}.",
            )
        command_total += len(wave_steps)

    return (
        True,
        f"Strict audit: {len(run_waves)}/{len(run_waves)} complete wave sequences, "
        f"{command_total} processable commands.",
    )


def write_results(
    path: Path,
    results: list[dict],
    gates: list[dict],
    totals: dict[str, int],
    session: str,
    username: str,
    matrix_run_id: str,
) -> None:
    passed = sum(result["status"].startswith("pass") for result in results)
    failed = len(results) - passed
    lines = [
        "# Frontend level-sequence verification",
        "",
        f"- Date: {datetime.now().isoformat(timespec='seconds')}",
        f"- Browser session: `{session}`",
        f"- QA account: `{username}`",
        f"- Matrix run: `{matrix_run_id}`",
        f"- Levels checked: **{len(results)} / {totals['levels']}**",
        f"- Passed: **{passed}**",
        f"- Failed: **{failed}**",
        "- Method: commands were filled into the rendered Git command textbox and submitted with Enter; "
        "authored workspace edits were saved through the rendered Project Files editor.",
        "- Variant selection: the run's selected variant was read from the local QA database; no command was sent directly to an API.",
        "- Strict pass rule: every wave must persist the selected variant's complete authored command sequence in order, "
        "and every command must be processable; prefix-only advancement and visible terminal errors fail the level.",
        "",
        "## Progression scaffolding",
        "",
        "Challenge trials were not part of this level-only regression. Their completion rows were ensured "
        "for the disposable QA player after each chapter so the next chapter could be opened. Paid-story "
        "entitlements and prerequisite command-form mastery were granted to the same QA player for "
        "cross-story coverage. These scaffolds do not alter any recorded level pass/fail result.",
        "",
    ]
    if gates:
        lines.extend(
            [
                "| Gate | Challenge levels present | Trials present | Mastery forms present |",
                "|---|---:|---:|---:|",
            ]
        )
        for gate in gates:
            lines.append(
                f"| {gate['story']} · {gate['chapter']} | {gate.get('challenge_levels', 0)} | "
                f"{gate.get('trials', 0)} | {gate.get('mastery_forms', 0)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Level results",
            "",
            "| # | Story | Chapter | Level | Status | Detail |",
            "|---:|---|---:|---|---|---|",
        ]
    )
    for index, result in enumerate(results, start=1):
        detail = str(result["detail"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {index} | {result['story']} | {result['chapter']} | {result['level']} | "
            f"{result['status']} | {detail} |"
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def prior_results(
    path: Path,
    *,
    username: str,
    session: str,
) -> dict[tuple[str, int, str], dict]:
    latest: dict[tuple[str, int, str], dict] = {}
    if not path.exists():
        return latest
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("username") != username or record.get("session") != session:
            continue
        key = (str(record.get("story")), int(record.get("chapter", 0)), str(record.get("level_slug")))
        latest[key] = record
    return latest


def verify(args: argparse.Namespace, totals: dict[str, int]) -> int:
    output = workspace_path(args.output)
    screenshots = output / "screenshots"
    output.mkdir(parents=True, exist_ok=True)
    screenshots.mkdir(parents=True, exist_ok=True)
    jsonl = output / "level-sequence-results.jsonl"
    results_path = output / "frontend-level-test-results.md"
    matrix_run_id = f"{args.session}-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    history = prior_results(
        jsonl,
        username=args.username,
        session=args.session,
    )

    player = current_player(args.username)
    browser = Browser(args.session)
    levels = published_levels()
    results: list[dict] = []
    gates: list[dict] = []
    total = len(levels)

    by_chapter: dict[int, list[AdventureLevel]] = defaultdict(list)
    for level in levels:
        by_chapter[level.chapter_id].append(level)

    ordered_chapters = list(
        Chapter.objects.filter(
            id__in=by_chapter.keys(),
            is_published=True,
        )
        .select_related("story")
        .order_by("story__sort_order", "sort_order", "number", "id")
    )

    checked = 0
    prepared_stories: set[str] = set()
    for chapter in ordered_chapters:
        story_slug = chapter.story.slug
        if story_slug not in prepared_stories:
            grant_story_entitlement(player, story_slug)
            mastery_forms = grant_prerequisite_story_mastery(player, chapter.story)
            if chapter.story.prerequisite_story_id:
                gates.append(
                    {
                        "story": story_slug,
                        "chapter": f"prerequisite {chapter.story.prerequisite_story.title}",
                        "mastery_forms": mastery_forms,
                    }
                )
                print(
                    f"[gate] {story_slug}: ensured {mastery_forms} prerequisite mastery form(s)",
                    flush=True,
                )
            prepared_stories.add(story_slug)
        browser.open(f"http://localhost:5173/stories/{story_slug}?chapter={chapter.id}")
        time.sleep(0.75)
        chapter_levels = by_chapter[chapter.id]
        for level_index, level in enumerate(chapter_levels, start=1):
            checked += 1
            existing = AdventureLevelCompletion.objects.filter(
                player=player,
                adventure_level=level,
            ).first()
            if existing is not None:
                prior = history.get((story_slug, chapter.number, level.slug), {})
                is_bypass = existing.stars == 0 and existing.adventure_run_id is None
                record = {
                    "matrix_run_id": matrix_run_id,
                    "username": args.username,
                    "session": args.session,
                    "story": story_slug,
                    "chapter": chapter.number,
                    "chapter_title": chapter.title,
                    "level": level.title,
                    "level_slug": level.slug,
                    "status": "fail-preserved" if is_bypass else "pass-existing",
                    "detail": (
                        prior.get("detail", "Earlier frontend sequence failure; test-only gate bypass retained.")
                        if is_bypass
                        else f"Completion already recorded with {existing.stars} star(s)."
                    ),
                }
                results.append(record)
                append_jsonl(jsonl, record)
                state = "FAIL preserved" if is_bypass else "PASS existing"
                print(f"[{checked:03d}/{total}] {state} · {story_slug} · C{chapter.number:02d} · {level.title}", flush=True)
                continue

            run: AdventureRun | None = None
            try:
                run = active_run_for(browser, player, level)
                if run is None:
                    run = start_level(
                        browser,
                        player=player,
                        story_slug=story_slug,
                        level_index=level_index,
                        level=level,
                    )
                passed, detail, run = exercise_run(browser, run)
                status = "pass" if passed else "fail"
            except Exception as exc:  # Continue the matrix after capturing the failed state.
                passed = False
                status = "fail"
                detail = f"{type(exc).__name__}: {exc}"

            if not passed:
                screenshot = screenshots / (
                    f"{matrix_run_id}-sequence-fail-{checked:03d}-{story_slug}-{level.slug}.png"
                )
                browser.screenshot(screenshot, annotate=True)
                detail = f"{detail} Evidence: {screenshot.relative_to(output).as_posix()}"
                if args.continue_on_failure:
                    bypass_failed_level(player, level, run)

            record = {
                "matrix_run_id": matrix_run_id,
                "username": args.username,
                "session": args.session,
                "story": story_slug,
                "chapter": chapter.number,
                "chapter_title": chapter.title,
                "level": level.title,
                "level_slug": level.slug,
                "run_id": run.id if run else None,
                "status": status,
                "detail": detail,
            }
            results.append(record)
            append_jsonl(jsonl, record)
            label = "PASS" if passed else "FAIL"
            print(
                f"[{checked:03d}/{total}] {label} · {story_slug} · C{chapter.number:02d} · {level.title} · {detail}",
                flush=True,
            )
            write_results(
                results_path,
                results,
                gates,
                totals,
                args.session,
                args.username,
                matrix_run_id,
            )
            if not passed and not args.continue_on_failure:
                return 1

        challenge_levels, trials = grant_chapter_trial_gate(player, chapter)
        gate = {
            "story": story_slug,
            "chapter": f"{chapter.number:02d} {chapter.title}",
            "challenge_levels": challenge_levels,
            "trials": trials,
        }
        gates.append(gate)
        print(
            f"[gate] {story_slug} C{chapter.number:02d}: ensured {challenge_levels} challenge level(s), {trials} trial(s)",
            flush=True,
        )
        write_results(
            results_path,
            results,
            gates,
            totals,
            args.session,
            args.username,
            matrix_run_id,
        )

    browser.run("errors", timeout=10, attempts=1)
    write_results(
        results_path,
        results,
        gates,
        totals,
        args.session,
        args.username,
        matrix_run_id,
    )
    return 1 if any(result["status"] == "fail" for result in results) else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="qa_levels_20260715")
    parser.add_argument("--session", default="git-it-levels")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--cheat-sheet", default=str(DEFAULT_CHEAT_SHEET))
    parser.add_argument("--generate-only", action="store_true")
    parser.add_argument("--continue-on-failure", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    totals = generate_cheat_sheet(workspace_path(args.cheat_sheet))
    print(
        f"Generated cheat sheet: {totals['levels']} levels, {totals['waves']} waves, "
        f"{totals['variants']} variants",
        flush=True,
    )
    if args.generate_only:
        return 0
    return verify(args, totals)


if __name__ == "__main__":
    raise SystemExit(main())
