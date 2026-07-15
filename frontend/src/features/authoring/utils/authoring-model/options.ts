import type { BattleStageConfig, Visibility } from '@/features/authoring/types'

export const VISIBILITIES: { id: Visibility; label: string }[] = [
  { id: 'private', label: 'Private (only you)' },
  { id: 'public', label: 'Public (shareable)' },
  { id: 'store', label: 'Store (listed)' },
]

export const DIFFICULTIES: { id: string; label: string }[] = [
  { id: '', label: 'Unset' },
  { id: 'easy', label: 'Easy' },
  { id: 'medium', label: 'Medium' },
  { id: 'hard', label: 'Hard' },
]

export const DEFAULT_BATTLE_STAGE: BattleStageConfig = {
  background: null,
  landing: null,
}

export const EVALUATION_MODES: { id: string; label: string }[] = [
  { id: 'state_hash', label: 'Reach the exact target repository state' },
  { id: 'commands', label: 'Run the expected commands' },
]

export const BLOCK_TYPES: { id: string; label: string }[] = [
  { id: 'paragraph', label: 'Paragraph' },
  { id: 'bullet_list', label: 'Bullet list (one item per line)' },
  { id: 'command', label: 'Command' },
  { id: 'code', label: 'Code' },
  { id: 'callout', label: 'Callout' },
  { id: 'warning', label: 'Warning' },
  { id: 'terminal_output', label: 'Terminal output' },
]
