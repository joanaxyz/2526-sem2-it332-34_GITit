# Learning performance KPIs

Git it! keeps the five approved KPI names and thresholds. Practice can be
repeated freely. Successful required repetitions build mastery; they are not
unsuccessful retries. The backend calculates the scores; learner and Admin
screens share their explanations.

## Definitions and targets

Let:

| Symbol | Meaning | Code name |
| --- | --- | --- |
| M | Required tiers mastered, each counted once after all required successful clears | `mastered` |
| N | Unique required tiers attempted (with an outcome) in live progress, or fixed tiers assigned in a study | tier records |
| H | Required hard tiers in that same population | `difficulty == "hard"` |
| T | Validated reference number of counted commands for the assessed variant | `ref_count` |
| A | Actual counted commands on the assessed run | `actual` |
| S | 1 when the assessed run succeeded; otherwise 0 | `passed` |
| F | Failed or meaningfully abandoned attempts before first mastery | `failures`, checkpoint `retries` |
| C | Eligible novel transfer checkpoints assessed live, or assigned in a study | transfer records |
| P | Transfer checkpoints cleared on their first run | transfer `passed` |

| Official KPI | Formula | Target |
| --- | --- | --- |
| SCR — Scenario Completion Rate | `100 × M / N` | ≥80% |
| CAR — Command Accuracy Rate | Mean of `100 × S × min(1, T / max(1, A))` | ≥70% |
| HLCR — Hard-Level Completion Rate | `100 × mastered H / assigned-or-attempted H` | ≥70%; Module 4 ≥65% |
| ARC — Average Retry Count | `sum(F for mastered tiers) / M` | ≤2; Module 4 ≤3 |
| RTA — Retry Transfer Accuracy | `100 × P / C` | ≥65%, Modules 3–4 only |

CAR's approved name is retained. Its operational meaning is **benchmark-relative
command efficiency**, not the percentage of individual commands that were
semantically correct. A validated reference is a working solution, not a claim
that no shorter Git solution exists. A successful shorter solution receives
100%; an unsuccessful assessed solution receives 0%.

For example, `failure → success → failure → success → success` masters a tier
requiring three clears. If its final run uses 4 commands against reference 3,
and its first transfer checkpoint succeeds: SCR 100%, CAR 75%, HLCR 100% when
hard, ARC 2, RTA 100%. The preceding successful repetitions do not add retries.

## Command assessment and references

The first run that achieves mastery is the live CAR assessment. A separate
`KpiCheckpoint` preserves its run, reference hash/count, actual count, result,
timestamp and unsuccessful-attempt total. Improving the best-star score later
cannot overwrite it. Stars keep their separate scoring budget.

Count the commands that consume the action budget, including incorrect input.
Optional diagnostics and shell operations stay free, using the existing runtime
accounting. For a diagnostic objective, an author may explicitly enable
`assess_diag`; both reference and actual counts then also include Git diagnostic
submissions. Shell commands remain excluded. A zero-count reference stays
unscored until an appropriate diagnostic policy is explicitly selected.

`ref_count` is never copied from `min_counted_commands`. `generate_targets`
replays the authored route and workspace edits through the actual browser Git
engine, and CI proves the committed targets and trajectories match a fresh
replay. Every seed then runs the backend completion evaluator on that replay and
counts its trajectory, so a reseed refreshes references without Node. The
`kpi_refs` command re-runs the live replay on demand. Merely processing every
command does not validate a solution. `ref_hash` covers the initial and target
states, objective, solution, workspace edits, diagnostic policy, action limit and
counting policy version. A run snapshots this evidence at launch; content drift during
play invalidates its assessment reference.

## Transfer and exposure

Authors explicitly reserve a variant with a written explanation of the
meaningful repository or goal difference. Reserved variants are excluded from
normal practice selection. A new variant ID alone does not establish transfer.
Canonical repository fingerprints screen equivalent content; the authored
review remains necessary to judge the educational difference.

After mastery, an eligible learner receives an assigned transfer checkpoint.
Home Progress offers an explicit start/resume link under RTA. It uses the
existing tier workspace with no expected-state answer or command guide. Its
first run is kept separately from practice mastery, rewards and replay scores.
Duplicate starts resume that run; abandonment records failure even when no
command was submitted. Later practice cannot replace the first result.

Every launch records durable `KpiExposure`, including empty discarded practice
launches. Previously seen IDs or canonical states are ineligible. Existing
histories may contain deleted launches: legacy progress has
`exposure_complete = false` and cannot certify novelty. Use a fresh study cohort
or newly designed assessment content with complete exposure evidence; do not
reinterpret old changed retries as transfer checkpoints.

## Live progress and formal studies

Live SCR/HLCR use unique attempted required tiers. A tier counts as attempted
once it has an outcome: it is mastered, a run on it ends (completed, failed or
left after submitting commands), or an open run's last command is at least 7
days old. Opening a tier without submitting a command is not an attempt; such
tiers appear in `samples.in_progress_tiers` and stay outside both denominators.
The rule applies to mastered and unmastered tiers alike, so it does not filter
out failures. Mastery is dated by its first clear, never by a later best-score
replay. Live CAR uses recorded valid
mastery assessments; live RTA uses concluded valid transfer checkpoints.
Pending transfer checkpoints and unavailable evidence are reported separately.
ARC includes only mastered tiers, with their contributing count shown.

Admin live cohort values average each contributing learner's score, so frequent
users do not dominate. The ordinary Admin date filter still selects runs started
in the chosen Manila calendar days; outcomes after the range end are excluded
from assessment evidence. It is a practice view, not a frozen study result.

A formal study must be created **before participants encounter assigned tiers**.
Its versioned manifest fixes participant IDs, tier requirements, accepted
reference hashes, reserved transfer variants, positive module weights and an
aware cutoff timestamp. Adding curriculum later does not change its denominator.

At cutoff, only terminal run evidence at or before the cutoff can establish
mastery. The run reaching the frozen required-clear count is the study CAR
assessment. Valid failed, unfinished or unattempted assignments score zero for
completion/CAR/transfer. Missing or invalid reference/novelty evidence stays
unscored and is counted separately; it is never fabricated as success or failure.
ARC remains null without a mastered tier. An unavailable assigned variant is
reported as missing assessment evidence.

Each participant's module scores are calculated first. Predefined weights are
then normalized over the KPI's applicable assigned modules (RTA only 3–4; HLCR
only modules with assigned hard tiers). An applicable module missing a score
makes that participant's overall KPI null. Cohort values average the observed
participant scores and report the contributing sample. Missing participants
must be considered when interpreting those averages.

Freeze is transactional and allowed only after cutoff. Repeated freeze/export
returns the saved report, even after later practice or content changes. Reports
include the manifest, participant/module scores, per-tier run evidence, coverage,
missing evidence and unattempted assignments. Freeze promptly at the cutoff;
content unavailable when a still-unassessed assignment is frozen is treated
conservatively as missing evidence.

## Setup and research commands

Run from `backend/` with the project's Python environment and installed frontend
Node dependencies. Migrations add storage without inventing historic assessments.
`seed_curriculum` (and so `seed_all`) refreshes every reference from the
committed replay; run `kpi_refs` for the author-selected cases below.

```powershell
python manage.py migrate
python manage.py seed_all
# Diagnostic-only cases need explicit author selection:
python manage.py kpi_refs --cases CASE_SLUG --diagnostics
# Review a structurally different case before reserving it:
python manage.py kpi_refs --cases TRANSFER_CASE_SLUG --reserve --reason "Describe the repository or goal difference"

python manage.py kpi_study create capstone-v1 --players 12 13 --tiers 41 42 --cutoff 2026-11-01T17:00:00+08:00
python manage.py kpi_study freeze capstone-v1 --output capstone-v1.json
python manage.py kpi_study export capstone-v1 --output capstone-v1.json
```

Case slugs and player/tier IDs above are placeholders. Validate references before
enrollment. The default command reports diagnostic-only routes as unscored;
explicitly select appropriate cases with `--diagnostics` to assess them.
Reserving a batch must leave at
least one normal practice variant per scenario. No case is automatically declared a
transfer task simply because it is last in a list.

Use a new study slug for every version. Default module weights are equal over
assigned modules; `--weights` accepts a JSON object with one positive weight per
assigned module. The creation command rejects retrospective enrollment and
unvalidated references. The export command requires an already frozen study.

`RateMetric.value` is authoritative. For live learner rates, `numerator` and
`denominator` count the formula's units; CAR's numerator sums percentage scores.
For cohort means, `unit: "participants"` means numerator sums participant
scores and denominator counts contributing participants. `samples` gives tier,
assessment and exposure coverage. No observations is null; measured failure is
zero. Retry Success Rate remains a supplementary diagnostic with no target:
successful concluded retries following an actual failed run divided
by all such concluded retries.

For research questions about knowledge improvement, use independently scored
comparable pretest/posttest tasks in addition to these KPIs. This is a separate
evaluation instrument; platform scores alone do not establish causal learning
gains.
