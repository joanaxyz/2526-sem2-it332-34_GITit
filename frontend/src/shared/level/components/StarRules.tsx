import { Star } from 'lucide-react'
import { useId, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import type { LevelTourMode } from '@/shared/level/utils/levelTour'
import { GameplayWorkspaceTour } from './GameplayWorkspaceTour'

import './star-rules.css'

/** Shared copy keeps onboarding and the on-demand reminder in agreement. */
export function StarRulesContent({ mode = 'tier' }: { mode?: LevelTourMode }) {
  return (
    <div className="star-rules">
      <dl>
        <div><dt>3 stars</dt><dd>Finish within the Star target with no more than one retry.</dd></div>
        <div><dt>2 stars</dt><dd>Finish within the Star target after two or more retries.</dd></div>
        <div><dt>1 star</dt><dd>Finish using more commands than the Star target.</dd></div>
      </dl>
      <p>The Star target is your command goal. Commands that change the repository and invalid commands count. Valid checks like <code>git status</code> are free.</p>
      {mode === 'adventure' ? (
        <p>Clear every scenario; your lowest scenario score becomes your level score. Opening the command guide takes away one star, down to a minimum of 1.</p>
      ) : null}
      <p>Click the stars any time to see these rules again.</p>
    </div>
  )
}

export function StarRulesButton({ children, label, mode = 'tier' }: {
  children: ReactNode
  label: string
  mode?: LevelTourMode
}) {
  const targetId = useId().replace(/:/g, '')
  const [open, setOpen] = useState(false)
  const steps = useMemo(() => [{
    id: 'star-rules',
    selector: `[data-star-rules="${targetId}"]`,
    icon: Star,
    title: 'How to earn stars',
    body: <StarRulesContent mode={mode} />,
    placement: 'bottom' as const,
  }], [mode, targetId])

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
