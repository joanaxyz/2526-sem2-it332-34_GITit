import type { ContentKind } from '@/features/authoring/types'
import { DEFAULT_BATTLE_STAGE } from '@/features/authoring/utils/authoring-model/options'
import type { AuthoredLevel, AuthoredProblem, AuthoredVariant, AuthoringForm, BookPage } from '@/features/authoring/utils/authoring-model/types'

export function emptyProblem(kind: ContentKind, index = 0): AuthoredProblem {
  return {
    slug: index === 0 ? 'wave-one' : `wave-${index + 1}`,
    title: index === 0 ? 'First problem' : `Problem ${index + 1}`,
    difficulty: kind === 'challenge' ? 'easy' : '',
    story: '',
    task: '',
    solutionCommands: ['git status'],
    initialStateText: '{}',
    evaluationMode: 'state_hash',
    minCountedCommands: 1,
    maxCountedCommands: 8,
    variants: [],
  }
}

export function emptyLevel(kind: ContentKind, index = 0): AuthoredLevel {
  return {
    slug: index === 0 ? 'level-one' : `level-${index + 1}`,
    title: index === 0 ? 'First level' : `Level ${index + 1}`,
    commandForms: [],
    problems: [emptyProblem(kind, 0)],
  }
}

export function emptyVariant(index: number): AuthoredVariant {
  return { slug: `case-${index + 1}`, label: `Case ${index + 1}`, initialStateText: '{}', solutionCommands: ['git status'] }
}

export function emptyPage(index = 0): BookPage {
  return { title: index === 0 ? 'Overview' : `Page ${index + 1}`, blocks: [{ type: 'paragraph', body: '' }] }
}

export function initialForm(kind: ContentKind): AuthoringForm {
  return {
    kind,
    slug: `new-${kind}`,
    title: `New ${kind}`,
    summary: '',
    commandFamily: kind === 'lesson' ? '' : 'git status',
    difficulty: kind === 'challenge' ? 'easy' : '',
    tags: [],
    visibility: 'private',
    chapterId: null,
    pages: kind === 'lesson' ? [emptyPage(0)] : [],
    levels: kind === 'lesson' ? [] : [emptyLevel(kind, 0)],
    battleStage: { ...DEFAULT_BATTLE_STAGE },
  }
}
