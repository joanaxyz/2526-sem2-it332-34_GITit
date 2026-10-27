import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { commandIntroductionsApi, type CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import { CommandIntroductionPanel } from '@/features/story-map/components/CommandIntroductionPanel'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { readTierRunBootstrap } from '@/features/story-map/utils/tierRunBootstrap'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'

vi.mock('@/features/story-map/api/commandIntroductionsApi', () => ({
  commandIntroductionsApi: { complete: vi.fn() },
}))

const tutor: CommandIntroduction = {
  context_id: 'snapshot-1', teaching_key: 'form:git switch -c <branch>',
  help_token: 'guide-help-token',
  run_revision: 0, phase: 'introduction', title: 'Create and switch',
  needs: [
    { kind: 'branch', text: 'A branch pointer changes.', action: 'create', subjects: ['<branch>'] },
    { kind: 'head', text: 'HEAD changes where you are working.', action: 'move', subjects: ['<branch>'] },
  ],
  changes: [],
  anatomy: [
    { token: 'git', text: 'runs Git' },
    { token: 'switch', text: 'the Git command to run' },
    { token: '-c', text: 'create the branch first, then switch to it' },
    { token: '<branch>', text: 'you fill this in: the branch name' },
  ],
  verdict: null, explanation: null, completion_token: null,
  command_form: {
    teaching_key: 'form:git switch -c <branch>', usage_form: 'git switch -c <branch>',
    label: 'Create and switch', summary: 'Creates a branch and moves HEAD onto it.',
  },
}
const nothingToTeach = { tutor: null, command_guides: [], guide_elsewhere: null, tips: [] }
const feedback: CommandIntroduction = {
  ...tutor, phase: 'feedback', verdict: 'incorrect',
  explanation: "Review the syntax and placeholder meanings, then try your own values.",
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

function setup(lesson = tutor, replay = false) {
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
    <CommandIntroductionPanel run={run} tutor={lesson} replay={replay} onDismiss={onDismiss} />
  </QueryClientProvider>)
  return { client, run, onDismiss }
}

beforeEach(() => {
  localStorage.clear()
  useAuthStore.getState().setSession('learner-token', {
    id: 1, username: 'learner', email: 'learner@example.com', is_staff: false,
  })
  vi.mocked(commandIntroductionsApi.complete).mockResolvedValue(nothingToTeach)
})
afterEach(() => {
  cleanup()
  useAuthStore.getState().clearSession()
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
    expect(screen.getByRole('dialog', { name: 'Create and switch' }).querySelector('img')).toBeNull()
    expect(screen.getByRole('button', { name: 'Move command guide' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Resize command guide' })).toBeInTheDocument()
    expect(screen.getAllByRole('textbox')).toHaveLength(1)
    // Its chat starts as a launcher, so nothing covers the card.
    expect(screen.queryByRole('dialog', { name: 'Ask Git-It' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ask Git-It' })).toBeInTheDocument()
    expect(screen.getByText(tutor.command_form.summary)).toBeInTheDocument()
    // Absolute beginners: what each part means. New words are tips, not guide content.
    const parts = within(screen.getByLabelText('What each part means'))
    expect(parts.getByText('create the branch first, then switch to it')).toBeInTheDocument()
    // A miss never reveals the concrete solution command either.
    expect(screen.queryByText('git switch -c feature')).not.toBeInTheDocument()
    // Nothing to click through: the guide stays while the learner types, with a
    // single close button (the chat starts collapsed). On a narrow screen the
    // change sits in its own tab of the same card.
    expect(screen.getAllByRole('button', { name: /close/i })).toEqual([
      screen.getByRole('button', { name: 'Close command guide' }),
    ])
    expect(screen.queryByRole('button', { name: 'Got it' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', { name: 'What changes' }))
    const needs = within(screen.getByRole('region', { name: 'What this command does' }))
    expect(needs.getAllByRole('listitem').map((item) => item.textContent)).toEqual([
      'A branch pointer changes.', 'HEAD changes where you are working.',
    ])
    expect(screen.queryByRole('region', { name: 'Words to know' })).not.toBeInTheDocument()
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
    const { client, run, onDismiss } = setup(feedback)
    expect(await screen.findByText('Syntax: git switch -c <branch>')).toBeInTheDocument()
    expect(screen.queryByText('git switch -c feature')).not.toBeInTheDocument()
    expect(screen.getByTestId('workspace-tour-spotlight')).toHaveStyle({ top: '151px' })
    // Feedback waits for "Got it": no close button, and neither a click outside
    // nor Escape puts it away.
    expect(screen.queryByRole('button', { name: 'Close command guide' })).not.toBeInTheDocument()
    fireEvent.pointerDown(document.body)
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(onDismiss).not.toHaveBeenCalled()
    expect(screen.getByRole('status')).toHaveTextContent('Review the syntax and placeholder meanings')
    fireEvent.click(screen.getByRole('tab', { name: 'What changes' }))
    expect(screen.getByRole('region', { name: 'What this command does' })).toBeInTheDocument()
    expect(commandIntroductionsApi.complete).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Got it' }))
    await waitFor(() => expect(commandIntroductionsApi.complete).toHaveBeenCalledWith(1, 'feedback-token'))
    await waitFor(() => expect(readTierRunBootstrap(1)?.tutor).toBeNull())
    expect(client.getQueryData(queryKeys.adventureTierRun(1))).toEqual({ ...run, ...nothingToTeach })
  })

  it('stays open for clicks in its chat launcher, chat window and terminal, and collapses on a click elsewhere', async () => {
    const { onDismiss } = setup()
    await screen.findByText('Syntax: git switch -c <branch>')
    const chatLauncher = screen.getByRole('button', { name: 'Ask Git-It' })
    fireEvent.pointerDown(chatLauncher)
    fireEvent.click(chatLauncher)
    fireEvent.pointerDown(screen.getByRole('textbox', { name: 'Ask Git-It a question' }))
    fireEvent.pointerDown(document.querySelector('[data-command-input]')!)
    fireEvent.pointerDown(screen.getByRole('dialog', { name: 'Create and switch' }))
    expect(onDismiss).not.toHaveBeenCalled()
    fireEvent.pointerDown(document.body)
    expect(onDismiss).toHaveBeenCalledOnce()
    // Hiding an introduction is not completing it.
    expect(commandIntroductionsApi.complete).not.toHaveBeenCalled()
  })

  it('closes from its close button without completing the guide', async () => {
    const { onDismiss } = setup()
    fireEvent.click(await screen.findByRole('button', { name: 'Close command guide' }))
    expect(onDismiss).toHaveBeenCalledOnce()
    expect(commandIntroductionsApi.complete).not.toHaveBeenCalled()
  })

  it('collapses on Escape and hands focus back to the terminal', async () => {
    const { onDismiss } = setup()
    await screen.findByText('Syntax: git switch -c <branch>')
    fireEvent.keyDown(document.querySelector('[data-command-input]')!, { key: 'Escape' })
    expect(onDismiss).toHaveBeenCalledOnce()
    await waitFor(() => expect(document.activeElement).toHaveAttribute('data-command-input'))
  })

  it('reopens a saved guide as read-only reference', async () => {
    const { onDismiss } = setup(feedback, true)
    expect(await screen.findByText('Syntax: git switch -c <branch>')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Got it' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Close command guide' }))
    expect(onDismiss).toHaveBeenCalledOnce()
    expect(commandIntroductionsApi.complete).not.toHaveBeenCalled()
  })

  it('does not clear a newer repository introduction when an old acknowledgment returns', async () => {
    let resolve!: (value: typeof nothingToTeach) => void
    vi.mocked(commandIntroductionsApi.complete).mockReturnValue(new Promise((done) => { resolve = done }))
    const { client, run } = setup(feedback)
    fireEvent.click(await screen.findByRole('button', { name: 'Got it' }))
    const newer = { ...run, tutor: { ...tutor, context_id: 'snapshot-2' } }
    client.setQueryData(queryKeys.adventureTierRun(1), newer)
    await act(async () => { resolve(nothingToTeach) })
    expect(client.getQueryData(queryKeys.adventureTierRun(1))).toEqual(newer)
  })
})
