# Authored curriculum source

This directory is the canonical home for human-authored curriculum definitions.
Content is grouped by chapter, adventure, or cohesive concept module; stable
composer modules preserve the public seed-data imports used by the runtime.

Ownership rules:

1. Edit hand-authored curriculum only under `seed_data/source/`.
2. Keep deterministic generated artifacts under `seed_data/generated/`.
3. Regenerate generated output through the canonical management command; never
   edit generated files by hand.
4. Preserve stable composer exports when splitting a large authored ledger, and
   keep source-layout and seed-idempotency checks passing.
