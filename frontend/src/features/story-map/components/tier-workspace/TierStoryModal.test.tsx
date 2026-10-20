import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { TierStoryModal } from './TierStoryModal'

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

const story = {
  title: 'Initialize invoice-tracker',
  intro: 'A client hired you to build a simple invoice tracker.',
  startingPoint: 'The invoice-tracker folder contains two untracked files.',
  task: 'Create and initialize a new Git repository named invoice-tracker.',
  expectedResult: 'The folder is a repository and the files remain untracked.',
}

describe('TierStoryModal', () => {
  it('leads with the task and keeps the complete authored briefing before the continue hint', () => {
    render(<TierStoryModal open {...story}
      realWorldContext="Teams clone shared projects locally." onClose={vi.fn()} />)
    const startingPoint = screen.getByRole('region', { name: 'Starting point' })
    const context = screen.getByRole('region', { name: 'Why this matters' })
    const task = screen.getByRole('region', { name: 'Your task' })
    const expectedResult = screen.getByRole('region', { name: 'Expected result' })
    const follows = (a: Element, b: Element) => Boolean(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING)
    expect(follows(task, screen.getByText(story.intro))).toBe(true)
    expect(follows(screen.getByText(story.intro), startingPoint)).toBe(true)
    expect(follows(startingPoint, expectedResult)).toBe(true)
    expect(follows(expectedResult, context)).toBe(true)
    expect(follows(context, screen.getByText(/click anywhere to begin/i))).toBe(true)
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    expect(within(task).getByText(story.task).tagName).toBe('P')
    expect(within(startingPoint).getByText(story.startingPoint).tagName).toBe('P')
  })

  it.each(['backdrop', 'story', 'hint', 'enter', 'space', 'escape', 'ctrl', 'meta'])('returns focus to the terminal using %s', async (action) => {
    const onClose = vi.fn()
    const view = render(<>
      <input data-command-input aria-label="Terminal" />
      <TierStoryModal open {...story} onClose={onClose} />
    </>)
    const dialog = screen.getByRole('dialog')
    if (action === 'backdrop') fireEvent.click(dialog)
    else if (action === 'story') fireEvent.click(screen.getByText(story.intro))
    else if (action === 'hint') fireEvent.click(screen.getByText(/click anywhere to begin/i))
    else fireEvent.keyDown(dialog, {
      key: action === 'space' ? ' ' : action === 'escape' ? 'Escape' : 'Enter',
      ctrlKey: action === 'ctrl', metaKey: action === 'meta',
    })
    expect(onClose).toHaveBeenCalledTimes(1)
    view.rerender(<input data-command-input aria-label="Terminal" />)
    await waitFor(() => expect(screen.getByRole('textbox', { name: 'Terminal' })).toHaveFocus())
  })

  it('shows the title, intro and task from the run, without an empty context section', () => {
    render(<TierStoryModal open {...story} onClose={vi.fn()} />)

    expect(screen.getByRole('dialog', { name: story.title })).toBeInTheDocument()
    expect(screen.getByText(story.intro)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Starting point' })).toBeInTheDocument()
    expect(screen.getByText(story.startingPoint)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Your task' })).toBeInTheDocument()
    expect(screen.getByText(story.task)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Expected result' })).toBeInTheDocument()
    expect(screen.getByText(story.expectedResult)).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Why this matters' })).not.toBeInTheDocument()
  })

  it('shows real-world context only when it is given', () => {
    render(<TierStoryModal open {...story} realWorldContext="Every team versions its code." onClose={vi.fn()} />)

    expect(screen.getByRole('heading', { name: 'Why this matters' })).toBeInTheDocument()
    expect(screen.getByText('Every team versions its code.')).toBeInTheDocument()
  })

  it('falls back to a short notice when the run carries no story text', () => {
    render(<TierStoryModal open title="Level" intro="" task="" onClose={vi.fn()} />)

    expect(screen.getByText('No story is available for this level.')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Your task' })).not.toBeInTheDocument()
  })

  it('does not dismiss while selecting a passage', () => {
    const onClose = vi.fn()
    render(<TierStoryModal open {...story} onClose={onClose} />)
    vi.spyOn(window, 'getSelection').mockReturnValue({ toString: () => 'A client hired you' } as Selection)

    fireEvent.click(screen.getByText(story.intro))
    expect(onClose).not.toHaveBeenCalled()
  })

  it('honors authored paragraph breaks without dropping or rewriting content', () => {
    const first = 'Finn has left the build file in pipelines/build.yml.'
    const second = 'The operations team needs a dedicated repository before the deployment meeting.'
    const intro = `${first}\n\n${second}`
    render(<TierStoryModal open {...story} intro={intro} onClose={vi.fn()} />)
    const situation = screen.getByRole('region', { name: 'The situation' })
    const paragraphs = Array.from(situation.querySelectorAll('p'))
    expect(paragraphs.map((paragraph) => paragraph.textContent)).toEqual([first, second])
  })

  it('renders authored emphasis and code while leaving HTML and links inert', () => {
    render(<TierStoryModal open {...story}
      intro={'Use **only `ci-configs`**.\n\n<script>alert(1)</script> [Link](https://example.test)'}
      task="Keep `main` as the first branch." onClose={vi.fn()} />)
    const situation = screen.getByRole('region', { name: 'The situation' })
    expect(within(situation).getByText('only', { exact: false }).tagName).toBe('STRONG')
    expect(within(situation).getByText('ci-configs').tagName).toBe('CODE')
    expect(within(screen.getByRole('region', { name: 'Your task' })).getByText('main').tagName).toBe('CODE')
    expect(within(situation).getByText('<script>alert(1)</script> [Link](https://example.test)')).toBeInTheDocument()
    expect(situation.querySelector('script, a')).toBeNull()
  })

  it('ignores unrelated keys and held Enter keys', () => {
    const onClose = vi.fn()
    render(<TierStoryModal open {...story} onClose={onClose} />)
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'a' })
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Enter', repeat: true })

    expect(onClose).not.toHaveBeenCalled()
  })

  it('renders nothing while closed', () => {
    render(<TierStoryModal open={false} {...story} onClose={vi.fn()} />)

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })
})
