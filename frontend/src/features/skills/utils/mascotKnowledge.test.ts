import { describe, expect, it } from 'vitest'
import type { LearnedSkill } from '@/features/skills/types'
import { COMMAND_ANATOMY_TIP } from '@/shared/mascot/mascotKnowledge'
import { knowledgeForMascot } from './mascotKnowledge'

const skills: LearnedSkill[] = [
  { id: 1, slug: 'git-init', base_command: 'git init', title: 'Initialize', summary: 'Create Git metadata.', chapter_id: 10, chapter_number: 1, chapter_title: 'Foundations' },
  { id: 2, slug: 'git-branch', base_command: 'git branch', title: 'Branch', summary: 'Create and inspect branches.', chapter_id: 20, chapter_number: 2, chapter_title: 'Branches' },
  { id: 3, slug: 'git-merge', base_command: 'git merge', title: 'Merge', summary: 'Combine another branch into this one.', chapter_id: 30, chapter_number: 3, chapter_title: 'Merging' },
]

const initKnowledge: NonNullable<LearnedSkill['knowledge']> = [
  { id: 'form:1:command', kind: 'command', command: 'git init', title: 'Initialize', token: '', syntax: 'git init -b <branch>', text: 'Create Git metadata.', when_to_use: 'Choose the first branch.' },
  { id: 'form:1:branch', kind: 'option', command: 'git init', title: 'Initial branch', token: '-b / --initial-branch', syntax: 'git init -b <branch>', text: 'Name the first branch.', when_to_use: 'Choose the first branch.' },
  { id: 'form:2:directory', kind: 'argument', command: 'git init', title: 'Directory', token: '<directory>', syntax: 'git init <directory>', text: 'Choose the repository directory.', when_to_use: 'Initialize another directory.' },
]

describe('knowledge matched to the learner', () => {
  it('uses earned skills and their authored descriptions, with the latest chapter first at home', () => {
    const tips = knowledgeForMascot(skills)
    expect(tips.map((tip) => tip.command)).toEqual(['git merge', 'git branch', 'git init', undefined])
    expect(tips.at(-1)).toBe(COMMAND_ANATOMY_TIP)
    expect(tips[0]).toEqual({ id: 'skill:3', command: 'git merge', text: skills[2].summary, source: 'Merging' })
    expect(skills.map((skill) => skill.id)).toEqual([1, 2, 3])
  })

  it('prioritizes the viewed chapter, reinforces earlier knowledge, and excludes later chapters', () => {
    const tips = knowledgeForMascot(skills, { id: 20, number: 2 })
    expect(tips.map((tip) => tip.command)).toEqual(['git branch', 'git init', undefined])
  })

  it('never introduces a command just because its chapter is open', () => {
    expect(knowledgeForMascot(skills.slice(0, 1), { id: 30, number: 3 }).map((tip) => tip.command)).toEqual(['git init', undefined])
    expect(knowledgeForMascot([], { id: 30, number: 3 })).toEqual([])
  })

  it('ignores missing teaching copy and supplies a source for unassigned skills', () => {
    expect(knowledgeForMascot([{ ...skills[0], summary: '  ' }])).toEqual([])
    expect(knowledgeForMascot([{ ...skills[0], chapter_title: '' }])[0].source).toBe('Your spellbook')
  })

  it('cycles through learned options and arguments even when only git init is learned', () => {
    const tips = knowledgeForMascot([{ ...skills[0], knowledge: initKnowledge }])
    expect(tips.map((tip) => tip.id)).toEqual([
      'skill:1', 'skill:1:form:1:branch', 'skill:1:form:2:directory', COMMAND_ANATOMY_TIP.id,
    ])
    expect(tips[1]).toMatchObject({ kind: 'option', token: '-b / --initial-branch', whenToUse: 'Choose the first branch.' })
  })

  it('deduplicates map guidance while retaining other learned forms of the same command', () => {
    const tips = knowledgeForMascot([{ ...skills[0], knowledge: initKnowledge }], undefined, {
      currentLevelId: 1,
      levels: [{ id: 1, title: 'Initialize a project', is_passed: false, knowledge: initKnowledge.slice(0, 2) }],
    })
    expect(tips.map((tip) => tip.id)).toEqual([
      'level:1:form:1:command', 'level:1:form:1:branch', 'skill:1:form:2:directory', COMMAND_ANATOMY_TIP.id,
    ])
  })
})
