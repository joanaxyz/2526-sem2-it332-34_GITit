# Module 4 variant re-seed (Render)

Publishes the new Module 4 revert and rebase variants (`re6`–`re8`, `rm6`–`rm8`,
`rh6`–`rh8`, `be6`–`be8`, `bm6`–`bm8`, `bh6`–`bh8`) and unpublishes the retired
duplicates (`re1`–`re5`, `rm1`–`rm5`, `rh1`–`rh5`, `be1`–`be5`, `bm1`–`bm5`,
`bh1`–`bh5`).

- **No schema migration.** Only curriculum data changes.
- **Retired rows stay in the database.** Run records reference them, so past
  runs and replays still resolve to the content that was played. In-progress
  runs on a retired variant can be finished normally.
- **Target states come from `backend/tier_targets.json`.** `seed_legacy_modules`
  now writes each variant's `target_state` from that file. Before this change a
  re-seed blanked every tier target state and needed a manual
  `backfill_tier_target_states --import`. That manual step is no longer needed.

The `git-it-app` service is on Render's free plan, which has no pre-deploy
commands, one-off jobs, or shell. Seeding therefore runs through
`DJANGO_SEED_ON_STARTUP`, which makes `deploy/render-api/start.sh` run
`python manage.py seed_all` before Gunicorn starts.

## Before you start

1. The commit that contains this change is merged to `main`, and Render has
   deployed it. Check the latest event under **git-it-app → Events**.
2. Pick a low-traffic window. The seed runs for several minutes before the
   service binds its port.
3. Optional: take a Supabase backup (**Supabase → Database → Backups**).

## Steps

1. **Enable the seed.** Go to **Render → git-it-app → Environment**, set
   `DJANGO_SEED_ON_STARTUP` to `True`, and save. Saving an environment variable
   triggers a redeploy. If it does not, use
   **Manual Deploy → Deploy latest commit**.
2. **Watch the deploy logs.** Wait for all of these lines in order:
   - `2/4 Runebound Turret`
   - `seed_all complete — safely upserted official data.`
   - Gunicorn's `Listening at: http://0.0.0.0:10000`
3. **Turn the seed back off.** Set `DJANGO_SEED_ON_STARTUP` to `False`, save,
   and let the service redeploy. Every later restart would otherwise re-seed
   and risk the port-binding timeout.
4. **Check health.**

   ```bash
   export APP_URL=https://git-it-app-czpy.onrender.com
   curl --fail --show-error "$APP_URL/api/health/live/"
   curl --fail --show-error "$APP_URL/api/health/ready/"
   ```

## If the deploy times out while seeding

Render fails the deploy if the port is not bound in time. Each seed command
runs in a transaction, so a killed container rolls back the step it was in.
Set `DJANGO_SEED_ON_STARTUP=False` so the service can start again, then run the
verification queries below to see which step landed. Re-running the seed is
safe: every step is an upsert.

## Verify

Run these read-only queries in **Supabase → SQL Editor**.

**1. New variants are published and have target states.** Expect 18 rows, all
with `is_published = true` and `blank_target = false`.

```sql
select l.slug as level, t.difficulty, v.slug as variant, v.is_published,
       v.target_state = '{}'::jsonb as blank_target
from adventures_adventureleveltierwavevariant v
join adventures_adventureleveltierwave w on w.id = v.wave_id
join adventures_adventureleveltier t on t.id = w.tier_id
join adventures_adventurelevel l on l.id = t.adventure_level_id
where v.slug ~ '^(re|rm|rh|be|bm|bh)[678]$'
order by l.slug, t.difficulty, v.slug;
```

**2. Retired duplicates are unpublished.** Expect 30 rows, all with
`is_published = false`.

```sql
select v.slug, v.is_published
from adventures_adventureleveltierwavevariant v
where v.slug ~ '^(re|rm|rh|be|bm|bh)[1-5]$'
order by v.slug;
```

**3. No legacy variant lost its target state.** Expect `0`.

```sql
select count(*)
from adventures_adventureleveltierwavevariant v
join adventures_adventureleveltierwave w on w.id = v.wave_id
join adventures_adventureleveltier t on t.id = w.tier_id
join adventures_adventurelevel l on l.id = t.adventure_level_id
join curriculum_chapter c on c.id = l.chapter_id
join curriculum_story s on s.id = c.story_id
where s.slug = 'git-it-legacy' and v.target_state = '{}'::jsonb;
```

**4. In the app.** As a learner who has not played Module 4, open
**Reversing Pushed Commits Safely → Easy**. The first variant must be the
original repository (label "Revert c3 safely", commits "Initial commit" →
"Unrelated follow-up"). Fail it on purpose, for example with `git revert c2`
then `git push`, and retry. The retry must show a different repository.

## Roll back

Revert the commit on `main` and let Render redeploy. A redeploy alone changes
no data. A re-seed after the revert would republish `…1`–`…5`, but it would also
leave `…6`–`…8` published, because the reverted seed does not know about them.
Restore the previous published set directly instead:

```sql
update adventures_adventureleveltierwavevariant
set is_published = (slug ~ '^(re|rm|rh|be|bm|bh)[1-5]$')
where slug ~ '^(re|rm|rh|be|bm|bh)[1-8]$';
```

## Play-test checklist

Run these locally before release. Use a learner account, open the level and
tier, and check that each variant:

- completes with its correct solution;
- does **not** complete with the wrong attempt listed.

On a first attempt you get the `…6` variant. To reach `…7` and `…8`, fail and
press **Retry**, or clear the tier and press **Continue** on easy tiers, which
need two clears. The variant key is the `case_id`, visible in Django admin
under *Adventure level tier wave variants*.

| Variant | Level / tier | Repository to expect | Correct | Wrong (must not complete) |
|---|---|---|---|---|
| re6 | Reversing Pushed Commits Safely / Easy | MVP config repo, tip "Unrelated follow-up" | `git revert c3`, `git push` | `git reset --hard c2`, `git push --force` |
| re7 | Reversing Pushed Commits Safely / Easy | Agency site, tip "Add promo banner to homepage" | `git revert c2`, `git push` | `git revert c2` without pushing |
| re8 | Reversing Pushed Commits Safely / Easy | Payments API, tip "Lower API timeout to 1s" | `git revert c4`, `git push` | `git reset --hard c3`, `git push --force` |
| rm6 | Reversing Pushed Commits Safely / Medium | MVP config repo, bad "Risky config change" | `git revert c2`, `git push` | `git revert c3`, `git push` |
| rm7 | Reversing Pushed Commits Safely / Medium | Billing, bad "Round invoice totals to whole units" | `git revert c2`, `git push` | `git revert c3`, `git push` |
| rm8 | Reversing Pushed Commits Safely / Medium | Storefront, bad "Switch brand color to neon" | `git revert c3`, `git push` | `git revert c4`, `git push` |
| rh6 | Reversing Pushed Commits Safely / Hard | MVP config repo, bad "Risky config change" | `git revert c2`, `git push` | `git revert c3`, `git push` |
| rh7 | Reversing Pushed Commits Safely / Hard | Auth service, bad "Cache sessions for 24 hours" | `git revert c2`, `git push` | `git revert c3`, `git push` |
| rh8 | Reversing Pushed Commits Safely / Hard | Shop, bad "Enable beta checkout for all users" | `git revert c3`, `git push` | `git reset --hard c2`, `git push --force` |
| be6 | Completing Rebase Recovery Sequences / Easy | MVP repo, branch `feature/recovery` | `git rebase main` | `git merge main` |
| be7 | Completing Rebase Recovery Sequences / Easy | `feature/search-filters` behind an app-shell update | `git rebase main` | `git merge main` |
| be8 | Completing Rebase Recovery Sequences / Easy | `feature/cli-flags` (3 commits) behind 2 main commits | `git rebase main` | `git merge main` |
| bm6 | Completing Rebase Recovery Sequences / Medium | MVP repo, branch `feature/recovery` | `git rebase main` | `git merge main` |
| bm7 | Completing Rebase Recovery Sequences / Medium | `feature/payment-retry` behind "Add refunds route" | `git rebase main` | `git merge main` |
| bm8 | Completing Rebase Recovery Sequences / Medium | `feature/i18n` (3 commits) behind 2 main commits | `git rebase main` | `git merge main` |
| bh6 | Completing Rebase Recovery Sequences / Hard | MVP repo, branch `feature/recovery` | `git rebase main` | `git merge main` |
| bh7 | Completing Rebase Recovery Sequences / Hard | `hotfix/export-csv` behind 2 main commits | `git rebase main` | `git merge main` |
| bh8 | Completing Rebase Recovery Sequences / Hard | `feature/rate-limits` (3 commits) behind 1 main commit | `git rebase main` | `git merge main` |

For each variant, also confirm three things:
- the story text matches the repository shown;
- the "expected state" view shows the solved graph;
- the correct route stays within the tier's command budget (easy 12, medium
  10, hard 8).
