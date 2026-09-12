import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import type { LearningChapter, Story } from '@/features/story-map/types'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'

import { StoryMapPage } from './StoryMapPage'

const mocks = vi.hoisted(() => ({
  useAppOnboarding: vi.fn(),
  usePlayerLoadout: vi.fn(),
  useStories: vi.fn(),
}))

vi.mock('@/features/onboarding/hooks/onboardingContext', () => ({
  useAppOnboarding: mocks.useAppOnboarding,
}))

vi.mock('@/features/story-map/hooks/useStories', () => ({
  useStories: mocks.useStories,
}))

vi.mock('@/shared/player-loadout/usePlayerLoadout', () => ({
  usePlayerLoadout: mocks.usePlayerLoadout,
}))

vi.mock('@/features/story-map/components/ChapterOverview', () => ({
  ChapterOverview: () => <button type="button">Chapter drawer action</button>,
}))

vi.mock('@/features/story-map/components/StoryChapterList', () => ({
  StoryChapterList: ({ activeChapterId, onSelectChapter }: {
    activeChapterId: number
    onSelectChapter: (chapterId: number) => void
  }) => (
    <div>
      <span>Active chapter {activeChapterId}</span>
      <button type="button" onClick={() => onSelectChapter(0)}>Choose orientation</button>
    </div>
  ),
}))

vi.mock('@/features/story-map/components/orientation/OrientationLessonWorkspace', () => ({
  OrientationLessonWorkspace: () => <div>Orientation workspace</div>,
}))

vi.mock('@/features/story-map/components/StorySidePanels', () => ({
  StorySkillFocusPanel: () => <div>Skill focus</div>,
  StoryCompanionPanel: () => <div>Companion state</div>,
}))

vi.mock('@/features/story-map/components/path/StoryAdventurePath', () => ({
  StoryAdventurePath: () => <div>Story path</div>,
}))

const chapter: LearningChapter = {
  adventure_level_count: 1,
  challenge_count: 0,
  chest_schedule: [],
  command_skill_count: 1,
  description: 'Learn the foundations.',
  id: 1,
  is_orientation: false,
  is_playable: true,
  level_completion: { denominator: 1, numerator: 0, value: 0 },
  lock_reason: '',
  locked: false,
  number: 1,
  slug: 'foundations',
  sort_order: 1,
  story: { id: 1, slug: 'arcane-spire', title: 'The Arcane Spire', world_slug: 'arcane-spire' },
  title: 'Foundations',
}

const orientationChapter: LearningChapter = {
  ...chapter,
  adventure_level_count: 0,
  command_skill_count: 0,
  id: 0,
  is_orientation: true,
  level_completion: { denominator: 0, numerator: 0, value: 0 },
  number: 0,
  slug: 'module-0-orientation',
  sort_order: 0,
  title: 'Module 0',
}

const story: Story = {
  completed: false,
  difficulty: 'beginner',
  id: 1,
  is_published: true,
  lock_reason: '',
  locked: false,
  prerequisite_story: null,
  slug: 'arcane-spire',
  sort_order: 1,
  summary: 'Learn Git foundations.',
  title: 'The Arcane Spire',
  world_slug: 'arcane-spire',
}

function compactMatchMedia() {
  return {
    matches: true,
    media: '(max-width: 1120px)',
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }
}

describe('StoryMapPage responsive rails', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'matchMedia', {
      configurable: true,
      value: vi.fn(() => compactMatchMedia()),
    })
    mocks.useStories.mockReturnValue({ data: [story], isLoading: false, isError: false })
    mocks.useAppOnboarding.mockReturnValue({ phase: 'done', setPhase: vi.fn() })
    mocks.usePlayerLoadout.mockReturnValue({
      companion: COMPANIONS.blue,
      companionSlug: 'blue',
      hasCompanion: false,
      isLoading: false,
      isError: false,
      error: null,
    })
    vi.spyOn(storyMapApi, 'listChapters').mockResolvedValue([chapter])
    vi.spyOn(storyMapApi, 'listOrientationLessons').mockResolvedValue([])
    vi.spyOn(storyMapApi, 'getChapterOverview').mockResolvedValue({
      chapter_id: chapter.id,
      adventures: [],
      lessons: [],
      challenges: [],
    })
  })

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
  })

  it('keeps closed compact rails out of the accessibility tree and restores them when opened', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/stories/arcane-spire']}>
          <Routes>
            <Route path="/stories/:storySlug" element={<StoryMapPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await waitFor(() => expect(screen.getByText('Story path')).toBeInTheDocument())
    await waitFor(() => expect(storyMapApi.getChapterOverview).toHaveBeenCalledWith(chapter.id))
    const chapterRail = document.getElementById('story-map-tools')
    const utilityRail = document.getElementById('story-map-utilities')
    expect(chapterRail).toHaveAttribute('aria-hidden', 'true')
    expect(chapterRail).toHaveAttribute('inert')
    expect(utilityRail).toHaveAttribute('aria-hidden', 'true')
    expect(utilityRail).toHaveAttribute('inert')

    fireEvent.click(screen.getByRole('button', { name: 'Chapter tools' }))
    await waitFor(() => expect(chapterRail).not.toHaveAttribute('aria-hidden'))
    expect(chapterRail).not.toHaveAttribute('inert')
    expect(document.querySelector('.story-page-shell')).toHaveClass('story-page-shell--rail-open')
    fireEvent.click(within(chapterRail!).getByRole('button', { name: 'Close chapter tools' }))
    expect(chapterRail).toHaveAttribute('aria-hidden', 'true')
    expect(chapterRail).toHaveAttribute('inert')
    expect(document.querySelector('.story-page-shell')).not.toHaveClass('story-page-shell--rail-open')

    queryClient.clear()
  })

  it('opens Module 0 only when onboarding requests it and removes the story side cards', async () => {
    mocks.useAppOnboarding.mockReturnValue({ phase: 'orientation', setPhase: vi.fn() })
    vi.mocked(storyMapApi.listChapters).mockResolvedValue([orientationChapter, chapter])
    vi.mocked(storyMapApi.listOrientationLessons).mockResolvedValue([
      { id: 10, slug: 'git-basics', title: 'Git basics', subtitle: '', sort_order: 1, is_complete: false },
    ])
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/stories/arcane-spire']}>
          <Routes>
            <Route path="/stories/:storySlug" element={<StoryMapPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(await screen.findByText('Orientation workspace')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Chapters' }))
    expect(screen.getByText('Active chapter 0')).toBeInTheDocument()
    expect(screen.queryByText('Chapter drawer action')).not.toBeInTheDocument()
    expect(screen.queryByText('Skill focus')).not.toBeInTheDocument()
    expect(screen.queryByText('Companion state')).not.toBeInTheDocument()
    expect(storyMapApi.getChapterOverview).not.toHaveBeenCalled()
    queryClient.clear()
  })

  it('defaults to Module 1 when Module 0 was skipped', async () => {
    vi.mocked(storyMapApi.listChapters).mockResolvedValue([orientationChapter, chapter])
    vi.mocked(storyMapApi.listOrientationLessons).mockResolvedValue([
      { id: 10, slug: 'git-basics', title: 'Git basics', subtitle: '', sort_order: 1, is_complete: false },
    ])
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/stories/arcane-spire']}>
          <Routes>
            <Route path="/stories/:storySlug" element={<StoryMapPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await waitFor(() => expect(storyMapApi.getChapterOverview).toHaveBeenCalledWith(chapter.id))
    expect(screen.queryByText('Orientation workspace')).not.toBeInTheDocument()
    queryClient.clear()
  })

  it('defaults to Module 1 after every orientation lesson is complete', async () => {
    const setPhase = vi.fn()
    mocks.useAppOnboarding.mockReturnValue({ phase: 'orientation', setPhase })
    vi.mocked(storyMapApi.listChapters).mockResolvedValue([orientationChapter, chapter])
    vi.mocked(storyMapApi.listOrientationLessons).mockResolvedValue([
      { id: 10, slug: 'git-basics', title: 'Git basics', subtitle: '', sort_order: 1, is_complete: true },
    ])
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/stories/arcane-spire']}>
          <Routes>
            <Route path="/stories/:storySlug" element={<StoryMapPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await waitFor(() => expect(storyMapApi.getChapterOverview).toHaveBeenCalledWith(chapter.id))
    await waitFor(() => expect(setPhase).toHaveBeenCalledWith('stories'))
    expect(screen.queryByText('Orientation workspace')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Story utilities' }))
    expect(screen.getByText('Active chapter 1')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Choose orientation' }))
    expect(await screen.findByText('Orientation workspace')).toBeInTheDocument()
    queryClient.clear()
  })
})
