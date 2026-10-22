import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { WorldMascot } from './WorldMascot'
import type { MascotKnowledgeTip } from './mascotKnowledge'

vi.mock('./MascotSprite', () => ({
  MascotSprite: ({ idleActions }: { idleActions?: boolean }) => <span data-testid="mascot-sprite" data-idle-actions={idleActions} />,
}))
vi.mock('@/shared/sprites/preload', () => ({ warmImages: vi.fn().mockResolvedValue(undefined) }))

const knowledge: MascotKnowledgeTip[] = [
  { id: 'init', command: 'git init', text: 'Create Git metadata.', source: 'Foundations' },
  { id: 'add', command: 'git add', text: 'Stage working directory changes.', source: 'Foundations' },
]

beforeEach(() => {
  vi.stubGlobal('requestAnimationFrame', vi.fn(() => 1))
  vi.stubGlobal('cancelAnimationFrame', vi.fn())
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockImplementation(function (this: HTMLElement) {
    return this.classList.contains('world-mascot') ? new DOMRect(0, 0, 1024, 768) : new DOMRect()
  })
})
afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.restoreAllMocks() })

const mascot = () => screen.getByRole('button', { name: 'Learning guide: share a Git tip' })

describe('roaming mascot knowledge', () => {
  it.each(['home', 'track'] as const)('enables random idle actions only on Home (%s)', (surface) => {
    render(<main><WorldMascot surface={surface} /></main>)
    expect(screen.getByTestId('mascot-sprite')).toHaveAttribute('data-idle-actions', String(surface === 'home'))
  })

  it('shows a tip on click without flying away, and cycles through earned knowledge', () => {
    render(<main><WorldMascot surface="home" knowledge={knowledge} /></main>)
    const actor = mascot()
    const position = actor.style.transform
    expect(screen.queryByRole('region', { name: 'Git knowledge' })).not.toBeInTheDocument()
    fireEvent.click(actor)
    expect(actor).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByRole('status')).toHaveTextContent('Create Git metadata.')
    expect(actor.style.transform).toBe(position)
    fireEvent.click(actor)
    expect(screen.getByRole('status')).toHaveTextContent('Stage working directory changes.')
    fireEvent.click(screen.getByRole('button', { name: 'Another tip' }))
    expect(screen.getByRole('status')).toHaveTextContent('Create Git metadata.')
  })

  it('provides introductory concepts when knowledge has not loaded or no commands are learned', () => {
    const view = render(<main><WorldMascot surface="home" /></main>)
    fireEvent.click(mascot())
    expect(screen.getByRole('status')).toHaveTextContent('Git keeps a history of your project.')
    expect(screen.getByRole('region', { name: 'Git knowledge' })).toBeInTheDocument()
    view.rerender(<main><WorldMascot surface="home" knowledge={knowledge} /></main>)
    expect(screen.getByRole('status')).toHaveTextContent('Git keeps a history of your project.')
    fireEvent.click(screen.getByRole('button', { name: 'Another tip' }))
    expect(screen.getByRole('status')).toHaveTextContent('Create Git metadata.')
  })

  it('continues to a different tip after dismissal instead of repeating the first one', () => {
    render(<main><WorldMascot surface="home" knowledge={knowledge} /></main>)
    fireEvent.click(mascot())
    fireEvent.click(screen.getByRole('button', { name: 'Dismiss tip' }))
    fireEvent.click(mascot())
    expect(screen.getByRole('status')).toHaveTextContent('Stage working directory changes.')
  })

  it('supports close, Escape, and clicking the page, with focus returned for keyboard dismissal', () => {
    render(<main data-testid="page"><WorldMascot surface="track" knowledge={knowledge} /></main>)
    fireEvent.click(mascot())
    screen.getByRole('button', { name: 'Another tip' }).focus()
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
    expect(mascot()).toHaveFocus()
    fireEvent.click(mascot())
    fireEvent.click(screen.getByRole('button', { name: 'Dismiss tip' }))
    expect(mascot()).toHaveAttribute('aria-expanded', 'false')
    fireEvent.click(mascot())
    fireEvent.pointerDown(screen.getByTestId('page'))
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('drops stale tips when the user changes chapter or the earned skill list changes', () => {
    const view = render(<main><WorldMascot surface="track" knowledge={knowledge} contextKey="chapter:1" /></main>)
    fireEvent.click(mascot())
    view.rerender(<main><WorldMascot surface="track" knowledge={knowledge} contextKey="chapter:2" /></main>)
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
    view.rerender(<main><WorldMascot surface="track" knowledge={knowledge} contextKey="chapter:1" /></main>)
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
    view.rerender(<main><WorldMascot surface="track" knowledge={knowledge} contextKey="chapter:2" /></main>)
    fireEvent.click(mascot())
    expect(screen.getByRole('status')).toHaveTextContent('Create Git metadata.')
    view.rerender(<main><WorldMascot surface="track" knowledge={knowledge.slice(1)} contextKey="chapter:2" /></main>)
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
    fireEvent.click(mascot())
    expect(screen.getByRole('status')).toHaveTextContent('Stage working directory changes.')
  })
})
