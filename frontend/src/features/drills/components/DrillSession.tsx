import { useEffect, useEffectEvent, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Heart, Pause, Play, X } from 'lucide-react'

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

/** Flight collisions answer pick-one rounds; assembled answers become a walking path. */
export function DrillSession({ plan }: { plan: DrillPlan }) {
  const session = useDrillSession(plan)
  const [started, setStarted] = useState(false)
  const [paused, setPaused] = useState(false)
  const { ask, card, verdict, check, advance, answer } = session
  const exitPath = drillExitPath(plan)
  const rung = ask?.kind === 'card' ? ask.rung : null
  const options = useMemo(() => seededShuffle(choicePoolFor(card, rung), `${card?.key}:${rung}:${session.round}`), [card, rung, session.round])
  const optionCount = options.length
  const checkpoint = optionCount === 0
  const nextWave = useEffectEvent(advance)
  useEffect(() => {
    if (!verdict || session.finished || paused) return
    const timer = window.setTimeout(() => nextWave(), session.lives === 0 ? 1600 : verdict.correct ? 650 : 1000)
    return () => window.clearTimeout(timer)
  }, [verdict, session.finished, session.lives, paused])
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.defaultPrevented) return
      if (event.metaKey || event.ctrlKey || event.altKey) return
      const target = event.target
      if (target instanceof Element && target.closest('[role="dialog"]')) return
      const typing =
        target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement
      if (event.key === 'Escape') {
        event.preventDefault()
        if (!event.repeat && !session.finished) setPaused((current) => !current)
        return
      }
      if (session.finished) return
      if (paused) return
      if (event.repeat) {
        if (event.key === 'Enter') event.preventDefault()
        return
      }
      if (event.key === 'Enter' && !(target instanceof HTMLButtonElement) && !(target instanceof HTMLAnchorElement)) {
        event.preventDefault()
        if (verdict || checkpoint) return
        if (!started) document.querySelector<HTMLButtonElement>('.drill-flight-intro button')?.click()
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
  }, [checkpoint, paused, session.finished, started, verdict])

  const question = <DrillQuestion
    key={`question-${session.round}`}
    card={card} rung={rung} sequence={session.sequence} round={session.round}
    verdict={verdict} onAnswer={session.setAnswer}
    flightChoices={optionCount > 0}
    flightSelection={answer?.kind === 'choice' ? answer.value : null}
    checkpoint={checkpoint ? { onResolve: session.resolveCheckpoint, paused, onPauseChange: setPaused, showHud: false } : undefined}
  />

  return (
    <div className={`drill-screen drill-screen--flight ${session.finished ? 'drill-screen--results' : 'drill-screen--immersive'}`}>
      <header className="drill-header">
        <div className="drill-identity">
          <p className="drill-level">{session.finished ? 'GIT it!' : plan.level.title}</p>
          <div className="drill-screen-controls">
            {session.finished ? null : <>
              <div className="drill-flight-lives" role="status" aria-label={`${session.lives} of 3 lives remaining`}>
                {[0, 1, 2].map((index) => <Heart key={index} aria-hidden="true" data-lost={index >= session.lives || undefined} />)}
              </div>
              <button type="button" className="drill-screen-control" aria-label={`${paused ? 'Resume' : 'Pause'} ${checkpoint ? 'crossing' : 'flight'}`}
                title={paused ? 'Resume (Esc)' : 'Pause (Esc)'} onClick={() => setPaused((current) => !current)}>
                {paused ? <Play aria-hidden="true" /> : <Pause aria-hidden="true" />}
              </button>
            </>}
            <Link className="drill-screen-control" to={exitPath} aria-label="Leave the drill" title="Leave the drill"><X aria-hidden="true" /></Link>
          </div>
        </div>
        {session.finished ? null : <DrillProgressTrack segments={session.rail} />}
      </header>

      <main className="drill-stage">
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
            mistakes={session.mistakes}
            saveFailed={session.saveFailed}
            gameOver={session.gameOver}
            fell={session.fell}
            onRestart={() => { setStarted(false); setPaused(false); session.restart() }}
          />
        ) : (
          <div className="drill-flight-round" data-checkpoint={checkpoint || undefined}>
          {checkpoint ? question : <DrillFlightArena round={session.round}
            options={options} verdict={verdict} lives={session.lives} started={started}
            paused={paused} onPauseChange={setPaused}
            showHud={false}
            onStart={() => setStarted(true)} onCollide={session.collide} onMiss={session.miss}
            voice={rung === 'read' ? 'prose' : 'machine'}>{question}</DrillFlightArena>}
          </div>
        )}
      </main>

      {session.finished ? null : (
        <DrillVerdictBar
          verdict={verdict}
          canCheck={!checkpoint && answer !== null}
          optionCount={optionCount}
          onCheck={check}
          flightChoices={optionCount > 0}
          outOfLives={session.lives === 0}
          checkpoint={checkpoint}
          fell={session.fell}
        />
      )}
    </div>
  )
}
