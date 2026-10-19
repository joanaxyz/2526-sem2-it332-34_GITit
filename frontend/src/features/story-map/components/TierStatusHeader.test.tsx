import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import type { TierRun } from './tierWorkspaceTypes'

vi.mock('@/shared/audio/AudioControls', () => ({
  AudioControls: () => <div data-testid="audio-controls" />,
}))

vi.mock('@/shared/level/components/WorkspaceHeaderAccount', () => ({
  WorkspaceHeaderAccount: () => <div data-testid="workspace-account" />,
}))

import { TierStatusHeader } from './TierStatusHeader'

afterEach(cleanup)

const run = {
  status: 'started',
  replay: false,
  difficulty: 'easy',
  tier: { adventure_level_title: 'Branching paths' },
} as TierRun

const guide = (teachingKey: string, title: string, usageForm: string) => ({
  teaching_key: teachingKey,
  title,
  command_form: { usage_form: usageForm },
}) as CommandIntroduction

const guides = [
  guide('form:git init', 'Initialize the current folder', 'git init'),
  guide('form:git add <path>', 'Stage a file', 'git add <path>'),
]

describe('TierStatusHeader', () => {
  it('uses the floating mascot to reopen a single guide', () => {
    const onSelectCommandGuide = vi.fn()
    render(
      <TierStatusHeader
        run={run}
        commandGuides={[guides[0]]}
        commandGuideOpen={false}
        onSelectCommandGuide={onSelectCommandGuide}
      />,
    )

    const button = screen.getByRole('button', { name: 'Open command guide' })
    expect(button).toHaveAttribute('data-command-guide-launcher')
    expect(button).not.toHaveTextContent('Command guide')
    expect(button).toHaveClass('guide-mascot__button')
    expect(button.closest('.gameplay-workspace-header')).toBeNull()
    fireEvent.click(button)
    expect(onSelectCommandGuide).toHaveBeenCalledWith('form:git init')
  })

  it('opens a picker when the run has encountered multiple guides', () => {
    const onSelectCommandGuide = vi.fn()
    render(
      <TierStatusHeader
        run={run}
        commandGuides={guides}
        currentCommandGuideKey="form:git add <path>"
        onSelectCommandGuide={onSelectCommandGuide}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Browse command guides' }))
    expect(screen.getByRole('group', { name: 'Command guides' })).toBeInTheDocument()
    expect(screen.getByText('Initialize the current folder')).toBeInTheDocument()
    expect(screen.getByText('Stage a file')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /Initialize the current folder/ }))
    expect(onSelectCommandGuide).toHaveBeenCalledWith('form:git init')
  })

  it('hides the floating mascot and history control while the guide is visible', () => {
    render(
      <TierStatusHeader
        run={run}
        commandGuides={guides}
        commandGuideOpen
      />,
    )

    expect(screen.queryByRole('button', { name: 'Command guide is open' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Browse command guides' })).not.toBeInTheDocument()
    expect(document.querySelector('.guide-mascot')).toHaveAttribute('inert')
  })

  it('reopens the current guide directly when several commands have been encountered', () => {
    const onSelectCommandGuide = vi.fn()
    render(<TierStatusHeader run={run} commandGuides={guides}
      currentCommandGuideKey={guides[0].teaching_key} onSelectCommandGuide={onSelectCommandGuide} />)
    fireEvent.click(screen.getByRole('button', { name: 'Open command guide' }))
    expect(onSelectCommandGuide).toHaveBeenCalledWith(guides[0].teaching_key)
    expect(screen.queryByRole('group', { name: 'Command guides' })).not.toBeInTheDocument()
  })
})
