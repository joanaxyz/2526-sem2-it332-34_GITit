# Backend Architecture and DRY Optimization Goal

The backend model and module design should have one explicit owner for each durable rule, no dead persisted state, no runtime import cycles, and no meaningful duplicate implementation paths. The maintained Python code should be consistently formatted and the repository should enforce those properties in CI.

The goal is complete only when the model cutover has a forward migration, focused and full integration tests pass on PostgreSQL and Redis, the maintained backend has zero runtime import cycles, the identified duplicate implementations are gone, Ruff lint and format checks pass, and the architecture documentation describes what the guard actually enforces.
