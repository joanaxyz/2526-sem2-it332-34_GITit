/**
 * Structured form model for content authoring, plus (de)serialization to the
 * `definition` JSON the backend validates/compiles. The structured editors edit
 * this model; only `initial_state` stays as guided JSON text (repository state
 * is too rich for a simple form), everything else is real fields.
 */
import type { ContentKind } from '@/features/authoring/types'

export type ChestReward = { threshold: number; coins: number }
export type EncounterRow = { species: string; hp: number; tier?: string }
export type BossSpec = { species: string; hp: number }

export type AuthoredVariant = {
  slug: string
  label: string
  initialStateText: string
  solutionCommands: string[]
}

export type AuthoredLevel = {
  slug: string
  title: string
  difficulty: string
  solutionCommands: string[]
  initialStateText: string
  evaluationMode: string
  requiredSuccessfulAttempts: number
  minCountedCommands: number
  maxCountedCommands: number
  encounterSpec: EncounterRow[]
  bossSpec: BossSpec | null
  variants: AuthoredVariant[]
}

export type BookBlock = { type: string; body: string }
export type BookPage = { title: string; blocks: BookBlock[] }

export type AuthoringForm = {
  kind: ContentKind
  slug: string
  title: string
  summary: string
  commandFamily: string
  difficulty: string
  storeyId: number | null
  // tome
  pages: BookPage[]
  // playable
  levels: AuthoredLevel[]
}

export const EVALUATION_MODES: { id: string; label: string }[] = [
  { id: 'state_hash', label: 'Reach the exact target repository state' },
  { id: 'commands', label: 'Run the expected commands' },
]

export const DEFAULT_CHEST_REWARDS: ChestReward[] = [
  { threshold: 25, coins: 25 },
  { threshold: 50, coins: 60 },
  { threshold: 75, coins: 100 },
  { threshold: 100, coins: 150 },
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

export function emptyLevel(kind: ContentKind, index = 0): AuthoredLevel {
  return {
    slug: index === 0 ? 'level-one' : `level-${index + 1}`,
    title: index === 0 ? 'First level' : `Level ${index + 1}`,
    difficulty: kind === 'challenge' ? 'easy' : '',
    solutionCommands: ['git status'],
    initialStateText: '{}',
    evaluationMode: 'state_hash',
    requiredSuccessfulAttempts: 1,
    minCountedCommands: 1,
    maxCountedCommands: 8,
    encounterSpec: [],
    bossSpec: null,
    variants: [],
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
    commandFamily: kind === 'tome' ? '' : 'git status',
    difficulty: kind === 'challenge' ? 'easy' : '',
    storeyId: null,
    pages: kind === 'tome' ? [emptyPage(0)] : [],
    levels: kind === 'tome' ? [] : [emptyLevel(kind, 0)],
  }
}

// --- serialization ------------------------------------------------------------

class DefinitionError extends Error {}

function parseJsonObject(text: string, label: string): Record<string, unknown> {
  const trimmed = (text || '').trim()
  if (!trimmed) return {}
  let parsed: unknown
  try {
    parsed = JSON.parse(trimmed)
  } catch {
    throw new DefinitionError(`${label} is not valid JSON.`)
  }
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    throw new DefinitionError(`${label} must be a JSON object.`)
  }
  return parsed as Record<string, unknown>
}

function levelToDefinition(level: AuthoredLevel, kind: ContentKind): Record<string, unknown> {
  const out: Record<string, unknown> = {
    slug: level.slug,
    title: level.title,
    solution_commands: level.solutionCommands.filter((c) => c.trim()),
    initial_state: parseJsonObject(level.initialStateText, `Level "${level.slug}" initial state`),
    evaluation_spec: { completion_policy: { mode: level.evaluationMode } },
    required_successful_attempts: level.requiredSuccessfulAttempts,
    command_budget: {
      min_counted_commands: level.minCountedCommands,
      max_counted_commands: level.maxCountedCommands,
    },
  }
  if (kind === 'challenge' && level.difficulty) out.difficulty = level.difficulty
  if (level.encounterSpec.length) {
    out.encounter_spec = level.encounterSpec.map((row) => ({
      species: row.species,
      hp: row.hp,
      ...(row.tier ? { tier: row.tier } : {}),
    }))
  }
  if (level.bossSpec?.species) out.boss_spec = { species: level.bossSpec.species, hp: level.bossSpec.hp }
  if (level.variants.length) {
    out.variants = level.variants.map((variant) => ({
      slug: variant.slug,
      label: variant.label,
      initial_state: parseJsonObject(variant.initialStateText, `Variant "${variant.slug}" initial state`),
      solution_commands: variant.solutionCommands.filter((c) => c.trim()),
    }))
  }
  return out
}

/**
 * Build the `definition` payload, throwing a friendly error on bad JSON.
 * Reward checkpoints / rosters / pass-bar live on the storey now, not here.
 */
export function formToDefinition(form: AuthoringForm): Record<string, unknown> {
  if (form.kind === 'tome') {
    return {
      pages: form.pages.map((page) => ({
        title: page.title,
        blocks: page.blocks.map((block) => blockToDefinition(block)),
      })),
    }
  }
  return { levels: form.levels.map((level) => levelToDefinition(level, form.kind)) }
}

function blockToDefinition(block: BookBlock): Record<string, unknown> {
  if (block.type === 'bullet_list') {
    return { type: 'bullet_list', items: block.body.split('\n').map((s) => s.trim()).filter(Boolean) }
  }
  return { type: block.type, body: block.body }
}

export function definitionErrorMessage(error: unknown): string | null {
  return error instanceof DefinitionError ? error.message : null
}

export function isDefinitionError(error: unknown): boolean {
  return error instanceof DefinitionError
}

// --- deserialization (existing content -> form) -------------------------------

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : []
}

function levelFromDefinition(raw: Record<string, unknown>, kind: ContentKind, index: number): AuthoredLevel {
  const budget = (raw.command_budget as Record<string, unknown>) || {}
  const evaluation = (raw.evaluation_spec as Record<string, unknown>) || {}
  const policy = (evaluation.completion_policy as Record<string, unknown>) || {}
  return {
    slug: String(raw.slug ?? `level-${index + 1}`),
    title: String(raw.title ?? `Level ${index + 1}`),
    difficulty: String(raw.difficulty ?? (kind === 'challenge' ? 'easy' : '')),
    solutionCommands: asArray(raw.solution_commands).map(String),
    initialStateText: JSON.stringify(raw.initial_state ?? {}, null, 2),
    evaluationMode: String(policy.mode ?? 'state_hash'),
    requiredSuccessfulAttempts: Number(raw.required_successful_attempts ?? 1),
    minCountedCommands: Number(budget.min_counted_commands ?? raw.min_counted_commands ?? 1),
    maxCountedCommands: Number(budget.max_counted_commands ?? raw.max_counted_commands ?? 8),
    encounterSpec: asArray(raw.encounter_spec).map((row) => {
      const r = row as Record<string, unknown>
      return { species: String(r.species ?? ''), hp: Number(r.hp ?? 1), tier: r.tier ? String(r.tier) : undefined }
    }),
    bossSpec:
      raw.boss_spec && (raw.boss_spec as Record<string, unknown>).species
        ? {
            species: String((raw.boss_spec as Record<string, unknown>).species),
            hp: Number((raw.boss_spec as Record<string, unknown>).hp ?? 1),
          }
        : null,
    variants: asArray(raw.variants).map((v, i) => {
      const r = v as Record<string, unknown>
      return {
        slug: String(r.slug ?? `case-${i + 1}`),
        label: String(r.label ?? `Case ${i + 1}`),
        initialStateText: JSON.stringify(r.initial_state ?? {}, null, 2),
        solutionCommands: asArray(r.solution_commands).map(String),
      }
    }),
  }
}

function blockFromDefinition(raw: Record<string, unknown>): BookBlock {
  if (raw.type === 'bullet_list') {
    return { type: 'bullet_list', body: asArray(raw.items).map(String).join('\n') }
  }
  return { type: String(raw.type ?? 'paragraph'), body: String(raw.body ?? '') }
}

export function formFromContent(content: {
  kind: ContentKind
  slug: string
  title: string
  summary: string
  command_family: string
  difficulty: string
  storey_id?: number | null
  definition?: Record<string, unknown>
}): AuthoringForm {
  const definition = content.definition ?? {}
  return {
    kind: content.kind,
    slug: content.slug,
    title: content.title,
    summary: content.summary,
    commandFamily: content.command_family,
    difficulty: content.difficulty,
    storeyId: content.storey_id ?? null,
    pages:
      content.kind === 'tome'
        ? asArray(definition.pages).map((p) => {
            const r = p as Record<string, unknown>
            return { title: String(r.title ?? r.heading ?? ''), blocks: asArray(r.blocks).map((b) => blockFromDefinition(b as Record<string, unknown>)) }
          })
        : [],
    levels:
      content.kind === 'tome'
        ? []
        : contentLevels(definition).map((lvl, i) => levelFromDefinition(lvl, content.kind, i)),
  }
}

function contentLevels(definition: Record<string, unknown>): Record<string, unknown>[] {
  const levels = definition.levels
  if (Array.isArray(levels)) return levels.filter((l) => typeof l === 'object' && l) as Record<string, unknown>[]
  const single = definition.level
  return single && typeof single === 'object' ? [single as Record<string, unknown>] : []
}
