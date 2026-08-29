import type { ContentKind } from '@/features/authoring/types'
import type { AuthoringForm } from '@/features/authoring/utils/authoringModel'

export type DraftState = { sourceKey: string; form: AuthoringForm }

export function sameForm(a: AuthoringForm, b: AuthoringForm): boolean {
  return JSON.stringify(a) === JSON.stringify(b)
}

export function newDraftSourceKey(
  kind: ContentKind,
  requestedOfficialMode: boolean,
  presetChapterId: number | null,
): string {
  const mode = requestedOfficialMode ? 'official' : 'authored'
  return `new:${kind}:${mode}:${presetChapterId ?? 'none'}`
}

export function reconcileSavedDraft(
  current: DraftState,
  submitted: DraftState,
  saved: DraftState,
): DraftState {
  if (current.sourceKey !== submitted.sourceKey) return saved
  return {
    sourceKey: saved.sourceKey,
    form: sameForm(current.form, submitted.form) ? saved.form : current.form,
  }
}

export function mergeCreatedChapter(
  current: DraftState,
  submitted: DraftState,
  chapterId: number,
): DraftState {
  const latest = current.sourceKey === submitted.sourceKey ? current : submitted
  return { ...latest, form: { ...latest.form, chapterId } }
}
