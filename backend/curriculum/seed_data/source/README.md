# Curriculum source data migration

This folder is the landing zone for human-authored curriculum definitions split by
chapter/module. The existing monolithic seed files remain the runtime source of
truth until each chapter is migrated and checked against deterministic seed
output.

Migration rule:

1. Move only hand-authored definitions here.
2. Keep generated artifacts under `seed_data/generated/`.
3. Do not edit generated output by hand.
4. Each migrated chapter must keep seed idempotency tests passing.
