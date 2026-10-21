# Tutor semantic index

`scenario-index.json` is generated from the public `label`, `story`, `starting_point`,
`task`, and `real_world_context` fields in both curriculum scenario banks. It contains
source-qualified IDs and normalized 768-dimensional vectors, not answer keys or
solution/evaluation fields. It ships with the backend; no vector database is required.

From `backend/`, run `python manage.py build_tutor_index` with
`GOOGLE_AI_STUDIO_API_KEY` configured. The command resumes matching `.building`
checkpoints and respects rate-limit delays. Check freshness without network calls:
`python manage.py build_tutor_index --check`.

Model, dimensions, preprocessing version and public-corpus digest must match before
runtime semantic matching is enabled. Changed files are picked up by modification
time. Retrieval returns the matched case IDs; the answer guard looks up those cases'
answer fields separately and never sends them to a provider. Missing/stale indexes or
limited query embeddings fall back to text matching and keep scenario protection on.
Reply generation follows Gemini → Groq; embedding vectors are never mixed between
models/providers.
