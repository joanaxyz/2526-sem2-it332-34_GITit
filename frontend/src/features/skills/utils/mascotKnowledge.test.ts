import { describe, expect, it } from 'vitest'
import type { LearnedSkill } from '@/features/skills/types'
import { knowledgeForMascot } from './mascotKnowledge'

const skills: LearnedSkill[] = [
  { id: 1, slug: 'git-init', base_command: 'git init', title: 'Initialize', summary: 'Create Git metadata.', chapter_id: 10, chapter_number: 1, chapter_title: 'Foundations' },
  { id: 2, slug: 'git-branch', base_command: 'git branch', title: 'Branch', summary: 'Create and inspect branches.', chapter_id: 20, chapter_number: 2, chapter_title: 'Branches' },
  { id: 3, slug: 'git-merge', base_command: 'git merge', title: 'Merge', summary: 'Combine another branch into this one.', chapter_id: 30, chapter_number: 3, chapter_title: 'Merging' },
]

describe('knowledge matched to the learner', () => {
  it('uses earned skills and their authored descriptions, with the latest chapter first at home', () => {
    const tips = knowledgeForMascot(skills)
    expect(tips.map((tip) => tip.command)).toEqual(['git merge', 'git branch', 'git init'])
    expect(tips[0]).toEqual({ id: 'skill:3', command: 'git merge', text: skills[2].summary, source: 'Merging' })
    expect(skills.map((skill) => skill.id)).toEqual([1, 2, 3])
  })

  it('prioritizes the viewed chapter, reinforces earlier knowledge, and excludes later chapters', () => {
    const tips = knowledgeForMascot(skills, { id: 20, number: 2 })
    expect(tips.map((tip) => tip.command)).toEqual(['git branch', 'git init'])
  })

  it('never introduces a command just because its chapter is open', () => {
    expect(knowledgeForMascot(skills.slice(0, 1), { id: 30, number: 3 }).map((tip) => tip.command)).toEqual(['git init'])
    expect(knowledgeForMascot([], { id: 30, number: 3 })).toEqual([])
  })

  it('ignores missing teaching copy and supplies a source for unassigned skills', () => {
    expect(knowledgeForMascot([{ ...skills[0], summary: '  ' }])).toEqual([])
    expect(knowledgeForMascot([{ ...skills[0], chapter_title: '' }])[0].source).toBe('Your spellbook')
  })
})
