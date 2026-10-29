import { Star } from 'lucide-react'
import { useId, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import type { LevelTourMode } from '@/shared/level/utils/levelTour'
import { GameplayWorkspaceTour } from './GameplayWorkspaceTour'
import { StarScoreChecklist } from './StarScoreChecklist'
import type { StarBreakdown } from './StarScoreChecklist'

import './star-rules.css'

/** Shared copy keeps onboarding and the on-demand reminder in agreement. */
export function StarRulesContent({ mode = 'tier' }: { mode?: LevelTourMode }) {
  return (
    <div className="star-rules">
      <dl>
        <div><dt>3 stars</dt><dd>Finish within the efficient command target.</dd></div>
        <div><dt>2 stars</dt><dd>Finish above the efficient target but within the generous target.</dd></div>
        <div><dt>1 star</dt><dd>Finish above the generous target but within the maximum allowance.</dd></div>
      </dl>
      <p>Each attempt is scored separately. Retries and restarts never reduce stars. Typos, failed commands, recovery and repeated Git actions count. Valid checks like <code>git status</code>, file edits and opening the command guide are free.</p>
      {mode === 'adventure' ? (
        <p>Clear every scenario; your lowest scenario score becomes your level score. Opening the command guide never costs a star.</p>
      ) : null}
      <p>Click the stars any time to see these rules again.</p>
    </div>
  )
}

export function StarRulesButton({ children, label, mode = 'tier', breakdown, active, savedStars, multiScenario }: {
  children: ReactNode
  label: string
  mode?: LevelTourMode
  breakdown?: StarBreakdown | null
  active?: boolean
  savedStars?: number
  multiScenario?: boolean
}) {
  const targetId = useId().replace(/:/g, '')
  const [open, setOpen] = useState(false)
  const steps = useMemo(() => [{
    id: 'star-rules',
    selector: `[data-star-rules="${targetId}"]`,
    icon: Star,
    title: 'How to earn stars',
    body: breakdown ? (
      <div className="star-rules">
        <StarScoreChecklist breakdown={breakdown} active={active} tier={mode === 'tier'} savedStars={savedStars} multiScenario={multiScenario} />
      </div>
    ) : <StarRulesContent mode={mode} />,
    placement: 'bottom' as const,
  }], [mode, targetId, breakdown, active, savedStars, multiScenario])

  return (
    <>
      <button
        type="button"
        className="star-rules-trigger"
        data-star-rules={targetId}
        aria-label={label}
        aria-haspopup="dialog"
        aria-expanded={open}
        title="How to earn stars"
        onClick={() => setOpen((current) => !current)}
      >
        {children}
      </button>
      {open ? (
        <GameplayWorkspaceTour
          label="Star rules"
          finishLabel="Got it"
          skipLabel="Close star rules"
          skipIconOnly
          showProgress={false}
          steps={steps}
          onClose={() => setOpen(false)}
        />
      ) : null}
    </>
  )
}
