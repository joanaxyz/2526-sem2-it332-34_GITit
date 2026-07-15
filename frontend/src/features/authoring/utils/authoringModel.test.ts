import { describe, expect, it } from 'vitest'

import {
  compileSummary,
  emptyLevel,
  emptyProblem,
  formFromContent,
  formToDefinition,
  initialForm,
} from './authoringModel'

describe('authoring serde round-trip', () => {
  it('preserves brief, waves and variants through the definition', () => {
    const form = initialForm('adventure')
    form.levels = [
      {
        ...emptyLevel('adventure', 0),
        brief: 'Make your first save.',
        problems: [
          {
            ...emptyProblem('adventure', 0),
            story: 'The history got tangled.',
            task: 'Inspect the repository state.',
            solutionCommands: ['git status'],
            variants: [
              { slug: 'case-1', label: 'Case 1', initialStateText: '{}', solutionCommands: ['git status'] },
            ],
          },
          {
            ...emptyProblem('adventure', 1),
            story: 'Now seal it.',
            task: 'Commit the staged snapshot.',
            solutionCommands: ['git commit -m wip'],
          },
        ],
      },
    ]

    const definition = formToDefinition(form) as Record<string, unknown>
    const restored = formFromContent({
      kind: 'adventure',
      slug: form.slug,
      title: form.title,
      summary: form.summary,
      command_family: form.commandFamily,
      difficulty: form.difficulty,
      chapter_id: null,
      definition,
    })

    const level = restored.levels[0]
    expect(level.brief).toBe('Make your first save.')
    expect(level.problems).toHaveLength(2)
    const wave = level.problems[0]
    expect(wave.story).toBe('The history got tangled.')
    expect(wave.task).toBe('Inspect the repository state.')
    expect(wave.variants).toHaveLength(1)
    expect(wave.variants[0].slug).toBe('case-1')
    expect(level.problems[1].task).toBe('Commit the staged snapshot.')
  })

  it('summarizes what a form compiles into', () => {
    const challenge = initialForm('challenge')
    challenge.levels = [
      {
        ...emptyLevel('challenge', 0),
        problems: [
          {
            ...emptyProblem('challenge', 0),
            variants: [
              { slug: 'case-1', label: 'Case 1', initialStateText: '{}', solutionCommands: ['git status'] },
              { slug: 'case-2', label: 'Case 2', initialStateText: '{}', solutionCommands: ['git status'] },
            ],
          },
        ],
      },
    ]
    // one level, one trial, primary + two extra variants = 3
    expect(compileSummary(challenge)).toBe('1 level · 1 trial · 3 variants')

    const adventure = initialForm('adventure')
    adventure.levels = [
      {
        ...emptyLevel('adventure', 0),
        problems: [{ ...emptyProblem('adventure', 0) }],
      },
    ]
    expect(compileSummary(adventure)).toBe('1 level · 1 wave · 1 variant')
  })

  it('emits nested waves for adventures and trials for challenges', () => {
    const adventure = initialForm('adventure')
    const advDef = formToDefinition(adventure) as { levels: Record<string, unknown>[] }
    expect(Array.isArray(advDef.levels[0].waves)).toBe(true)

    const challenge = initialForm('challenge')
    const chalDef = formToDefinition(challenge) as { levels: Record<string, unknown>[] }
    expect(Array.isArray(chalDef.levels[0].trials)).toBe(true)
  })

  it('omits brief from the definition when the author leaves it empty', () => {
    const form = initialForm('adventure')
    const definition = formToDefinition(form) as { levels: { waves: Record<string, unknown>[] }[] }
    const wave = definition.levels[0].waves[0]
    expect(wave.scenario_context).toBeUndefined()
  })

  it('reads legacy flat levels as a single problem', () => {
    const restored = formFromContent({
      kind: 'adventure',
      slug: 'legacy',
      title: 'Legacy',
      summary: '',
      command_family: 'git status',
      difficulty: '',
      chapter_id: null,
      definition: {
        levels: [
          {
            slug: 'old-level',
            title: 'Old level',
            solution_commands: ['git status'],
            initial_state: {},
            scenario_context: { schema_version: 3, story: 'old story', task: 'old task' },
          },
        ],
      },
    })
    expect(restored.levels[0].problems).toHaveLength(1)
    expect(restored.levels[0].problems[0].story).toBe('old story')
  })

  it('round-trips lesson content metadata', () => {
    const form = initialForm('lesson')
    form.tags = ['intro', 'staging']
    form.visibility = 'public'

    const definition = formToDefinition(form) as Record<string, unknown>

    const restored = formFromContent({
      kind: 'lesson',
      slug: form.slug,
      title: form.title,
      summary: form.summary,
      command_family: '',
      difficulty: '',
      tags: form.tags,
      visibility: form.visibility,
      chapter_id: null,
      definition,
    })
    expect(restored.tags).toEqual(['intro', 'staging'])
    expect(restored.visibility).toBe('public')
  })
})
