# Scripts

Root-level script files are compatibility wrappers for CI/package scripts. New
implementation code should live in grouped folders:

- `checks/` — repository, architecture, docs, API, and deploy guards.
- `api/` — OpenAPI/schema generation helpers.
- `assets/` — sprite and image processing helpers.
- `packaging/` — source-zip and artifact cleanup helpers.

Keep wrappers when external tooling still calls `python scripts/<name>.py`.
