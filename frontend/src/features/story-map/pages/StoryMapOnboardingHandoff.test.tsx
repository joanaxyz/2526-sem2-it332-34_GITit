import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { OnboardingProvider } from '@/features/onboarding/components/OnboardingProvider'
import { onboardingStorageKey, writeOnboardingPhase } from '@/features/onboarding/utils/onboardingState'
import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import type {
  ChapterOrientationLessonDetail,
  ChapterOrientationLessonSummary,
} from '@/features/story-map/components/orientation/types'
import type { LearningChapter, Story } from '@/features/story-map/types'
import { useAuthStore } from '@/shared/auth/useAuth'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import { preferencesApi } from '@/shared/preferences/preferencesApi'

import { StoryMapPage } from './StoryMapPage'

const mocks = vi.hoisted(() => ({ usePlayerLoadout: vi.fn(), useStories: vi.fn() }))

vi.mock('@/features/story-map/hooks/useStories', () => ({ useStories: mocks.useStories }))
vi.mock('@/shared/player-loadout/usePlayerLoadout', () => ({ usePlayerLoadout: mocks.usePlayerLoadout }))
vi.mock('@/features/story-map/components/path/StoryAdventurePath', () => ({
  StoryAdventurePath: () => <div>Story path</div>,
}))

const chapter: LearningChapter = {
  adventure_level_count: 1, challenge_count: 0, chest_schedule: [], command_skill_count: 1,
  description: 'Learn the foundations.', id: 1, is_orientation: false, is_playable: true,
  level_completion: { denominator: 1, numerator: 0, value: 0 }, lock_reason: '', locked: false,
  number: 1, slug: 'foundations', sort_order: 1,
  story: { id: 1, slug: 'arcane-spire', title: 'The Arcane Spire', world_slug: 'arcane-spire' },
  title: 'Foundations',
}
const orientationChapter: LearningChapter = {
  ...chapter, adventure_level_count: 0, command_skill_count: 0, id: 0, is_orientation: true,
  level_completion: { denominator: 0, numerator: 0, value: 0 }, number: 0,
  slug: 'module-0-orientation', sort_order: 0, title: 'Module 0',
}
const story: Story = {
  completed: false, difficulty: 'beginner', id: 1, is_published: true, lock_reason: '',
  locked: false, prerequisite_story: null, slug: 'arcane-spire', sort_order: 1,
  summary: 'Learn Git foundations.', title: 'The Arcane Spire', world_slug: 'arcane-spire',
}

function lesson(id: number, isComplete: boolean): ChapterOrientationLessonSummary {
  return { id, slug: `topic-${id}`, title: `Topic ${id}`, subtitle: '', sort_order: id, is_complete: isComplete }
}

function lessonDetail(id: number, isComplete: boolean): ChapterOrientationLessonDetail {
  return {
    content_html: '', highest_step_seen: 0, id, interaction_steps: [], is_complete: isComplete,
    scoped_css: '', slug: `topic-${id}`, sort_order: id, subtitle: '', title: `Topic ${id}`,
  }
}

beforeEach(() => {
  localStorage.clear()
  useAuthStore.setState({
    accessToken: 'token',
    user: { id: 401, email: 'player@example.com', is_staff: false, username: 'player' },
  })
  // The tour only draws around a measurable spotlight target.
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
    x: 80, y: 100, left: 80, top: 100, right: 380, bottom: 260, width: 300, height: 160, toJSON: () => ({}),
  })
  mocks.useStories.mockReturnValue({ data: [story], isLoading: false, isError: false })
  mocks.usePlayerLoadout.mockReturnValue({
    companion: COMPANIONS.blue, companionSlug: 'blue', hasCompanion: false,
    isLoading: false, isError: false, error: null,
  })
  vi.spyOn(preferencesApi, 'get').mockResolvedValue({ motion_mode: 'system', onboarding_phase: 'orientation' })
  vi.spyOn(preferencesApi, 'update').mockImplementation(async (payload) => ({
    motion_mode: 'system', onboarding_phase: payload.onboarding_phase ?? 'orientation',
  }))
  vi.spyOn(storyMapApi, 'listChapters').mockResolvedValue([orientationChapter, chapter])
  vi.spyOn(storyMapApi, 'listOrientationLessons').mockResolvedValue([lesson(10, false)])
  vi.spyOn(storyMapApi, 'getOrientationLesson').mockResolvedValue(lessonDetail(10, false))
  vi.spyOn(storyMapApi, 'getChapterOverview').mockResolvedValue({
    chapter_id: chapter.id, adventures: [], lessons: [], challenges: [],
  })
})

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

function renderMap(userId = 401) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={['/stories/arcane-spire']}>
        <OnboardingProvider userId={userId}>
          <Routes><Route path="/stories/:storySlug" element={<StoryMapPage />} /></Routes>
        </OnboardingProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

// Module 0 is the one journey step a player can walk out of, so every exit has
// to hand the journey back to the story tour. Otherwise the account sits in
// "orientation" with no tutorial on screen and never reaches the Shop or Home.
describe('Module 0 hands the onboarding journey back', () => {
  it('opens the story tour when the player picks another chapter in the dropdown', async () => {
    writeOnboardingPhase(401, 'orientation')
    renderMap()
    expect(await screen.findByRole('heading', { name: 'Module 0' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /Choose chapter/ }))
    fireEvent.click(await screen.findByRole('button', { name: '01 Foundations' }))

    await waitFor(() => expect(screen.getByText('Story path')).toBeInTheDocument())
    expect(await screen.findByRole('heading', { name: 'Your Git journey starts here' })).toBeInTheDocument()
    expect(localStorage.getItem(onboardingStorageKey(401))).toBe('stories')
  })

  it('opens the story tour from the last topic even when earlier topics were skipped', async () => {
    writeOnboardingPhase(401, 'orientation')
    vi.mocked(storyMapApi.listOrientationLessons).mockResolvedValue([lesson(10, false), lesson(11, true)])
    vi.mocked(storyMapApi.getOrientationLesson).mockImplementation(async (id) => lessonDetail(id, id === 11))
    renderMap()

    fireEvent.click(await screen.findByRole('button', { name: /Topic 11/ }))
    fireEvent.click(await screen.findByRole('button', { name: /Continue to Module 1/ }))

    await waitFor(() => expect(screen.getByText('Story path')).toBeInTheDocument())
    expect(await screen.findByRole('heading', { name: 'Your Git journey starts here' })).toBeInTheDocument()
    expect(localStorage.getItem(onboardingStorageKey(401))).toBe('stories')
  })

  it('opens the story tour once every topic is complete', async () => {
    writeOnboardingPhase(401, 'orientation')
    vi.mocked(storyMapApi.listOrientationLessons).mockResolvedValue([lesson(10, true)])
    vi.mocked(storyMapApi.getOrientationLesson).mockResolvedValue(lessonDetail(10, true))
    renderMap()

    await waitFor(() => expect(screen.getByText('Story path')).toBeInTheDocument())
    expect(await screen.findByRole('heading', { name: 'Your Git journey starts here' })).toBeInTheDocument()
  })
})
