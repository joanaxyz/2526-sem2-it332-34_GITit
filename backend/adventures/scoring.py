"""Adventure mastery scoring.

Implements the CommandAdventure scoring model from the refactor brief. This is
intentionally pure (no DB access) so it can be unit-tested and reused by the
AdventureRun orchestration service.

Score components (weights):
    correctness  60%
    efficiency   25%
    independence 15%

Bands (applied to the final score):
    < 70        failed
    70 - 84     passed
    85 - 94     strong_pass
    95 - 100    mastered

A problem that is not solved scores 0 correctness and yields no mastery
progress, regardless of efficiency/independence.
"""

from dataclasses import dataclass

CORRECTNESS_WEIGHT = 0.60
EFFICIENCY_WEIGHT = 0.25
INDEPENDENCE_WEIGHT = 0.15

PASS_THRESHOLD = 70
STRONG_PASS_THRESHOLD = 85
MASTERED_THRESHOLD = 95

# Each hint costs this many independence points.
HINT_PENALTY = 25

BAND_FAILED = "failed"
BAND_PASSED = "passed"
BAND_STRONG_PASS = "strong_pass"
BAND_MASTERED = "mastered"


@dataclass(frozen=True)
class AttemptScore:
    correctness_score: int
    efficiency_score: int
    independence_score: int
    final_score: int
    band: str
    passed: bool
    mastery_gain: float


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def correctness_score(*, solved: bool) -> int:
    return 100 if solved else 0


def efficiency_score(*, counted_commands: int, ideal_commands: int) -> int:
    """100 when the learner used the ideal command count (or fewer)."""
    ideal = max(1, ideal_commands)
    used = max(1, counted_commands)
    return int(round(_clamp((ideal / used) * 100)))


def independence_score(*, hint_count: int) -> int:
    return int(round(_clamp(100 - HINT_PENALTY * max(0, hint_count))))


def band_for(final_score: int) -> str:
    if final_score < PASS_THRESHOLD:
        return BAND_FAILED
    if final_score < STRONG_PASS_THRESHOLD:
        return BAND_PASSED
    if final_score < MASTERED_THRESHOLD:
        return BAND_STRONG_PASS
    return BAND_MASTERED


def mastery_gain_for(*, final_score: int, solved: bool) -> float:
    """Per-attempt mastery contribution in [0, 1].

    A bare pass (72%) yields partial mastery; a 95%+ run yields near-full
    mastery. Below the pass threshold yields nothing, so a learner cannot reach
    full mastery by scraping a single weak pass.
    """
    if not solved or final_score < PASS_THRESHOLD:
        return 0.0
    span = 100 - PASS_THRESHOLD
    return round(0.4 + ((final_score - PASS_THRESHOLD) / span) * 0.6, 4)


class AdventureScoringService:
    def score_attempt(
        self,
        *,
        solved: bool,
        counted_commands: int,
        ideal_commands: int,
        hint_count: int,
    ) -> AttemptScore:
        correctness = correctness_score(solved=solved)
        efficiency = efficiency_score(
            counted_commands=counted_commands, ideal_commands=ideal_commands
        )
        independence = independence_score(hint_count=hint_count)
        # Efficiency/independence only matter once the objective is met.
        if not solved:
            efficiency = 0
            independence = 0
        final = int(
            round(
                CORRECTNESS_WEIGHT * correctness
                + EFFICIENCY_WEIGHT * efficiency
                + INDEPENDENCE_WEIGHT * independence
            )
        )
        return AttemptScore(
            correctness_score=correctness,
            efficiency_score=efficiency,
            independence_score=independence,
            final_score=final,
            band=band_for(final),
            passed=final >= PASS_THRESHOLD and solved,
            mastery_gain=mastery_gain_for(final_score=final, solved=solved),
        )
