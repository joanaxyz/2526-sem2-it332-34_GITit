# Shared Git domain

This folder keeps reusable Git-specific subsystems together instead of spreading
them directly across `shared/`:

- `simulator/` owns in-browser Git state execution.
- `commandCatalog/` owns Git command metadata/icons used by product screens.

Product features should import through `@/shared/git/...` so the root `shared/`
folder remains reserved for truly generic API, auth, UI, navigation, and utility
code.
