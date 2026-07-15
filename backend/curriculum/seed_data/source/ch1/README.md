# Chapter 1 source migration

Chapter 1 is the first target for splitting `adventure_levels.py`, `challenges.py`,
and `blueprint_overlay.py` into reviewable, chapter-scoped modules. The current
monolithic files still drive seeding; this folder records the intended destination
so future changes do not add more hand-authored data to generated or oversized
modules.
