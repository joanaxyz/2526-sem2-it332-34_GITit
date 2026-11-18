# Learner KPI evidence export

In Admin > Learners, apply a search (or clear it) and select **Export KPI
Evidence (.xlsx)**. The export contains every matching non-staff account,
including inactive accounts and accounts beyond the directory's 100-row limit.
Accounts without a player/profile remain in the summary with blank metrics.
Search text and account identity fields are not written to the workbook.

The admin-only GET `/api/admin/users/kpi-evidence/?q=...` produces five sheets
using one transaction and one bulk `live_records` extraction. All arithmetic
uses `balanced`, `samples`, and the existing objective CAR slug mapping. No
progress or assessment records are written. PostgreSQL uses repeatable-read;
SQLite uses its read transaction. The cutoff is captured once and excludes
runs/evidence after export start. This endpoint exports live practice only.

The objective metadata mirrors `learningObjectives.ts`; a parity test requires
every condition, title and target to agree. Individual target comparisons are
descriptive. Official cohort objective totals require every condition; RSR has
no target. Cohort metrics equally weight contributing learners, including their
existing backend rounding, rather than averaging modules or pooling events.

The standard-library XLSX writer adds no dependencies. It emits literal inline
strings (never formulas), numeric measurements, frozen headers and blue styling.
Blank values represent missing measurements; zero denominators remain auditable.
CAR numerator is a sum of scenario percentage scores, not a count of commands.
IDs are random and workbook-local, with no retained mapping. Small-cohort scores
can still be identifying. The optional last-activity field is omitted because
canonical KPI records do not provide one authoritative timestamp.

The methodology sheet documents actual formulas, exclusions, missing data,
snapshot scope and limitations. Revision is included only if deployment supplies
`RENDER_GIT_COMMIT` or `GIT_COMMIT`. Preserve the exported file as the snapshot.
Live data is mutable: rerunning later at a historical cutoff is not guaranteed
to reproduce it after edits, deletions, new activity or content/exposure changes.
For immutable formal-study evidence use the existing prospective
`kpi_study create`, `freeze`, and `export` workflow in `KPI_METHODOLOGY.md`.

## Local checks

Run the backend and frontend normally. Sign in as staff, visit Learners, download
with and without an applied search, and open the XLSX in Excel or LibreOffice.
Confirm five sheets, blank unavailable metrics, no names/emails, and matching
learner counts. With no search and no concurrent activity, compare Research
Summary against KPI Overview. Ordinary learners must receive HTTP 403.

From the repository root, using the backend Python environment:

```
python -m pytest backend/adminconsole/tests/test_kpi_evidence.py backend/progress/tests/test_kpi_scope.py -q
```

From `frontend`, run `npx tsc -b`. Tests cover permissions, empty populations,
privacy, search filtering, existing live metric parity, literal formula-like
strings and objective metadata parity. Visual inspection in Excel remains a
manual check; XML validation does not prove rendering in every spreadsheet app.
