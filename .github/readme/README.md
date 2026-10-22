# README screenshots

These WebP images are screenshots of the application, not generated mockups.
Captures use a disposable SQLite database and demo account, plus the existing
development preview routes for populated map, profile, and dashboard states.
No shared player data or account credentials are included.

| Asset | Capture source | Framing |
| --- | --- | --- |
| `arcane-spire.webp` | `/design-preview/story-map`, Challenge Gate closed, scrolled to top | Complete 1600 × 1000 viewport |
| `adventure-workspace.webp` | Staging and Committing, Easy, after `git status` | Complete 1600 × 820 viewport |
| `repository-graph.webp` | Reconciling Diverged Local and Remote Histories, Easy | Square crop of the live graph |
| `challenge-workspace.webp` | Foundations Gate, Easy, during the first commit | Crop of objectives, battle, and terminal |
| `companion-profile.webp` | `/design-preview/home` | Crop of the character, rank, sprite, roster, and spellbook |
| `armory.webp` | `/shop`, White selected | Crop of the portrait and animation/effect inspectors |
| `progress-dashboard.webp` | `/design-preview/home?view=progress` | Full page |

To refresh, start the frontend in development mode, seed an isolated local API
with `python manage.py seed_all`, and use a demo account with a companion.
Launch adventures and challenges through the map; run IDs belong to the local
database. Dismiss briefing dialogs and first-use tours before capture. Preserve
the actual application UI and crop only for framing. Export as WebP at quality
88; keep UI text readable and verify every asset in the root README preview.
