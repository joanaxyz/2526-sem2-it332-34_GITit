import type { Recovery } from './tutorRecovery'
import { findOfflineFaq } from './offlineFaqs'
import { TutorMarkdown } from './TutorMarkdown'

export function TutorRecoveryPanel({ recovery, remaining, pending, draft, history, onRetry, onFaqs }: {
  recovery: Recovery | null
  remaining: number
  pending: boolean
  draft: string
  history: readonly { role: string; text: string }[]
  onRetry: () => void
  onFaqs: () => void
}) {
  if (!recovery) return null
  const saved = findOfflineFaq(draft, history)
  return <section className="tutor-chat__recovery app-scrollbar" aria-label="Chat recovery" data-tutor-selectable>
    <p role="status">{recovery.message}</p>
    <div className="tutor-chat__recovery-actions">
      {recovery.canRetry ? <button type="button" className="tutor-chat__reset" aria-label="Retry question"
        disabled={pending || remaining > 0 || !draft.trim() || recovery.reason === 'offline'} onClick={onRetry}>
        <span aria-hidden="true">{remaining > 0 ? `Retry in ${remaining}s` : 'Retry'}</span>
      </button> : null}
      <button type="button" className="tutor-chat__reset" onClick={onFaqs}>Browse FAQS</button>
    </div>
    {saved && recovery.canRetry ? <details className="tutor-chat__saved">
      <summary>Saved explanation: {saved.question}</summary>
      <TutorMarkdown text={saved.answer} />
    </details> : null}
  </section>
}
