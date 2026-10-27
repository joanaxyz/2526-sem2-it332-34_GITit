import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { CommandIntroduction, GuideElsewhere, Tip } from '@/features/story-map/api/commandIntroductionsApi'
import { WorkspaceTips } from '@/features/story-map/components/WorkspaceTips'

const tips: Tip[] = [
  { key: 'concept:staging-area', kind: 'concept', title: 'Staging area', text: 'A waiting area for your next commit.', syntax: null },
  { key: 'technique:several-paths', kind: 'technique', title: 'Name several files at once', text: 'List more than one path.', syntax: 'git add <path> <path>' },
]
const elsewhere: GuideElsewhere = {
  guide: {
    teaching_key: 'form:git rebase <upstream>',
    command_form: { usage_form: 'git rebase <upstream>' },
  } as CommandIntroduction,
  home: {
    chapter_number: 4,
    level_title: 'Completing Rebase Recovery Sequences', difficulty: 'easy',
    scenario_title: 'Replay your branch onto main',
  },
}

function setup(props: Partial<Parameters<typeof WorkspaceTips>[0]> = {}) {
  const handlers = { onDismissTip: vi.fn(), onReadGuide: vi.fn(), onHideElsewhere: vi.fn() }
  const view = render(<WorkspaceTips tips={tips} elsewhere={elsewhere} {...handlers} {...props} />)
  return { ...handlers, ...view }
}

afterEach(cleanup)

describe('workspace tips', () => {
  it('shows one tip at a time and puts it away on request', () => {
    const { onDismissTip } = setup({ elsewhere: null })
    const tip = screen.getByRole('region', { name: 'Tip: Staging area' })
    expect(within(tip).getByText('A waiting area for your next commit.')).toBeInTheDocument()
    expect(within(tip).getByText('1 more')).toBeInTheDocument()
    expect(screen.queryByText('Name several files at once')).not.toBeInTheDocument()

    fireEvent.click(within(tip).getByRole('button', { name: 'Got it' }))
    expect(onDismissTip).toHaveBeenCalledWith('concept:staging-area')
  })

  it('shows a technique with its syntax', () => {
    setup({ tips: tips.slice(1), elsewhere: null })
    const tip = screen.getByRole('region', { name: 'Tip: Name several files at once' })
    expect(within(tip).getByText('git add <path> <path>')).toBeInTheDocument()
    expect(within(tip).queryByText(/^\d+ more$/)).not.toBeInTheDocument()
  })

  it('says where a command taught elsewhere lives, and offers its guide', () => {
    const { onReadGuide, onHideElsewhere } = setup({ tips: [] })
    const note = screen.getByRole('region', { name: 'Taught in another scenario' })
    expect(within(note).getByText('Taught in Chapter 4')).toBeInTheDocument()
    expect(within(note).getByText('git rebase <upstream>')).toBeInTheDocument()
    expect(note).toHaveTextContent('Completing Rebase Recovery Sequences · easy · Replay your branch onto main')

    fireEvent.click(within(note).getByRole('button', { name: 'Read guide' }))
    expect(onReadGuide).toHaveBeenCalledWith('form:git rebase <upstream>')
    fireEvent.click(within(note).getByRole('button', { name: 'Hide note' }))
    expect(onHideElsewhere).toHaveBeenCalledOnce()
  })

  it('stays readable while a command guide is open', () => {
    setup()
    expect(screen.getByRole('complementary', { name: 'Tips' })).toHaveAttribute('data-tour-target', 'workspace-tips')
  })

  it('renders nothing when there is nothing to say', () => {
    const { container } = setup({ tips: [], elsewhere: null })
    expect(container).toBeEmptyDOMElement()
  })
})
