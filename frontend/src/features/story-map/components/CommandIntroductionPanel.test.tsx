import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { commandIntroductionsApi, type CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import { CommandIntroductionPanel } from '@/features/story-map/components/CommandIntroductionPanel'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { readTierRunBootstrap } from '@/features/story-map/utils/tierRunBootstrap'
import { queryKeys } from '@/shared/api/queryKeys'

vi.mock('@/features/story-map/api/commandIntroductionsApi', () => ({
  commandIntroductionsApi: { complete: vi.fn() },
}))

const tutor: CommandIntroduction = {
  context_id: 'snapshot-1', teaching_key: 'form:git switch -c <branch>',
  run_revision: 0, phase: 'introduction', title: 'Create and switch',
  needs: [
    { kind: 'branch', text: 'Branch feature is created.', action: 'create', subjects: ['feature'] },
    { kind: 'head', text: 'HEAD moves to feature.', action: 'move', subjects: ['feature'] },
  ],
  changes: [],
  anatomy: [
    { token: 'git', text: 'runs Git' },
    { token: 'switch', text: 'the Git command to run' },
    { token: '-c', text: 'create the branch first, then switch to it' },
    { token: '<branch>', text: 'you fill this in: the branch name' },
  ],
  concepts: [
    { key: 'commands', title: 'Commands', text: 'You type a command in the terminal and press Enter.' },
    { key: 'branch', title: 'Branch', text: 'A name that points at a commit.' },
  ],
  verdict: null, explanation: null, example_command: null, completion_token: null,
  command_form: {
    teaching_key: 'form:git switch -c <branch>', usage_form: 'git switch -c <branch>',
    label: 'Create and switch', summary: 'Creates a branch and moves HEAD onto it.',
  },
}
const feedback: CommandIntroduction = {
  ...tutor, phase: 'feedback', verdict: 'incorrect',
  explanation: "That wasn't the command this step needs.", example_command: 'git switch -c feature',
  completion_token: 'feedback-token',
}

function target(tag: 'input' | 'div', attribute: string, value: string, top: number) {
  const element = document.createElement(tag)
  element.setAttribute(attribute, value)
  Object.defineProperty(element, 'getBoundingClientRect', { value: () => ({
    x: 350, y: top, left: 350, right: 650, top, bottom: top + 48,
    width: 300, height: 48, toJSON: () => ({}),
  }) })
  element.scrollIntoView = vi.fn()
  document.body.appendChild(element)
}

function setup(lesson = tutor) {
  target('input', 'data-command-input', '', 650)
  target('div', 'data-tour-target', 'live-dag', 160)
  const run = { id: 1, status: 'started', tutor: lesson, steps: [],
    counts: { total_attempts: 0, counted_action_total: 0 },
    scaffolding: { live_dag: true, contextual_feedback: false, expected_state: false },
  } as unknown as TierRun
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  client.setQueryData(queryKeys.adventureTierRun(run.id), run)
  const onDismiss = vi.fn()
  render(<QueryClientProvider client={client}>
    <CommandIntroductionPanel run={run} tutor={lesson} onDismiss={onDismiss} />
  </QueryClientProvider>)
  return { client, run, onDismiss }
}

beforeEach(() => { vi.mocked(commandIntroductionsApi.complete).mockResolvedValue({ tutor: null }) })
afterEach(() => {
  cleanup()
  document.querySelectorAll('[data-command-input], [data-tour-target="live-dag"]').forEach((element) => element.remove())
  vi.clearAllMocks()
  sessionStorage.clear()
})

describe('terminal-led command introduction', () => {
  it('introduces only the one form the repository needs, around the normal terminal', async () => {
    setup()
    expect(await screen.findByText('Syntax: git switch -c <branch>')).toBeInTheDocument()
    expect(screen.getByText('Command guide')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-tour-spotlight')).toBeInTheDocument()
    expect(screen.getByRole('dialog', { name: 'Create and switch' })).toBeInTheDocument()
    expect(screen.getAllByRole('textbox')).toHaveLength(1)
    expect(screen.getByText(tutor.command_form.summary)).toBeInTheDocument()
    // Absolute beginners: what a command is, and what each part means.
    expect(screen.getByText(/You type a command in the terminal/)).toBeInTheDocument()
    const parts = within(screen.getByLabelText('What each part means'))
    expect(parts.getByText('create the branch first, then switch to it')).toBeInTheDocument()
    // The concrete solution command is only revealed after a miss.
    expect(screen.queryByText('git switch -c feature')).not.toBeInTheDocument()
    // Nothing to click through: the guide stays while the learner types. On a
    // narrow screen the change sits in its own tab of the same card.
    expect(screen.getByRole('button', { name: 'Hide command guide' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Got it' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', { name: 'What changes' }))
    const needs = within(screen.getByRole('region', { name: 'Your repository needs' }))
    expect(needs.getAllByRole('listitem').map((item) => item.textContent)).toEqual([
      'Branch feature is created.', 'HEAD moves to feature.',
    ])
    expect(within(screen.getByRole('region', { name: 'Words to know' })).getByText('Branch')).toBeInTheDocument()
    await waitFor(() => expect(document.activeElement).toHaveAttribute('data-command-input'))
  })

  it('confirms a correct move with what changed, not colour alone', async () => {
    setup({
      ...tutor, phase: 'feedback', verdict: 'correct', explanation: "That's the right command.",
      changes: [{ kind: 'branch', text: 'Branch feature is created.' }], completion_token: 'token',
    })
    expect(await screen.findByRole('status')).toHaveTextContent("That's the right command.")
    const changed = within(screen.getByRole('region', { name: 'What changed' }))
    expect(changed.getByText('Branch feature is created.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Got it' })).toBeInTheDocument()
  })

  it('explains the command after a terminal mistake and persists acknowledgment to bootstrap', async () => {
    const { client, run } = setup(feedback)
    expect(await screen.findByText('git switch -c feature')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-tour-spotlight')).toHaveStyle({ top: '151px' })
    expect(screen.queryByRole('button', { name: 'Hide command guide' })).not.toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent("That wasn't the command this step needs.")
    fireEvent.click(screen.getByRole('tab', { name: 'What changes' }))
    expect(screen.getByRole('region', { name: 'It will' })).toBeInTheDocument()
    expect(commandIntroductionsApi.complete).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Got it' }))
    await waitFor(() => expect(commandIntroductionsApi.complete).toHaveBeenCalledWith(1, 'feedback-token'))
    await waitFor(() => expect(readTierRunBootstrap(1)?.tutor).toBeNull())
    expect(client.getQueryData(queryKeys.adventureTierRun(1))).toEqual({ ...run, tutor: null })
  })

  it('does not mark a hidden introduction completed', async () => {
    const { onDismiss } = setup()
    fireEvent.click(await screen.findByRole('button', { name: 'Hide command guide' }))
    expect(onDismiss).toHaveBeenCalledOnce()
    expect(commandIntroductionsApi.complete).not.toHaveBeenCalled()
  })

  it('does not clear a newer repository introduction when an old acknowledgment returns', async () => {
    let resolve!: (value: { tutor: null }) => void
    vi.mocked(commandIntroductionsApi.complete).mockReturnValue(new Promise((done) => { resolve = done }))
    const { client, run } = setup(feedback)
    fireEvent.click(await screen.findByRole('button', { name: 'Got it' }))
    const newer = { ...run, tutor: { ...tutor, context_id: 'snapshot-2' } }
    client.setQueryData(queryKeys.adventureTierRun(1), newer)
    await act(async () => { resolve({ tutor: null }) })
    expect(client.getQueryData(queryKeys.adventureTierRun(1))).toEqual(newer)
  })
})
