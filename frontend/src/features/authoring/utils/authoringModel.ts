/**
 * Structured form model for content authoring, plus (de)serialization to the
 * `definition` JSON the backend validates/compiles.
 *
 * Hierarchy: a LEVEL is a lesson stage that groups ordered PROBLEMS. For an
 * adventure a problem is a playable wave; for a challenge it is a difficulty
 * trial. Each problem owns its scenario (initial state + solution) and its own
 * extra VARIANTS. Only `initial_state` stays as guided JSON text; everything
 * else is real fields.
 */
import type { BattleStageConfig, ContentKind, Visibility } from '@/features/authoring/types'
import { DEFAULT_BATTLE_STAGE } from '@/features/authoring/utils/authoring-model/options'
import type { AuthoredLevel, AuthoredProblem, AuthoringForm, BookBlock } from '@/features/authoring/utils/authoring-model/types'
import { computeTargetState } from '@/shared/git/simulator/engine'
import type { MutableRepositoryState } from '@/shared/git/simulator/types'

export type { AuthoredLevel, AuthoredProblem,  AuthoringForm, BookBlock, BookPage } from '@/features/authoring/utils/authoring-model/types'
export { BLOCK_TYPES,  DIFFICULTIES, EVALUATION_MODES, VISIBILITIES } from '@/features/authoring/utils/authoring-model/options'
export { emptyLevel, emptyPage, emptyProblem, emptyVariant, initialForm } from '@/features/authoring/utils/authoring-model/factories'

/** A plain-language summary of what this form will compile into, so the author
 *  can see — before and after publishing — that each problem/variant becomes a
 *  real runtime row (a level groups ordered waves/trials; each problem brings
 *  its own variants). */
export function compileSummary(form: AuthoringForm): string {
  if (form.kind === 'lesson') {
    const pages = form.pages.length
    return `${pages} page${pages === 1 ? '' : 's'}`
  }
  const levels = form.levels.length
  const problems = form.levels.reduce((sum, level) => sum + level.problems.length, 0)
  const variants = form.levels.reduce(
    (sum, level) => sum + level.problems.reduce((p, problem) => p + 1 + problem.variants.length, 0),
    0,
  )
  const unit = form.kind === 'challenge' ? 'trial' : 'wave'
  const parts = [
    `${levels} level${levels === 1 ? '' : 's'}`,
    `${problems} ${unit}${problems === 1 ? '' : 's'}`,
    `${variants} variant${variants === 1 ? '' : 's'}`,
  ]
  return parts.join(' · ')
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

function problemToDefinition(problem: AuthoredProblem, kind: ContentKind): Record<string, unknown> {
  const initialState = parseJsonObject(problem.initialStateText, `Problem "${problem.slug}" initial state`)
  const solutionCommands = problem.solutionCommands.filter((c) => c.trim())
  const out: Record<string, unknown> = {
    slug: problem.slug,
    title: problem.title,
    solution_commands: solutionCommands,
    initial_state: initialState,
    // Command execution lives in the browser now, so the target DAG is derived
    // here by replaying the solution; the backend persists/hashes it instead of
    // re-running the (removed) Python engine.
    target_state: computeTargetState(initialState as MutableRepositoryState, solutionCommands),
    evaluation_spec: { completion_policy: { mode: problem.evaluationMode } },
    command_budget: {
      min_counted_commands: problem.minCountedCommands,
      max_counted_commands: problem.maxCountedCommands,
    },
  }
  if (kind === 'challenge' && problem.difficulty) out.difficulty = problem.difficulty
  // Scenario copy is optional; the runtime supplies a generic fallback when
  // neither field is authored.
  const story = problem.story.trim()
  const task = problem.task.trim()
  if (story || task) {
    out.scenario_context = { schema_version: 3, story, task }
  }
  if (problem.variants.length) {
    out.variants = problem.variants.map((variant) => {
      const variantInitial = parseJsonObject(variant.initialStateText, `Variant "${variant.slug}" initial state`)
      const variantSolution = variant.solutionCommands.filter((c) => c.trim())
      return {
        slug: variant.slug,
        label: variant.label,
        initial_state: variantInitial,
        solution_commands: variantSolution,
        target_state: computeTargetState(variantInitial as MutableRepositoryState, variantSolution),
      }
    })
  }
  return out
}

function levelToDefinition(level: AuthoredLevel, kind: ContentKind): Record<string, unknown> {
  const out: Record<string, unknown> = {
    slug: level.slug,
    title: level.title,
  }
  if (level.commandForms.length) out.command_forms = [...level.commandForms]
  const problems = level.problems.map((problem) => problemToDefinition(problem, kind))
  if (kind === 'challenge') {
    out.trials = problems
  } else {
    out.waves = problems
  }
  return out
}

/**
 * Build the `definition` payload, throwing a friendly error on bad JSON.
 * Reward checkpoints live on the chapter now, not here.
 */
export function formToDefinition(form: AuthoringForm): Record<string, unknown> {
  if (form.kind === 'lesson') {
    return {
      pages: form.pages.map((page) => ({
        title: page.title,
        blocks: page.blocks.map((block) => blockToDefinition(block)),
      })),
    }
  }
  return {
    battle_stage: normalizeBattleStage(form.battleStage),
    levels: form.levels.map((level) => levelToDefinition(level, form.kind)),
  }
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

// --- deserialization (existing content -> form) -------------------------------

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : []
}

function normalizeLanding(value: unknown): BattleStageConfig['landing'] {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null
  const raw = value as Record<string, unknown>
  const num = (v: unknown, fallback: number) => {
    const n = Number(v)
    return Number.isFinite(n) ? Math.min(1, Math.max(0, n)) : fallback
  }
  return {
    x: num(raw.x, 0),
    y: num(raw.y, 0),
    width: num(raw.width, 0),
    height: num(raw.height, 0),
  }
}

function normalizeBattleStage(value: unknown): BattleStageConfig {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return { ...DEFAULT_BATTLE_STAGE }
  const raw = value as Record<string, unknown>
  return {
    background: raw.background ? String(raw.background) : null,
    landing: normalizeLanding(raw.landing),
  }
}

function problemFromDefinition(raw: Record<string, unknown>, kind: ContentKind, index: number): AuthoredProblem {
  const budget = (raw.command_budget as Record<string, unknown>) || {}
  const evaluation = (raw.evaluation_spec as Record<string, unknown>) || {}
  const policy = (evaluation.completion_policy as Record<string, unknown>) || {}
  const context = (raw.scenario_context as Record<string, unknown>) || {}
  return {
    slug: String(raw.slug ?? `wave-${index + 1}`),
    title: String(raw.title ?? `Problem ${index + 1}`),
    difficulty: String(raw.difficulty ?? (kind === 'challenge' ? 'easy' : '')),
    story: String(context.story ?? ''),
    task: String(context.task ?? ''),
    solutionCommands: asArray(raw.solution_commands).map(String),
    initialStateText: JSON.stringify(raw.initial_state ?? {}, null, 2),
    evaluationMode: String(policy.mode ?? 'state_hash'),
    minCountedCommands: Number(budget.min_counted_commands ?? raw.min_counted_commands ?? 1),
    maxCountedCommands: Number(budget.max_counted_commands ?? raw.max_counted_commands ?? 8),
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

function levelFromDefinition(raw: Record<string, unknown>, kind: ContentKind, index: number): AuthoredLevel {
  const nestedKey = kind === 'challenge' ? 'trials' : 'waves'
  const nested = raw[nestedKey]
  const problems =
    Array.isArray(nested) && nested.length
      ? (nested.filter((p) => typeof p === 'object' && p) as Record<string, unknown>[]).map((p, i) =>
          problemFromDefinition(p, kind, i),
        )
      : // Legacy flat level: the level itself is a single problem.
        [problemFromDefinition(raw, kind, 0)]
  return {
    slug: String(raw.slug ?? `level-${index + 1}`),
    title: String(raw.title ?? `Level ${index + 1}`),
    commandForms: asArray(raw.command_forms)
      .map((v) => Number(v))
      .filter((n) => Number.isInteger(n)),
    problems,
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
  tags?: string[]
  visibility?: Visibility
  chapter_id?: number | null
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
    tags: Array.isArray(content.tags) ? content.tags.map(String) : [],
    visibility: content.visibility ?? 'private',
    chapterId: content.chapter_id ?? null,
    pages:
      content.kind === 'lesson'
        ? asArray(definition.pages).map((p) => {
            const r = p as Record<string, unknown>
            return { title: String(r.title ?? r.heading ?? ''), blocks: asArray(r.blocks).map((b) => blockFromDefinition(b as Record<string, unknown>)) }
          })
        : [],
    levels:
      content.kind === 'lesson'
        ? []
        : contentLevels(definition).map((lvl, i) => levelFromDefinition(lvl, content.kind, i)),
    battleStage: normalizeBattleStage(definition.battle_stage),
  }
}

function contentLevels(definition: Record<string, unknown>): Record<string, unknown>[] {
  const levels = definition.levels
  if (Array.isArray(levels)) return levels.filter((l) => typeof l === 'object' && l) as Record<string, unknown>[]
  const single = definition.level
  return single && typeof single === 'object' ? [single as Record<string, unknown>] : []
}
