# Arcane Spire Story-Record Cutover

Replace the four-record story state with one canonical story by preserving the existing Runebound row and curriculum, renaming it to `arcane-spire` / `The Arcane Spire`, continuing to use Arcane visual assets, and deleting the obsolete modern Arcane, Frostbound, and Neon database trees.

Completion requires:

- the surviving record retains the former Runebound primary key and all Runebound child/progress identities;
- the surviving curriculum remains 5 chapters, 21 levels, and 63 tiers with unchanged authored content;
- the retired story records and runtime trees are absent;
- canonical seeding creates only the surviving story and cannot recreate or overwrite it with retired content;
- backend progress and frontend navigation/achievement behavior use `arcane-spire`;
- the Progress tab continues to expose only the 18 commands taught by the surviving curriculum;
- Arcane world assets continue to render via `world_slug="arcane-spire"`;
- targeted backend/frontend checks and the current database post-migration inventory pass.

Non-goals: rewriting Runebound content, deleting Arcane assets, rewriting simulator/runtime mechanics, removing shared command-library entries, or deleting historical authored fixture source that is no longer on a production seed path.
