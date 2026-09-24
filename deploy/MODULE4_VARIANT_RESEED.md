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

## Tier changes in this release

Revert easy and rebase easy/medium keep their task shape. These three tiers now
ask for more, and their task text says so:

| Tier | Now asks the learner to | Task text | Star budget (`min_counted_commands`) | Command budget (`max_counted_commands`) |
|---|---|---|---|---|
| Revert medium | Find a faulty commit 2–3 below the pushed tip from its symptom (no commit ID given), revert it, push | Unchanged: "Identify the correct published change to roll back and synchronize the shared branch." | 2 (unchanged) | 10 (unchanged) |
| Revert hard | Revert two separate faulty commits, keep the good commit between them, push once | Was "Execute the required rollback while preserving shared history integrity across local and remote." Now "Roll back both faulty published changes, keep the good change between them, and publish once without rewriting shared history." | 2 → 3 (two reverts and a push) | 8 (unchanged) |
| Rebase hard | Recover a commit a teammate's rebase dropped (reset to the original tip from the reflog), then rebase all of it onto main | Was "Complete the full recovery sequence and validate branch integrity with all required checks." Now "A rebase dropped one of your commits: recover the original branch from the reflog, then rebase all of it onto main with a linear history." | 1 → 2 (reset and rebase) | 8 (unchanged) |

Rebase medium is unchanged in this release. Its planned "rebase stops on a
conflict" exercise needs simulator work (see the PR notes).

HLCR for SO 4.4 before and after this release measures different exercises.
Report the two periods separately.

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
need two clears. `re6`, `be6` and `bm6` keep the MVP repository; the medium and
hard revert tiers and the hard rebase tier are new exercises (see
"Tier changes" below). The variant key is the `case_id`, visible in Django admin
under *Adventure level tier wave variants*.

| Variant | Level / tier | Repository to expect | Correct | Wrong (must not complete) |
|---|---|---|---|---|
| re6 | Reversing Pushed Commits Safely / Easy | MVP config repo, tip "Unrelated follow-up" | `git revert c3`, `git push` | `git reset --hard c2`, `git push --force` |
| re7 | Reversing Pushed Commits Safely / Easy | Agency site, tip "Add promo banner to homepage" | `git revert c2`, `git push` | `git revert c2` without pushing |
| re8 | Reversing Pushed Commits Safely / Easy | Payments API, tip "Lower API timeout to 1s" | `git revert c4`, `git push` | `git reset --hard c3`, `git push --force` |
| rm6 | Reversing Pushed Commits Safely / Medium | Payroll: flat 30% withholding, bad commit 2 below the tip | `git log`, then `git revert c2`, `git push` | `git revert HEAD`, `git push` |
| rm7 | Reversing Pushed Commits Safely / Medium | Notifications: pushes every minute, bad commit 3 below the tip | `git log`, then `git revert c2`, `git push` | `git revert HEAD`, `git push` |
| rm8 | Reversing Pushed Commits Safely / Medium | Docs portal: results sorted by date, bad commit 3 below the tip | `git log`, then `git revert c1`, `git push` | `git revert HEAD`, `git push` |
| rh6 | Reversing Pushed Commits Safely / Hard | Shop: beta checkout for all (c1) and double coupons (c3), good email commit between | `git revert c3`, `git revert c1`, `git push` | `git revert c3`, `git push` (only one reverted) |
| rh7 | Reversing Pushed Commits Safely / Hard | Auth: 30-day sessions (c1) and 24-hour cache (c3), good audit commit between | `git revert c3`, `git revert c1`, `git push` | `git revert c1`, `git push` (only one reverted) |
| rh8 | Reversing Pushed Commits Safely / Hard | Public site: robots block (c2) and full-IP logging (c4), good pages around them | `git revert c4`, `git revert c2`, `git push` | `git reset --hard c1`, `git push --force` |
| be6 | Completing Rebase Recovery Sequences / Easy | MVP repo, branch `feature/recovery` | `git rebase main` | `git merge main` |
| be7 | Completing Rebase Recovery Sequences / Easy | `feature/search-filters` behind an app-shell update | `git rebase main` | `git merge main` |
| be8 | Completing Rebase Recovery Sequences / Easy | `feature/cli-flags` (3 commits) behind 2 main commits | `git rebase main` | `git merge main` |
| bm6 | Completing Rebase Recovery Sequences / Medium | MVP repo, branch `feature/recovery` | `git rebase main` | `git merge main` |
| bm7 | Completing Rebase Recovery Sequences / Medium | `feature/payment-retry` behind "Add refunds route" | `git rebase main` | `git merge main` |
| bm8 | Completing Rebase Recovery Sequences / Medium | `feature/i18n` (3 commits) behind 2 main commits | `git rebase main` | `git merge main` |
| bh6 | Completing Rebase Recovery Sequences / Hard | `feature/cli-flags` rebased by a teammate, "Parse --quiet flag" dropped | `git reflog`, `git reset --hard c4`, `git rebase main` | `git rebase main` (dropped commit stays lost) |
| bh7 | Completing Rebase Recovery Sequences / Hard | `hotfix/export-csv` rebased, "Test CSV export" dropped | `git reflog`, `git reset --hard c5`, `git rebase main` | `git reset --hard c5`, `git merge main` |
| bh8 | Completing Rebase Recovery Sequences / Hard | `feature/rate-limits` rebased, "Add rate limiter" dropped | `git reflog`, `git reset --hard c4`, `git rebase main` | `git rebase main` (dropped commit stays lost) |

For each variant, also confirm three things:
- the story text matches the repository shown;
- the "expected state" view shows the solved graph;
- the correct route stays within the tier's command budget (easy 12, medium
  10, hard 8).
