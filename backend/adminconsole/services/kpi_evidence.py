"""Read-only live-practice research snapshot; arithmetic remains in mastery_metrics."""

import json
import os
from collections import defaultdict
from pathlib import Path
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone

from progress.objectives import SO_CAR_LEVELS
from progress.services.kpi_range import ALL_TIME, KPI_TIMEZONE
from progress.services.mastery_metrics import balanced, live_records, samples
from progress.services.metrics import MetricsService

from .evidence_xlsx import workbook

OBJECTIVES = json.loads(
    Path(__file__).with_name("evidence_objectives.json").read_text(encoding="utf-8-sig")
)
MODULES = {
    1: "Local Repository Foundations",
    2: "Branching and Collaboration",
    3: "Conflict Resolution",
    4: "Advanced Recovery and History",
}
METRICS = [
    ("scr", "SCR (%)", 80),
    ("car", "CAR (%)", 70),
    ("hlcr", "HLCR (%)", 70),
    ("arc", "ARC", 2),
    ("rta", "RTA (%)", 65),
    ("retry_success_rate", "RSR (%) - supplementary", None),
]
UNITS = {
    "scr": ("Mastered required tiers", "Attempted required tiers"),
    "car": ("Scenario score sum", "Eligible scored scenarios"),
    "hlcr": ("Mastered Hard tiers", "Attempted Hard tiers"),
    "arc": ("Unsuccessful attempts before mastery", "Mastered tiers"),
    "rta": ("First-run checkpoint clears", "Eligible novel checkpoints"),
    "retry_success_rate": ("Successful recovery retries", "Concluded recovery retries"),
}


def status(value, target, up=True):
    if value is None:
        return "Insufficient Evidence"
    return "Met" if (value >= target if up else value <= target) else "Not Met"


def metric_columns():
    return [label for key, name, _ in METRICS for label in (name, *UNITS[key])]


def metric_values(records):
    result = balanced(records)
    return [
        result[key][field]
        for key, _, _ in METRICS
        for field in ("value", "numerator", "denominator")
    ]


def evidence_notes(records):
    return "; ".join(f"{key}={value}" for key, value in samples(records).items())


def objective_rows(records, cohort=False):
    for objective in OBJECTIVES:
        module_records = [r for r in records if r["module"] == objective["module"]]
        for condition in objective["metrics"]:
            key = condition["key"]
            selected = (
                [r for r in module_records if r["slug"] in SO_CAR_LEVELS.get(objective["id"], ())]
                if key == "car"
                else module_records
            )
            metric = balanced(selected, cohort=cohort)[key]
            yield objective, condition, metric


@transaction.atomic
def build_evidence(query=""):
    # PostgreSQL's default READ COMMITTED would allow sheets to observe different
    # commits. SQLite's transaction provides a consistent read snapshot.
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
    cutoff = timezone.now()
    accounts = get_user_model().objects.filter(date_joined__lt=cutoff)
    registered = accounts.count()
    learners = accounts.filter(is_staff=False)
    total_learners = learners.count()
    if query.strip():
        learners = learners.filter(
            Q(username__icontains=query.strip()) | Q(email__icontains=query.strip())
        )
    users = list(learners.order_by("pk").values_list("pk", "player__pk"))
    player_ids = [player for _, player in users if player is not None]
    runs = (
        MetricsService()
        ._kpi_runs(kpi_range=ALL_TIME)
        .filter(player_id__in=player_ids, started_at__lt=cutoff)
    )
    records = live_records(runs, end_before=cutoff)
    grouped = defaultdict(list)
    for row in records:
        grouped[row["player_id"]].append(row)
    summary = [
        [
            "Anonymous Learner ID",
            *metric_columns(),
            "Modules with recorded participation",
            "Number of modules started",
            "Evidence availability",
        ]
    ]
    modules = [
        [
            "Anonymous Learner ID",
            "Module Number",
            "Module Name",
            *metric_columns(),
            "Evidence availability",
        ]
    ]
    objectives = [
        [
            "Anonymous Learner ID",
            "Module",
            "Specific Objective ID",
            "Specific Objective Name",
            "KPI",
            "Recorded Value",
            "Approved Target",
            "Individual comparison (not cohort attainment)",
            "Eligible assessment count",
            "Numerator",
            "Denominator",
            "Evidence availability",
        ]
    ]
    for _, player in users:
        anonymous = "L-" + uuid4().hex
        rows = grouped[player]
        started = sorted({r["module"] for r in rows})
        summary.append(
            [
                anonymous,
                *metric_values(rows),
                ", ".join(map(str, started)),
                len(started),
                evidence_notes(rows),
            ]
        )
        for number in started:
            scoped = [r for r in rows if r["module"] == number]
            modules.append(
                [anonymous, number, MODULES[number], *metric_values(scoped), evidence_notes(scoped)]
            )
        for objective, condition, metric in objective_rows(rows):
            objectives.append(
                [
                    anonymous,
                    objective["module"],
                    objective["id"],
                    objective["title"],
                    condition["key"],
                    metric["value"],
                    (">= " if condition["up"] else "<= ") + str(condition["target"]),
                    status(metric["value"], condition["target"], condition["up"]),
                    metric["denominator"],
                    metric["numerator"],
                    metric["denominator"],
                    "Available" if metric["value"] is not None else "Insufficient Evidence",
                ]
            )
    scope = (
        "All matching non-staff accounts; inactive included; no 100-row directory limit"
        if query.strip()
        else "All non-staff accounts; inactive included"
    )
    research = [
        ["Measure", "Value", "Contributors / target", "Status / notes"],
        ["Scope", scope],
        ["Cutoff (exclusive)", cutoff.isoformat()],
        ["Registered accounts (global)", registered],
        ["Eligible non-staff accounts (global)", total_learners],
        ["Selected non-staff accounts", len(users)],
    ]
    overall = balanced(records, cohort=True)
    for key, name, target in METRICS:
        metric = overall[key]
        research.append(
            [name, metric["value"], metric["denominator"], "Equal-weight contributing learners"]
        )
        research.append(
            [
                name + " target",
                target,
                None,
                status(metric["value"], target, key != "arc")
                if target is not None
                else "Supplementary; no target",
            ]
        )
    general_met = 0
    for number, name in MODULES.items():
        metric = balanced([r for r in records if r["module"] == number], cohort=True)["scr"]
        verdict = status(metric["value"], 80)
        general_met += verdict == "Met"
        research.append([f"GO {number}: {name}", metric["value"], "SCR >= 80", verdict])
    verdicts = defaultdict(list)
    for objective, condition, metric in objective_rows(records, cohort=True):
        verdict = status(metric["value"], condition["target"], condition["up"])
        verdicts[objective["id"]].append(verdict)
        research.append(
            [
                objective["id"] + " " + condition["key"],
                metric["value"],
                (">= " if condition["up"] else "<= ") + str(condition["target"]),
                verdict,
            ]
        )
    research.extend(
        [
            ["Total general objectives met", general_met],
            [
                "Total specific objectives met",
                sum(all(v == "Met" for v in values) for values in verdicts.values()),
            ],
            ["Population evidence", evidence_notes(records)],
        ]
    )
    metadata = [
        ["Item", "Definition / value"],
        ["Generated / cutoff", cutoff.astimezone(KPI_TIMEZONE).isoformat()],
        ["Timezone", "Asia/Manila"],
        ["Mode", "Live practice, all time to export cutoff; not a frozen formal study"],
        ["Scope", scope],
        ["Search applied", "Yes (text omitted for privacy)" if query.strip() else "No"],
        [
            "Backend revision",
            os.environ.get("RENDER_GIT_COMMIT") or os.environ.get("GIT_COMMIT") or "Unavailable",
        ],
        [
            "Data source",
            "MetricsService._kpi_runs; mastery_metrics.live_records, balanced, samples; progress.objectives.SO_CAR_LEVELS",
        ],
        [
            "Anonymous IDs",
            "Random workbook-local IDs. No identity mapping exported or retained; cannot link across exports. Detailed measurements may still be identifying in small cohorts.",
        ],
        [
            "Missing values",
            "Blank numeric value means unavailable, never zero; counts of zero indicate no contributing evidence.",
        ],
        [
            "Cohort weighting",
            "Mean of rounded contributing learner scores using balanced(cohort=True); not a mean of module rows or pooled events. Cohort denominators count learners.",
        ],
        [
            "SCR",
            "100 * mastered required tiers / unique required tiers with outcomes. Open tiers without outcomes excluded; command inactivity >= 7 days counts as concluded.",
        ],
        [
            "CAR",
            "Mean latest eligible fresh-content scenario-clear score: 100 * min(1, T / max(1, A)). T validated reference count; A counted commands plus assessed diagnostics. Missing references unscored. Numerator sums scenario percentage points.",
        ],
        ["HLCR", "SCR restricted to required Hard tiers."],
        [
            "ARC",
            "Unsuccessful attempts before first mastery / mastered tiers. Failures and meaningful abandonments count; successful repetitions do not.",
        ],
        [
            "RTA",
            "100 * valid novel checkpoints cleared on first run / valid novel checkpoints assessed; Modules 3-4 Hard tiers. Missing novelty/reference evidence unscored; pending and missing counts supplied.",
        ],
        [
            "RSR",
            "100 * successful recovery retries / concluded recovery retries following failed runs. Supplementary; no target.",
        ],
        [
            "Exclusions",
            "Staff, optional levels and transfer practice runs excluded from tier records. Replays excluded except eligible fresh clears for CAR; solved content cannot inflate CAR.",
        ],
        [
            "Objectives",
            "Approved mapping mirrors learningObjectives.ts. CAR uses objective-specific level slugs; other conditions use module metrics. Multi-condition SO 3.5 and SO 4.5 require all conditions for cohort attainment. Individual comparisons are descriptive, not official cohort conclusions.",
        ],
        [
            "Formal studies",
            "Separate prospective manifest, fixed assigned tiers, references and cutoff; unattempted valid assignments can score zero. Use kpi_study freeze/export for saved formal results. This workbook does not substitute for frozen-study evidence.",
        ],
        [
            "Reproducibility",
            "One transaction and one bulk record extraction. Matches live KPI calculations for this population/cutoff on unchanged data. Not an immutable historical database: later edits, deletions, content/exposure changes or activity can change reconstruction. Archive this workbook; use frozen studies for longitudinal reproducibility.",
        ],
        [
            "Unsupported date column",
            "Last relevant activity omitted: canonical tier records do not expose a single authoritative activity timestamp.",
        ],
        ["Source documentation", "KPI_METHODOLOGY.md; progress/services/mastery_metrics.py"],
    ]
    return workbook(
        [
            ("Learner KPI Summary", summary),
            ("Per-Module KPI Results", modules),
            ("Specific Objective Results", objectives),
            ("Research Summary", research),
            ("KPI Methodology and Metadata", metadata),
        ]
    ), cutoff
