# Curriculum scenarios cutover (Render)

Ships the ordered-scenario curriculum (docs/goals/curriculum-waves-and-repetition/):

- Every adventure tier of Modules 1–4 becomes 2–3 designed scenarios, 132 in all.
- Each scenario plays once, in order.
- 84 new scenarios join the team's 265.
- Each module gets a Challenge Gate (3 trials × 2 variants).
- GitCoins are paid on every tier's first clear: Easy 25 / Medium 35 / Hard 50.

All four modules cut over in this one release. The plan allowed one deploy per
module; the content and checks are complete for all four, so they ship together.

## What changes

- **Schema migrations** run on startup (`DJANGO_MIGRATE_ON_STARTUP`, on by default):
  - `adventures 0013`: scenario progress and variant order.
  - `adventures 0014`, `0015`, `progress 0004` and `practice 0004`: drop the
    retired pre-tier adventure tables.
  - `adventures 0016`: drops `AdventureLevelTierScenario.required_successful_attempts`;
    a scenario is now always cleared once.
- **Curriculum data** comes from `seed_all`, reading the scenario plan
  (`backend/curriculum/seed_data/source/scenario_plan/`).
- **Old scenarios and variants stay.** Each tier's previous single scenario
  (`{level}-{difficulty}`) and its variant rows are unpublished, never deleted,
  because past runs reference them.
- **Completed tiers stay completed.** Their new scenarios are free play.
- **In-flight runs** on an old scenario can still be finished. A solve counts as
  clearing the learner's next uncleared scenario.
- **Free play changes.** Replaying a completed tier now cycles through its
  scenarios, instead of reopening the variant that completed it. Mention this to
  returning learners.

## Before you start

1. The release commit is merged to `main`, and Render has deployed it.
2. Choose a low-traffic window, ideally between KPI cohorts (decision D7). The
   seed runs for several minutes before the service binds its port.
3. Take a Supabase backup (**Supabase → Database → Backups**).
4. On a developer machine, point `backend/.env` at the production database
   (`DATABASE_URL`). The free plan has no shell or one-off jobs, so the
   one-time commands below run from there.
5. Record the cutover time in UTC. It is the KPI period boundary.

## Steps

1. **Seed.** In **Render → git-it-app → Environment**, set
   `DJANGO_SEED_ON_STARTUP=True` and save. This redeploys; if it does not, use
   **Manual Deploy → Deploy latest commit**.
2. **Wait for the logs**, in this order:
   - the migrations up to `adventures.0016_retire_required_successful_attempts`;
   - `seed_all complete — safely upserted official data.`;
   - Gunicorn's `Listening at: http://0.0.0.0:10000`.
3. **Turn the seed off.** Set `DJANGO_SEED_ON_STARTUP=False` and save, so later
   restarts do not reseed.
4. **Map partial progress onto the first scenarios** (decision D2). Learners who
   were part-way through a tier keep their place. No tier is completed for
   anyone.

   ```bash
   cd backend
   python manage.py map_partial_tier_progress --dry-run
   python manage.py map_partial_tier_progress
   ```

5. **Pay the reward ladder for earlier completions** (decision D1). It is
   idempotent: Easy keeps its old award key, so nobody is paid twice.

   ```bash
   python manage.py award_missing_tier_rewards --dry-run
   python manage.py award_missing_tier_rewards
   ```

6. **Re-reserve transfer cases.** The seed already refreshed every KPI command
   reference from the committed replay. Transfer reservations live on variant
   rows. The new scenarios are new rows, so
   re-reserve each transfer case with
   `python manage.py kpi_refs --cases <slug> --reserve --reason "<what differs>"`.
   The shared dev database had none on 2026-10-20.
7. **Check health.**

   ```bash
   export APP_URL=https://git-it-app-czpy.onrender.com
   curl --fail --show-error "$APP_URL/api/health/live/"
   curl --fail --show-error "$APP_URL/api/health/ready/"
   ```

Running steps 4 and 5 a second time changes nothing. After this deploy, delete
both commands (`map_partial_tier_progress`, `award_missing_tier_rewards`) and
their tests.

## If the deploy times out while seeding

Each seed command runs in a transaction, so a killed container rolls back the
step it was in. Set `DJANGO_SEED_ON_STARTUP=False` so the service can start,
then run the checks below. Re-running the seed is safe: every step is an
upsert.

## Verify

Run these read-only queries in **Supabase → SQL Editor**.

**1. Exactly the planned scenarios are published.** Expect `132` scenarios and `349`
variants.

```sql
select count(distinct w.id) as scenarios, count(v.id) as variants
from adventures_adventureleveltierscenario w
join adventures_adventureleveltierscenariovariant v on v.scenario_id = w.id and v.is_published
join adventures_adventureleveltier t on t.id = w.tier_id
join adventures_adventurelevel l on l.id = t.adventure_level_id
join curriculum_chapter c on c.id = l.chapter_id
join curriculum_story s on s.id = c.story_id
where s.slug = 'arcane-spire' and w.is_published;
```

**2. The old single scenarios are unpublished.** Expect `0`.

```sql
select count(*)
from adventures_adventureleveltierscenario w
join adventures_adventureleveltier t on t.id = w.tier_id
join adventures_adventurelevel l on l.id = t.adventure_level_id
where w.is_published and w.slug = l.slug || '-' || t.difficulty;
```

**3. Every published variant has a target state.** Expect `0`.

```sql
select count(*)
from adventures_adventureleveltierscenariovariant v
join adventures_adventureleveltierscenario w on w.id = v.scenario_id
where v.is_published and w.is_published and v.target_state = '{}'::jsonb;
```

**4. Each module has its gate.** Expect 12 rows, each with 2 variants.

```sql
select cl.slug, tr.difficulty, count(tv.id) as variants
from challenges_challengelevel cl
join challenges_challengetrial tr on tr.challenge_level_id = cl.id
join challenges_challengetrialvariant tv on tv.trial_id = tr.id and tv.is_published
where cl.slug like 'module-%-challenge-gate'
group by cl.slug, tr.difficulty
order by cl.slug, tr.difficulty;
```

**5. In the app**, as a disposable learner who has not played Module 2:

1. Open **Pushing to a Remote → Easy**. The header shows scenario 1 of 2,
   "Publish a branch", with the `git push` guide.
2. Clear it. The outcome reads "Scenario 1 of 2 cleared — next: Publish and
   track".
3. Scenario 2 shows the `git push -u` guide.
4. Clearing it shows "+25 GitCoins".

## KPI periods

Report KPIs before and after the cutover time separately, following
`MODULE4_VARIANT_RESEED.md`. Runs on an old scenario name it by
`{level}-{difficulty}`; runs on the new scenarios name a designed scenario slug. To split
any run query by period:

```sql
select r.id, w.slug as scenario, (w.slug = l.slug || '-' || t.difficulty) as before_cutover
from adventures_adventureleveltierrun r
join adventures_adventureleveltierscenario w on w.id = r.current_scenario_id
join adventures_adventureleveltier t on t.id = r.tier_id
join adventures_adventurelevel l on l.id = t.adventure_level_id;
```

Each learner's no-fail path now has 132 runs instead of 137, and about 4.9 h
instead of 4.7 h.

## Roll back

Roll back only from the Supabase backup. Migrations `adventures 0014`–`0016`,
`progress 0004` and `practice 0004` drop tables and a column, and reverting the
code does not recreate them. A redeploy of the previous commit alone does not
match the dropped schema.
