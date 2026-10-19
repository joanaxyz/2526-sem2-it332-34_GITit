import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { X } from 'lucide-react'

import { DrillQuestion } from '@/features/drills/components/DrillQuestion'
import { DrillFlightArena } from '@/features/drills/components/DrillFlightArena'
import { DrillProgressTrack } from '@/features/drills/components/DrillProgressTrack'
import { DrillSummary } from '@/features/drills/components/DrillSummary'
import { DrillVerdictBar } from '@/features/drills/components/DrillVerdictBar'
import { useDrillSession } from '@/features/drills/hooks/useDrillSession'
import type { DrillPlan } from '@/features/drills/types'
import { choicePoolFor } from '@/features/drills/utils/drillChoices'
import { drillExitPath } from '@/features/drills/utils/drillRoutes'
import { seededShuffle } from '@/features/drills/utils/drillShuffle'

const CHOICE_KEYS = ['1', '2', '3', '4']

/** Flight collisions answer pick-one rounds; production rounds keep their assembly checkpoint. */
export function DrillSession({ plan }: { plan: DrillPlan }) {
  const navigate = useNavigate()
  const session = useDrillSession(plan)
  const [started, setStarted] = useState(false)
  const { ask, card, verdict, check, advance, answer } = session
  const exitPath = drillExitPath(plan)
  const rung = ask?.kind === 'card' ? ask.rung : null
  const options = useMemo(() => seededShuffle(choicePoolFor(card, rung), `${card?.key}:${rung}:${session.round}`), [card, rung, session.round])
  const optionCount = options.length
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.metaKey || event.ctrlKey || event.altKey) return
      const target = event.target
      const typing =
        target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement
      if (event.key === 'Escape') {
        navigate(exitPath)
        return
      }
      if (session.finished) return
      if (event.repeat) {
        if (event.key === 'Enter') event.preventDefault()
        return
      }
      if (event.key === 'Enter' && !(target instanceof HTMLButtonElement) && !(target instanceof HTMLAnchorElement)) {
        event.preventDefault()
        if (verdict) advance()
        else if (!started) document.querySelector<HTMLButtonElement>('.drill-flight-intro button')?.click()
        else if (!optionCount) check()
        return
      }
      if (typing) return
      if (CHOICE_KEYS.includes(event.key)) {
        const board = document.querySelector('.drill-flight-projectiles')
        const buttons = board?.querySelectorAll<HTMLButtonElement>('button:not(:disabled)')
        buttons?.[Number(event.key) - 1]?.click()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [advance, check, exitPath, navigate, optionCount, session.finished, started, verdict])

  return (
    <div className="drill-screen drill-screen--flight">
      {/* Identity and progress share one band. They were two, and the rail
          that sat below cost a whole row of a screen that cannot scroll -
          on a laptop that row came out of the question. */}
      <header className="drill-header">
        <div className="drill-identity">
          <p className="drill-wordmark">GIT it! <span>Flight Drill</span></p>
          {/* The summary titles itself with the level, so carrying it up
              here too would print the same string twice a hundred pixels
              apart. */}
          {session.finished ? null : (
            <p className="drill-level">
              {plan.level.chapter_number ? (
                <span className="drill-level-chapter">
                  Chapter {plan.level.chapter_number}
                  <span aria-hidden="true"> · </span>
                </span>
              ) : null}
              {plan.level.title}
            </p>
          )}
          <Link className="drill-exit" to={exitPath} aria-label="Leave the drill">
            <X aria-hidden="true" />
          </Link>
        </div>
        {session.finished ? null : <DrillProgressTrack segments={session.rail} />}
      </header>

      <main className="drill-stage">
        {/* Shown once, on arrival only: a part-filled track with no
            explanation reads as a bug the first time someone sees it. It
            sits in the question column so it lines up with the question it
            is explaining, and leaves on the first answer. */}
        {!session.finished && session.resumed && session.round === 0 ? (
          <p className="drill-resumed" role="status">
            Picked up where you left off.
          </p>
        ) : null}

        {session.finished ? (
          <DrillSummary
            plan={plan}
            rail={session.rail}
            accuracy={session.accuracy}
            answered={session.answered}
            shaky={session.shaky}
            saveFailed={session.saveFailed}
            gameOver={session.gameOver}
            onRestart={() => { setStarted(false); session.restart() }}
          />
        ) : (
          <div className="drill-flight-round">
          <DrillFlightArena round={session.round}
            options={options} verdict={verdict} lives={session.lives} started={started}
            onStart={() => setStarted(true)} onCollide={session.collide}
            voice={rung === 'read' ? 'prose' : 'machine'} />
          <DrillQuestion
            key={`question-${session.round}`}
            card={card}
            rung={rung}
            sequence={session.sequence}
            round={session.round}
            verdict={verdict}
            onAnswer={session.setAnswer}
            flightChoices={optionCount > 0}
            flightSelection={answer?.kind === 'choice' ? answer.value : null}
          />
          </div>
        )}
      </main>

      {session.finished ? null : (
        <DrillVerdictBar
          verdict={verdict}
          canCheck={answer !== null}
          card={card}
          rung={rung}
          sequence={session.sequence}
          optionCount={optionCount}
          onCheck={check}
          onContinue={advance}
          flightChoices={optionCount > 0}
          outOfLives={session.lives === 0}
        />
      )}
    </div>
  )
}
