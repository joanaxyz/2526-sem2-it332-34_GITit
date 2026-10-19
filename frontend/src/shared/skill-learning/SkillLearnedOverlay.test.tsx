import { useState } from 'react'
import { act, cleanup, fireEvent, render, renderHook, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { SkillLearnedOverlay } from './SkillLearnedOverlay'
import { useSkillLearnedQueue, type LearnedSkill } from './useSkillLearnedQueue'

const init: LearnedSkill = { id: 1, slug: 'git-init', base_command: 'git init', title: 'Create a repository', summary: '', chapter_number: 1, chapter_title: 'Foundations' }
const add: LearnedSkill = { ...init, id: 2, slug: 'git-add', base_command: 'git add', title: 'Stage changes' }

afterEach(cleanup)

describe('SkillLearnedOverlay', () => {
  it.each(['Escape', 'Enter', ' '])('dismisses with %j and restores terminal focus', async (key) => {
    function Workspace() {
      const [open, setOpen] = useState(false)
      return <><button onClick={() => setOpen(true)}>Terminal</button><SkillLearnedOverlay skill={open ? init : null} companionSlug="black" onClose={() => setOpen(false)} /></>
    }
    render(<Workspace />)
    const terminal = screen.getByRole('button', { name: 'Terminal' })
    terminal.focus()
    fireEvent.click(terminal)
    const dialog = screen.getByRole('dialog', { name: "You've learned a new skill" })
    await waitFor(() => expect(dialog).toHaveFocus())
    const portrait = screen.getByRole('img', { name: 'Create a repository skill' })
    expect(portrait.querySelector('image')).toHaveAttribute('href', '/cosmetics/companion/black/effects/skill-lightning-25/init.png')
    expect(portrait.querySelector('image')).toHaveAttribute('x', '-1024')
    expect(portrait.querySelector('image')).toHaveAttribute('y', '-512')
    fireEvent.keyDown(dialog, { key: 'Tab' })
    expect(dialog).toHaveFocus()
    fireEvent.keyDown(dialog, { key })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(terminal).toHaveFocus()
  })

  it.each(['backdrop', 'message', 'mascot', 'portrait'])('dismisses when clicking the %s', (target) => {
    function Workspace() {
      const [open, setOpen] = useState(true)
      return <SkillLearnedOverlay skill={open ? init : null} companionSlug="blue" onClose={() => setOpen(false)} />
    }
    render(<Workspace />)
    const element = target === 'backdrop' ? screen.getByRole('dialog')
      : target === 'message' ? screen.getAllByText("You've learned a new skill").at(-1)!
        : screen.getByRole('img', { name: target === 'mascot' ? 'Git it guide' : 'Create a repository skill' })
    fireEvent.click(element)
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })
})

describe('server-learned skill queue', () => {
  it('waits for animations, preserves multiple events in order, and never repeats a command family', () => {
    const { result, rerender } = renderHook(({ blocked }) => useSkillLearnedQueue({ runId: 1, blocked }), { initialProps: { blocked: true } })
    act(() => result.current.enqueue([init, add, { ...init, id: 99 }]))
    expect(result.current.pending).toBe(true)
    expect(result.current.skill).toBeNull()
    rerender({ blocked: false })
    expect(result.current.skill).toEqual(init)
    act(() => result.current.dismiss())
    expect(result.current.skill).toEqual(add)
    act(() => result.current.dismiss())
    act(() => result.current.enqueue([init, add]))
    expect(result.current.pending).toBe(false)
  })

  it('drops queued events on run changes and ignores late responses from the previous run', () => {
    const { result, rerender } = renderHook(({ runId }) => useSkillLearnedQueue({ runId, blocked: false }), { initialProps: { runId: 1 } })
    const oldEnqueue = result.current.enqueue
    act(() => oldEnqueue([init]))
    rerender({ runId: 2 })
    expect(result.current.skill).toBeNull()
    act(() => result.current.enqueue([add]))
    act(() => oldEnqueue([init]))
    expect(result.current.skill).toEqual(add)
    act(() => result.current.dismiss())
    act(() => result.current.enqueue([init]))
    expect(result.current.skill).toEqual(init)
  })
})
