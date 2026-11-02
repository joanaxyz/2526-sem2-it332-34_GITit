# Slice 14 Pre-Implementation Preservation Baseline

Captured after strict PRE approval and before any Slice 14 production edit. The machine-readable source is `PRE_SLICE_BASELINE.json`; this document explains its contract and records the executable baseline result.

## Preservation contract

- The capture expands every untracked file and records 221 dirty/deleted/untracked paths with status, presence, byte count, and SHA-256.
- 207 dirty paths are strict byte-for-byte entries. The current `GOAL.md` and approved `PLAN.md` have separate frozen hashes.
- Fourteen existing targets are mutable only within their approved replacement regions. Ten code targets carry top-level declaration/statement or normalized API-call fingerprints. The two architecture documents are append-only with exact original-prefix hashes. The two generated artifacts use semantic manifests plus generator reproducibility instead of byte preservation.
- Twenty-three high-risk payload/model/service/request/generator files are strict protected entries. Both gameplay payload modules must remain byte-for-byte identical. The deleted `backend/adventures/serializers.py` is recorded as absent and must stay absent.
- The two domain OpenAPI modules, focused response-contract test, baseline files, and evidence file were absent at the capture instant. The baseline files are expected additions after capture; the production additions remain blocked until replay succeeds.
- No file was staged, committed, normalized, discarded, or rewritten to take this baseline.

## JSON layout

- Dirty-manifest rows are `[status, path, exists, bytes, sha256]`.
- File facts are `[path, exists, bytes, sha256]`; mutable rows prepend their capture status.
- Python protected regions are `[identifier, node kind, raw-source sha256, AST sha256, optional ordered statement hashes]`.
- TypeScript protected regions are `[declaration name, raw-source sha256]`.
- API-wrapper regions remove response-only imports and normalize the response generic while hashing every remaining route, operation, body, query, option, and function byte. Non-response imports have independent hashes.
- Generated semantics record current component property/required sets and operation response references. The generator owner has an independent strict hash.
- `behavior` contains normalized authenticated endpoint evidence: exact response key sets and stable database/workspace state deltas without fixture IDs or timestamps.

## Captured contract defects

- `AdventureRunResponse` omits the runtime `passed` key and marks always-emitted nullable keys optional.
- `ChallengeRunResponse` omits the runtime `story` key and marks always-emitted nullable keys optional.
- `RuntimeStepResponse` advertises Challenge-only history fields while requiring only `id` and `command_text`.
- Adventure command `run` is an open object rather than the real full/partial union.
- Challenge command `run` is an open object; the command step omits `evaluation_result`; and the command envelope incorrectly optionalizes five always-emitted fields.
- Neither feature response type module references `ApiSchemas` for its complete success-response shapes.

## Authenticated behavior matrix

All cases ran against an isolated Django test database and authenticated DRF clients:

| Case | HTTP | Captured result |
|---|---:|---|
| Adventure start, detail, create-file | 201 / 200 / 200 | All three emit the same exact 21-key full run, including `is_passed` and `passed`; workspace state changes and `NOTES.md` exists. |
| Adventure diagnostic command | 200 | Exact nine-key envelope, four-key partial run with literal `partial: true`, four-key step; one persisted diagnostic step, no repository/completion/reward transition. |
| Adventure wave-clear command | 200 | Exact full run, no `partial`; current wave advances, prior/new wave statuses are `completed`/`started`, one step persists, no completion/reward transition. |
| Adventure terminal command | 200 | Exact full run, no `partial`; run completes, repository changes, one step and one level completion persist, existing reward/progress deltas are captured. |
| Challenge start, detail, create-file, retry | 201 / 200 / 200 / 201 | All emit the same exact 25-key full run, including `story`; workspace state changes and retry creates a full response. |
| Challenge diagnostic command | 200 | Exact eight-key envelope, nine-key started update, nine-key step including `evaluation_result`; all four transition-only fields are absent. |
| Challenge terminal command | 200 | Exact eight-key envelope, 13-key terminal update, nine-key step; `mastery_progress` and `sibling_levels` are present/non-null, `completion` and `next_difficulty` are present/nullable, and completion/reward/progress rows persist. |

The normalized response keys and exact state deltas are stored under `behavior` in the JSON manifest. Endpoint request logging was informational; fixture IDs, timestamps, durations, and request IDs are deliberately excluded from the replay contract.

## Baseline gate

Before implementation, replay must prove:

1. the JSON parses and all 221 captured manifest rows are internally valid;
2. all 207 strict dirty entries, 23 strict protected entries, approved plan files, append-only prefixes, and protected declaration/statement regions match;
3. current generated semantic facts match the captured defects and operation references;
4. the authenticated behavior matrix reproduces the captured key sets and state deltas;
5. both domain schema modules and the response-contract test remain absent until the gate passes.

Production editing is prohibited if any assertion fails.
