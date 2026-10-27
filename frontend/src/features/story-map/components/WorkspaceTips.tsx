import { BookOpen, Lightbulb, X } from 'lucide-react'

import type { GuideElsewhere, Tip } from '@/features/story-map/api/commandIntroductionsApi'
import { Button } from '@/shared/components/Button'

/**
 * Quiet notes beside the workspace, apart from the command guide.
 *
 * A command whose guide lives in another scenario gets a note saying where it
 * is taught, with its guide to read. Tips explain techniques and new words
 * wherever they first come up, one at a time, until dismissed. Neither blocks
 * the terminal, and both stay readable while a guide is open.
 */
export function WorkspaceTips({ tips, elsewhere, onDismissTip, onReadGuide, onHideElsewhere }: {
  tips: readonly Tip[]
  elsewhere: GuideElsewhere | null
  onDismissTip: (key: string) => void
  onReadGuide: (teachingKey: string) => void
  onHideElsewhere: () => void
}) {
  const [tip] = tips
  if (!tip && !elsewhere) return null

  return (
    <aside className="workspace-tips" data-tour-target="workspace-tips" aria-label="Tips">
      {elsewhere ? (
        <section className="workspace-tip" aria-label="Taught in another scenario">
          <header className="workspace-tip__header">
            <span className="workspace-tip__eyebrow">
              <BookOpen aria-hidden="true" />
              Taught in Chapter {elsewhere.home.chapter_number}
            </span>
            <button type="button" className="workspace-tip__close" aria-label="Hide note" onClick={onHideElsewhere}>
              <X aria-hidden="true" />
            </button>
          </header>
          <code className="workspace-tip__syntax">{elsewhere.guide.command_form.usage_form}</code>
          <p className="workspace-tip__text">
            {elsewhere.home.level_title} · <span className="workspace-tip__difficulty">{elsewhere.home.difficulty}</span>
            {elsewhere.home.scenario_title ? ` · ${elsewhere.home.scenario_title}` : null}
          </p>
          <div className="workspace-tip__actions">
            <Button type="button" size="sm" variant="outline" onClick={() => onReadGuide(elsewhere.guide.teaching_key)}>
              Read guide
            </Button>
          </div>
        </section>
      ) : null}
      {tip ? (
        <section key={tip.key} className="workspace-tip" aria-live="polite" aria-label={`Tip: ${tip.title}`}>
          <header className="workspace-tip__header">
            <span className="workspace-tip__eyebrow">
              <Lightbulb aria-hidden="true" />
              Tip
            </span>
            {tips.length > 1 ? <span className="workspace-tip__count">{tips.length - 1} more</span> : null}
          </header>
          <h3 className="workspace-tip__title">{tip.title}</h3>
          <p className="workspace-tip__text">{tip.text}</p>
          {tip.syntax ? <code className="workspace-tip__syntax">{tip.syntax}</code> : null}
          <div className="workspace-tip__actions">
            <Button type="button" size="sm" variant="ghost" onClick={() => onDismissTip(tip.key)}>
              Got it
            </Button>
          </div>
        </section>
      ) : null}
    </aside>
  )
}
