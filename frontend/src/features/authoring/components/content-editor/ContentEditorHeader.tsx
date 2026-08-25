import { CheckCircle2, Rocket, Save } from 'lucide-react'

import type { ContentKind } from '@/features/authoring/types'
import { Button } from '@/shared/components/Button'

type ContentEditorHeaderProps = {
  kind: ContentKind
  title: string
  isNew: boolean
  busy: boolean
  isDirty: boolean
  canUseActions: boolean
  officialDestinationMissing: boolean
  onSave: () => void
  onValidate: () => void
  onPublish: () => void
}

export function ContentEditorHeader({
  kind,
  title,
  isNew,
  busy,
  isDirty,
  canUseActions,
  officialDestinationMissing,
  onSave,
  onValidate,
  onPublish,
}: ContentEditorHeaderProps) {
  return (
    <header className="author-page-head">
      <div>
        <p className="author-eyebrow">Content Manager · {kind}</p>
        <h1 className="author-page-title">{isNew ? `New ${kind}` : title}</h1>
      </div>
      <div className="author-actions">
        <span
          className="author-save-status"
          data-state={busy ? 'saving' : isDirty ? 'dirty' : 'saved'}
          role="status"
          aria-live="polite"
        >
          {busy ? 'Working…' : isDirty ? 'Unsaved changes' : 'Saved'}
        </span>
        <Button disabled={busy || officialDestinationMissing} size="sm" onClick={onSave}>
          <Save className="size-4" aria-hidden="true" /> Save
        </Button>
        <Button
          disabled={!canUseActions || busy || isDirty || officialDestinationMissing}
          variant="outline"
          size="sm"
          onClick={onValidate}
        >
          <CheckCircle2 className="size-4" aria-hidden="true" /> Validate
        </Button>
        <Button
          disabled={!canUseActions || busy || isDirty || officialDestinationMissing}
          variant="secondary"
          size="sm"
          onClick={onPublish}
        >
          <Rocket className="size-4" aria-hidden="true" /> Publish
        </Button>
      </div>
    </header>
  )
}
