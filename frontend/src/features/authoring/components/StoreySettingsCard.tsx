import { MonsterRosterField } from '@/features/authoring/components/MonsterRosterField'
import { useOwnedMonsters } from '@/features/authoring/components/useOwnedMonsters'
import type { AuthoringStorey, ContentKind } from '@/features/authoring/types'

type StoreyPatch = Partial<
  Pick<AuthoringStorey, 'title' | 'mob_roster' | 'boss_roster' | 'pass_bar_fraction'>
>

/**
 * Settings for the SELECTED storey, shared by every adventure/challenge/tome in
 * it: the monster rosters its battles draw from, and the mastery pass-bar that
 * unlocks the storey's Challenge.
 *
 * Note: GitCoin reward checkpoints are deliberately NOT authorable here. Coins
 * are reserved for the official tower; custom towers grant no coins, so there's
 * no checkpoint editor to set the player's expectations wrongly.
 */
export function StoreySettingsCard({
  kind,
  storey,
  onChange,
}: {
  kind: ContentKind
  storey: AuthoringStorey
  onChange: (patch: StoreyPatch) => void
}) {
  const { monsters } = useOwnedMonsters()

  return (
    <section className="author-card">
      <header className="author-card-head">
        <h2 className="author-card-title">Storey settings · {storey.title}</h2>
        <p className="author-card-sub">Shared by every adventure, challenge, and tome in this storey.</p>
      </header>

      <label className="author-field">
        <span className="author-label">Storey name</span>
        <input className="author-input" value={storey.title} onChange={(e) => onChange({ title: e.target.value })} />
      </label>

      <p className="author-hint author-coins-note">
        Custom towers don't grant GitCoins — progress reward chests are reserved for the official tower.
      </p>

      <MonsterRosterField
        label="Mob roster"
        hint="Encounters without a named monster pick from this pool."
        monsters={monsters}
        selected={storey.mob_roster ?? []}
        onChange={(mob_roster) => onChange({ mob_roster })}
      />

      <MonsterRosterField
        label="Boss roster"
        hint="Challenge bosses pick from this pool when none is named."
        monsters={monsters}
        selected={storey.boss_roster ?? []}
        onChange={(boss_roster) => onChange({ boss_roster })}
      />

      {kind === 'adventure' ? (
        <label className="author-field">
          <span className="author-label">Pass bar (unlocks the Challenge)</span>
          <span className="author-hint">Fraction of mastery (0–1) the player must reach.</span>
          <input
            className="author-input author-input--narrow"
            type="number"
            min={0.1}
            max={1}
            step={0.05}
            value={storey.pass_bar_fraction}
            onChange={(e) => onChange({ pass_bar_fraction: Number(e.target.value) })}
          />
        </label>
      ) : null}
    </section>
  )
}
