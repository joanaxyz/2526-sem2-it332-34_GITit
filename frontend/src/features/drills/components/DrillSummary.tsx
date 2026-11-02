import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen, CircleAlert, CircleCheck, RotateCcw } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'

import { DrillProgressTrack } from '@/features/drills/components/DrillProgressTrack'
import type { DrillCard, DrillMistake, DrillPlan } from '@/features/drills/types'
import type { DrillRailSegment } from '@/features/drills/hooks/useDrillSession'
import { drillExitPath, drillPracticePath } from '@/features/drills/utils/drillRoutes'
import { ChapterBookModal } from '@/features/story-map/components/book/ChapterBookModal'

type SummaryView = 'review' | 'commands'

/** One result, two views: corrections to act on, or command references to read. */
export function DrillSummary({ plan, rail, accuracy, answered, shaky, mistakes = [], saveFailed,
  onRestart, gameOver = false, fell = false,
}: {
  plan: DrillPlan
  rail: DrillRailSegment[]
  accuracy: number
  answered: number
  shaky: string[]
  mistakes?: DrillMistake[]
  saveFailed: boolean
  onRestart: () => void
  gameOver?: boolean
  fell?: boolean
}) {
  const [guideCommand, setGuideCommand] = useState<string | null>(null)
  const [view, setView] = useState<SummaryView>(() => mistakes.length || shaky.length ? 'review' : 'commands')
  const sectionRef = useRef<HTMLElement>(null)
  const tabId = useId()
  useEffect(() => { sectionRef.current?.focus({ preventScroll: true }) }, [])
  const shakyKeys = new Set(shaky)
  const shakyCards = plan.cards.filter((card) => shakyKeys.has(card.key))
  const cardsByKey = new Map(plan.cards.map((card) => [card.key, card]))
  const practicePath = drillPracticePath(plan)
  const unfinished = rail.some((segment) => segment.kind === 'command' && !segment.mastered)
  const cleared = !gameOver && !fell && !unfinished
  const StateIcon = cleared ? CircleCheck : CircleAlert
  const lede = fell ? 'Blue fell through a gap. Review the commands before your next crossing.'
    : gameOver ? 'No lives left. Review your answers before the next flight.'
    : unfinished ? 'A few commands still need practice. Your next flight starts here.'
    : shakyCards.length ? 'Every command cleared. Revisit the ones that needed practice.'
    : 'Every command cleared on the first try. Ready for the next quest.'
  const tabs: { id: SummaryView; label: string; count: number }[] = [
    { id: 'review', label: 'Review mistakes', count: mistakes.length || shakyCards.length },
    { id: 'commands', label: 'Commands used', count: plan.cards.length },
  ]

  function practiceLink(command: string) {
    return <Link className="drill-practice-link" to={practicePath}
      aria-label={`Practice ${command} in ${plan.level.title}`} title={`Open ${plan.level.title}`}>
      Practice <ArrowRight aria-hidden="true" />
    </Link>
  }

  function commandReference(card: DrillCard) {
    const body = <>
      <span className="drill-command-copy"><code>{card.command}</code><span>{card.intent}</span></span>
      {plan.level.chapter_id ? <BookOpen className="drill-command-book" aria-hidden="true" /> : null}
    </>
    return plan.level.chapter_id ? <button type="button" className="drill-command-row"
      aria-label={`Open ${card.command} in the Field Guide`} title="Open Field Guide"
      onClick={() => setGuideCommand(card.base_command)}>{body}</button>
      : <div className="drill-command-row">{body}</div>
  }

  return <section ref={sectionRef} tabIndex={-1} className="drill-summary" aria-labelledby="drill-summary-title">
    <header className="drill-summary-heading">
      <p className="drill-summary-state" data-cleared={cleared}><StateIcon aria-hidden="true" />
        {fell ? 'Game over' : gameOver ? 'Out of lives' : cleared ? 'Drill cleared' : 'Drill over'}
      </p>
      <h2 id="drill-summary-title">{plan.level.title}</h2>
      <p className="drill-summary-lede">{lede}</p>
    </header>

    <div className="drill-summary-tally">
      <dl className="drill-summary-figures">
        <div><dt>Accuracy</dt><dd>{accuracy}%</dd></div>
        <div><dt>Answers</dt><dd>{answered}</dd></div>
      </dl>
      <DrillProgressTrack segments={rail} mode="record" />
    </div>

    <div className="drill-summary-tabs" role="tablist" aria-label="Drill results">
      {tabs.map((tab, index) => <button type="button" role="tab" key={tab.id}
        id={`${tabId}-${tab.id}-tab`} aria-controls={`${tabId}-${tab.id}-panel`}
        aria-selected={view === tab.id} tabIndex={view === tab.id ? 0 : -1}
        onClick={() => setView(tab.id)} onKeyDown={(event) => {
          const next = event.key === 'Home' ? 0 : event.key === 'End' ? 1
            : event.key === 'ArrowLeft' || event.key === 'ArrowRight' ? 1 - index : null
          if (next === null) return
          event.preventDefault()
          setView(tabs[next].id)
          document.getElementById(`${tabId}-${tabs[next].id}-tab`)?.focus()
        }}>
        {tab.label}<span aria-hidden="true">{tab.count}</span>
      </button>)}
    </div>

    <div role="tabpanel" id={`${tabId}-review-panel`} aria-labelledby={`${tabId}-review-tab`} hidden={view !== 'review'} tabIndex={0}>
      <section className="drill-summary-review" aria-label="Your flight review">
        {mistakes.length ? <ol>
          {mistakes.map((mistake) => {
            const card = mistake.cardKey ? cardsByKey.get(mistake.cardKey) : undefined
            return <li key={mistake.round}>
              <div className="drill-mistake-heading">
                <h4 data-voice={mistake.voice === 'prose' ? 'machine' : undefined}>{mistake.subject}</h4>
                {practiceLink(card?.command ?? mistake.subject)}
              </div>
              <dl>
                <div data-result="picked"><dt>Your answer</dt><dd>
                  <code data-voice={mistake.voice}>{mistake.picked || 'No answer selected'}</code>
                  {mistake.pickedGloss ? <span>{mistake.pickedGloss}</span> : null}
                </dd></div>
                <div data-result="expected"><dt>Correct answer</dt><dd>
                  <code data-voice={mistake.voice}>{mistake.expected}</code>
                  {mistake.expectedGloss ? <span>{mistake.expectedGloss}</span> : null}
                </dd></div>
              </dl>
            </li>
          })}
        </ol> : shakyCards.length ? <ul className="drill-command-list" aria-label="Worth another look">
          {shakyCards.map((card) => <li key={card.key}><div className="drill-command-row">
            <span className="drill-command-copy"><code>{card.command}</code><span>{card.intent}</span></span>
            {practiceLink(card.command)}
          </div></li>)}
        </ul> : <p className="drill-summary-clean"><CircleCheck aria-hidden="true" />No mistakes to review.</p>}
      </section>
    </div>

    <div role="tabpanel" id={`${tabId}-commands-panel`} aria-labelledby={`${tabId}-commands-tab`} hidden={view !== 'commands'} tabIndex={0}>
      <section className="drill-summary-commands" aria-label="Commands used in this drill">
        <ul className="drill-command-list">
          {plan.cards.map((card) => <li key={card.key}>{commandReference(card)}</li>)}
        </ul>
      </section>
    </div>

    {saveFailed ? <p className="drill-summary-warning" role="status">Your result could not be saved. The level map may still show this drill as unfinished.</p> : null}

    <footer className="drill-summary-actions">
      <Link className="ui-button ui-button--default" to={drillExitPath(plan)}>Back to the level map</Link>
      <button type="button" className="ui-button ui-button--ghost" onClick={onRestart}><RotateCcw aria-hidden="true" />Drill again</button>
    </footer>
    {guideCommand && plan.level.chapter_id ? <ChapterBookModal key={guideCommand}
      chapterId={plan.level.chapter_id} chapterTitle={plan.level.chapter_title}
      initialCommand={guideCommand} onClose={() => setGuideCommand(null)} /> : null}
  </section>
}
