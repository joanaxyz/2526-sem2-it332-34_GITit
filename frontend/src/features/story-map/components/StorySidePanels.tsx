import { useMemo, useState } from 'react'
import { Sparkles } from 'lucide-react'

import type { AdventureLevelSummary } from '@/features/story-map/types'
import { GamePanel } from '@/shared/components/GamePanel'
import { companionSkillPortrait, primarySkillCommand } from '@/shared/cosmetics/skillPortrait'
import type { CompanionDef } from '@/shared/cosmetics/types'
import { GitCommandIcon } from '@/shared/git/commandCatalog/commandIcons'
import { useRank } from '@/shared/progress/rank'

type NextSkill = {
  level: AdventureLevelSummary
  levelNumber: number
  command: string
}

/* The next spell the player earns: the primary command of the first level
   they have not cleared - the honest answer to "which skill, at what level?".
   Null once every level in the chapter is done. */
function nextSkillReward(levels: AdventureLevelSummary[]): NextSkill | null {
  const index = levels.findIndex((level) => !level.is_passed)
  if (index === -1) return null
  const level = levels[index]
  return { level, levelNumber: index + 1, command: primarySkillCommand(level.command) }
}

/* The companion's spell portrait for a command. The `portrait/<command>.png`
   art is populated per companion; fall back to the command glyph until it is. */
function SkillPortrait({ src, command }: { src: string; command: string }) {
  const [failed, setFailed] = useState(false)
  return (
    <span className="story-skill-portrait" aria-hidden="true">
      {failed ? (
        <GitCommandIcon command={command} className="story-skill-portrait-glyph" />
      ) : (
        <img src={src} alt="" onError={() => setFailed(true)} />
      )}
    </span>
  )
}

export function StorySkillFocusPanel({
  levels,
  companionSlug,
  companionLabel,
  loading,
}: {
  levels: AdventureLevelSummary[]
  companionSlug: string
  companionLabel: string
  loading: boolean
}) {
  const next = useMemo(() => nextSkillReward(levels), [levels])

  return (
    <GamePanel as="section" eyebrow="Skill Reward" className="story-skill-reward-detail-panel">
      {loading ? (
        <p className="story-skill-empty">Reading the next spell…</p>
      ) : !next ? (
        <div className="story-skill-reward story-skill-reward--done">
          <span className="story-skill-portrait story-skill-portrait--done" aria-hidden="true">
            <Sparkles />
          </span>
          <div className="story-skill-reward-copy">
            <strong className="story-skill-reward-name">Every spell inscribed</strong>
            <span className="story-skill-reward-level">Chapter mastered</span>
            <p className="story-skill-reward-desc">
              You have inscribed every command in this chapter into {companionLabel}'s Spellbook.
            </p>
          </div>
        </div>
      ) : (
        <div className="story-skill-reward">
          <SkillPortrait src={companionSkillPortrait(companionSlug, next.command)} command={next.command} />
          <div className="story-skill-reward-copy">
            <code className="story-skill-reward-name">{next.command}</code>
            <span className="story-skill-reward-level">Level {next.levelNumber} Skill Reward</span>
            <p className="story-skill-reward-desc">
              Clear <strong>{next.level.title}</strong> to inscribe {companionLabel}'s{' '}
              <code>{next.command}</code> spell.
            </p>
          </div>
        </div>
      )}
    </GamePanel>
  )
}

export function StoryCompanionPanel({ companion }: { companion: CompanionDef }) {
  const rank = useRank()
  const portrait = companion.sprites.portrait?.src ?? companion.sprites.idle?.src ?? ''
  return (
    <GamePanel as="section" eyebrow={companion.label} title="Your Companion" className="story-companion-panel">
      <div className="story-companion-body">
        <div className="story-companion-copy">
          <dl>
            <div>
              <dt>Rank</dt>
              <dd>{rank ? `${rank.tier.numeral} · ${rank.tier.name}` : '—'}</dd>
            </div>
            <div>
              <dt>Next Rank</dt>
              <dd>{rank ? (rank.nextTier ? `${Math.round(rank.ratingInTier)} / ${Math.round(rank.ratingForNext)} XP` : 'Max rank') : '—'}</dd>
            </div>
          </dl>
        </div>
      </div>
      <img className="story-companion-portrait" src={portrait} alt="" />
    </GamePanel>
  )
}
