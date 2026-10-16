import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import type { ChapterOrientationLessonDetail } from '@/features/story-map/components/orientation/types'
import type { LearningChapter } from '@/features/story-map/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'

import { OrientationLessonWorkspace } from './OrientationLessonWorkspace'

const chapter: LearningChapter = {
  adventure_level_count: 0,
  challenge_count: 0,
  chest_schedule: [],
  command_skill_count: 0,
  description: 'Optional Git foundations.',
  id: 10,
  is_orientation: true,
  is_playable: true,
  level_completion: { denominator: 0, numerator: 0, value: 0 },
  lock_reason: '',
  locked: false,
  number: 0,
  slug: 'module-0-orientation',
  sort_order: 0,
  story: { id: 1, slug: 'arcane-spire', title: 'Arcane Spire', world_slug: 'arcane-spire' },
  title: 'Git orientation',
}

const lesson: ChapterOrientationLessonDetail = {
  content_html: '',
  highest_step_seen: 0,
  id: 21,
  interaction_steps: [
    { id: 'mental-model', kind: 'continue', prompt: 'See what Git tracks.', title: 'Build the model' },
    { id: 'first-command', kind: 'continue', prompt: 'Try one command.', title: 'Run a command' },
  ],
  is_complete: false,
  scoped_css: '',
  slug: 'what-is-git-and-why-it-matters',
  sort_order: 0,
  subtitle: 'Two short steps',
  title: 'What Git changes',
}

function lessonSummary() {
  return {
    id: lesson.id,
    is_complete: false,
    slug: lesson.slug,
    sort_order: lesson.sort_order,
    subtitle: lesson.subtitle,
    title: lesson.title,
  }
}

function renderWorkspace(onLeaveModule = vi.fn(), preload = false) {
  const client = new QueryClient({
    defaultOptions: { mutations: { retry: false }, queries: { retry: false } },
  })
  if (preload) {
    client.setQueryData(queryKeys.orientationLessons(chapter.id), [lessonSummary()])
    client.setQueryData(queryKeys.orientationLesson(lesson.id), lesson)
  }
  const view = render(
    <QueryClientProvider client={client}>
      <OrientationLessonWorkspace chapter={chapter} onLeaveModule={onLeaveModule} />
    </QueryClientProvider>,
  )
  return { ...view, onLeaveModule }
}

beforeEach(() => {
  localStorage.clear()
  useAuthStore.setState({
    accessToken: 'token',
    sessionUserId: 44,
    user: { email: 'player@example.com', id: 44, is_staff: false, username: 'player' },
  })
  vi.spyOn(storyMapApi, 'listOrientationLessons').mockResolvedValue([lessonSummary()])
  vi.spyOn(storyMapApi, 'getOrientationLesson').mockResolvedValue(lesson)
})

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

describe('OrientationLessonWorkspace', () => {
  it('restores an unfinished step after the workspace remounts', async () => {
    const firstVisit = renderWorkspace()
    expect(await screen.findByRole('heading', { name: 'Build the model' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Understood — continue' }))
    expect(await screen.findByRole('heading', { name: 'Run a command' })).toBeInTheDocument()
    expect(screen.getByText('1 of 2 steps complete')).toBeInTheDocument()
    firstVisit.unmount()

    const resumed = renderWorkspace(vi.fn(), true)
    const renderedStepHeadings: string[] = []
    const observer = new MutationObserver(() => {
      resumed.container.querySelectorAll('.orientation-step-header h3').forEach((heading) => {
        renderedStepHeadings.push(heading.textContent ?? '')
      })
    })
    observer.observe(resumed.container, { childList: true, subtree: true })
    expect(await screen.findByRole('heading', { name: 'Run a command' })).toBeInTheDocument()
    observer.disconnect()
    expect(renderedStepHeadings).not.toContain('Build the model')
    expect(screen.getByRole('button', { name: 'Step 1: Build the model, complete' })).toBeInTheDocument()
    expect(screen.getByText('1 of 2 steps complete')).toBeInTheDocument()
  })

  it('lets the player leave the optional primer immediately', async () => {
    const onLeaveModule = vi.fn()
    renderWorkspace(onLeaveModule)

    fireEvent.click(await screen.findByRole('button', { name: 'Go to first quest' }))

    expect(onLeaveModule).toHaveBeenCalledOnce()
  })

  it('keeps the first-quest exit available when topics fail to load', async () => {
    const onLeaveModule = vi.fn()
    vi.mocked(storyMapApi.listOrientationLessons).mockRejectedValueOnce(new Error('Network unavailable'))
    renderWorkspace(onLeaveModule)

    expect(await screen.findByText('Could not load orientation lessons')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Go to first quest' }))
    expect(onLeaveModule).toHaveBeenCalledOnce()
  })
})
