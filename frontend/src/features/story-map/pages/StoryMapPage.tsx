import { type CSSProperties, useEffect, useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, useSearchParams } from 'react-router-dom'
import { PanelLeftOpen, PanelRightOpen, X } from 'lucide-react'

import { StoryAdventurePath } from '@/features/story-map/components/path/StoryAdventurePath'
import { useAppOnboarding } from '@/features/onboarding/hooks/onboardingContext'
import { ChapterOverview } from '@/features/story-map/components/ChapterOverview'
import { OrientationLessonWorkspace } from '@/features/story-map/components/orientation/OrientationLessonWorkspace'
import { StoryChapterList } from '@/features/story-map/components/StoryChapterList'
import { StoryOnboarding } from '@/features/story-map/components/StoryOnboarding'
import { StoryCompanionPanel, StorySkillFocusPanel } from '@/features/story-map/components/StorySidePanels'
import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import { useStories } from '@/features/story-map/hooks/useStories'
import { chapterTitle, firstOpenChapter } from '@/features/story-map/utils/storyMapChapter'
import { queryKeys } from '@/shared/api/queryKeys'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { useAuthStore } from '@/shared/auth/useAuth'
import { getStoryWorld } from '@/shared/story-worlds/registry'
import { storyWorldStyle } from '@/shared/story-worlds/theme'

const COMPACT_STORY_MAP_QUERY = '(max-width: 1120px)'

function useCompactStoryMap() {
  const [compact, setCompact] = useState(
    () => typeof window !== 'undefined' && typeof window.matchMedia === 'function'
      ? window.matchMedia(COMPACT_STORY_MAP_QUERY).matches
      : false,
  )

  useEffect(() => {
    if (typeof window.matchMedia !== 'function') return
    const media = window.matchMedia(COMPACT_STORY_MAP_QUERY)
    const update = () => setCompact(media.matches)
    update()
    media.addEventListener('change', update)
    return () => media.removeEventListener('change', update)
  }, [])

  return compact
}

export function StoryMapPage() {
  const userId = useAuthStore((state) => state.user?.id)
  const onboarding = useAppOnboarding()
  const { storySlug: routeStorySlug } = useParams<{ storySlug: string }>()
  const storySlug = routeStorySlug ?? 'git-it-legacy'
  const [searchParams] = useSearchParams()
  const chapterParam = searchParams.get('chapter')
  const focusedChapterId = chapterParam ? Number(chapterParam) : null

  const chaptersQuery = useQuery({
    queryKey: queryKeys.storyChapters(storySlug),
    queryFn: () => storyMapApi.listChapters(storySlug),
    staleTime: 5 * 60 * 1000,
  })
  const storiesQuery = useStories()

  const chapters = useMemo(() => chaptersQuery.data ?? [], [chaptersQuery.data])
  const orientationChapter = useMemo(
    () => chapters.find((chapter) => chapter.is_orientation) ?? null,
    [chapters],
  )
  const orientationPhaseActive = onboarding?.phase === 'orientation'
  const orientationLessonsQuery = useQuery({
    queryKey: queryKeys.orientationLessons(orientationChapter?.id),
    queryFn: () => storyMapApi.listOrientationLessons(orientationChapter!.id),
    enabled: Boolean(orientationChapter && orientationPhaseActive),
    staleTime: 60 * 1000,
  })
  const orientationComplete = Boolean(
    orientationLessonsQuery.data?.length && orientationLessonsQuery.data.every((lesson) => lesson.is_complete),
  )
  const activeStory = useMemo(
    () => storiesQuery.data?.find((story) => story.slug === storySlug) ?? null,
    [storySlug, storiesQuery.data],
  )
  const { companion, companionSlug, hasCompanion, isLoading: loadoutLoading, isError: loadoutError } = usePlayerLoadout()
  const storyWorld = useMemo(() => getStoryWorld(activeStory?.world_slug ?? storySlug), [activeStory?.world_slug, storySlug])
  const storyMapStyle = {
    ...storyWorldStyle(storyWorld),
    backgroundImage: `url("${storyWorld.map?.background.src ?? '/cosmetics/story-worlds/arcane-spire/backgrounds/level-map.png'}")`,
  } as CSSProperties
  const [activeChapterId, setActiveChapterId] = useState<number | null>(null)
  const userSelectedChapterId = useRef<number | null>(null)
  const [leftRailOpen, setLeftRailOpen] = useState(false)
  const [rightRailOpen, setRightRailOpen] = useState(false)
  const compactStoryMap = useCompactStoryMap()
  const orientationRequested = orientationPhaseActive && !orientationComplete

  useEffect(() => {
    if (!chapters.length || (orientationRequested && orientationLessonsQuery.isPending)) return

    setActiveChapterId((current) => {
      if (focusedChapterId && chapters.some((chapter) => chapter.id === focusedChapterId)) {
        return focusedChapterId
      }
      if (current != null && chapters.some((chapter) => chapter.id === current)) {
        if (
          !orientationRequested
          && current === orientationChapter?.id
          && userSelectedChapterId.current !== current
        ) {
          return firstOpenChapter(chapters, true)?.id ?? current
        }
        if (
          orientationRequested
          && orientationChapter
          && current !== orientationChapter.id
          && userSelectedChapterId.current == null
        ) {
          return orientationChapter.id
        }
        return current
      }
      return firstOpenChapter(chapters, !orientationRequested)?.id ?? null
    })
  }, [chapters, focusedChapterId, orientationChapter, orientationLessonsQuery.isPending, orientationRequested])

  useEffect(() => {
    if (!orientationComplete || onboarding?.phase !== 'orientation') return
    onboarding.setPhase('stories')
    userSelectedChapterId.current = null
    setActiveChapterId(firstOpenChapter(chapters, true)?.id ?? null)
  }, [chapters, onboarding, orientationComplete])

  useEffect(() => {
    setLeftRailOpen(false)
    setRightRailOpen(false)
  }, [activeChapterId, storySlug])

  const activeChapter = useMemo(
    () => chapters.find((chapter) => chapter.id === activeChapterId) ?? firstOpenChapter(chapters, !orientationRequested),
    [activeChapterId, chapters, orientationRequested],
  )

  const overviewQuery = useQuery({
    queryKey: queryKeys.chapterOverview(activeChapter?.id ?? 0),
    queryFn: () => storyMapApi.getChapterOverview(activeChapter!.id),
    // Orientation chapters carry no AdventureLevel/ChallengeLevel content, so
    // their overview would always resolve to empty arrays - skip the request
    // and route them to OrientationLessonWorkspace instead (see render below).
    enabled: Boolean(activeChapter) && !activeChapter?.is_orientation,
    staleTime: 2 * 60 * 1000,
  })

  if (chaptersQuery.isLoading || (orientationRequested && orientationLessonsQuery.isPending)) {
    return <LoadingState companionSlug={companionSlug} description="Preparing the story map." label="Loading map" variant="page" />
  }
  if (chaptersQuery.isError) {
    return <ErrorState title="Could not load map" description={chaptersQuery.error.message} />
  }
  if (!chapters.length || !activeChapter) {
    return <EmptyState title="No map available" description="Publish chapters to start learning." />
  }

  const overview = overviewQuery.data ?? null
  const adventures = overview?.adventures ?? []
  const challenges = overview?.challenges ?? []
  const levels = adventures
  const challengesLocked = activeChapter.locked
  const leftRailHidden = compactStoryMap && !leftRailOpen
  const rightRailHidden = compactStoryMap && !rightRailOpen
  const showingOrientation = activeChapter.is_orientation
  const selectChapter = (chapterId: number) => {
    userSelectedChapterId.current = chapterId
    setActiveChapterId(chapterId)
  }
  const selectFirstStoryChapter = () => {
    userSelectedChapterId.current = null
    setActiveChapterId(firstOpenChapter(chapters, true)?.id ?? null)
  }
  const selectOrientationChapter = () => {
    if (!orientationChapter) return
    userSelectedChapterId.current = orientationChapter.id
    setActiveChapterId(orientationChapter.id)
  }

  return (
    <div
      className={`story-page-shell ${compactStoryMap && (leftRailOpen || rightRailOpen) ? 'story-page-shell--rail-open' : ''}`}
      style={storyWorldStyle(storyWorld)}
    >
      <div className="story-map-backdrop" style={storyMapStyle} aria-hidden="true" />

      <div className="story-map-rail-controls" aria-label="Map panels">
        {!showingOrientation ? <button
          type="button"
          aria-expanded={leftRailOpen}
          aria-controls="story-map-tools"
          onClick={() => setLeftRailOpen((open) => !open)}
        >
          <PanelLeftOpen aria-hidden="true" />
          Chapter tools
        </button> : null}
        <button
          type="button"
          aria-expanded={rightRailOpen}
          aria-controls="story-map-utilities"
          onClick={() => setRightRailOpen((open) => !open)}
        >
          <PanelRightOpen aria-hidden="true" />
          {showingOrientation ? 'Chapters' : 'Story utilities'}
        </button>
      </div>

      {(leftRailOpen || rightRailOpen) ? (
        <button
          type="button"
          className="story-map-rail-backdrop"
          aria-label="Close map panels"
          onClick={() => { setLeftRailOpen(false); setRightRailOpen(false) }}
        />
      ) : null}

      <div className={`story-map-layout ${showingOrientation ? 'story-map-layout--orientation' : ''}`}>
        {!showingOrientation ? <aside
          id="story-map-tools"
          className={`story-map-left ${leftRailOpen ? 'is-open' : ''}`}
          aria-label="Chapter tools"
          aria-hidden={leftRailHidden || undefined}
          inert={leftRailHidden || undefined}
        >
          <button type="button" className="story-map-rail-close" aria-label="Close chapter tools" onClick={() => setLeftRailOpen(false)}>
            <X aria-hidden="true" />
          </button>
          <ChapterOverview chapter={{ ...activeChapter, title: chapterTitle(activeChapter) }} />
        </aside> : null}

        <section
          className={`story-map-stage ${showingOrientation ? 'story-map-stage--orientation' : ''}`}
          aria-label={showingOrientation ? `${activeStory?.title ?? 'Story'} onboarding` : `${activeStory?.title ?? 'Story'} chapter map`}
          data-onboarding={!showingOrientation ? 'stories' : undefined}
        >
          {userId != null ? (
            <StoryOnboarding
              key={userId}
              ready={!showingOrientation && Boolean(overview) && !overviewQuery.isError && !loadoutLoading && !loadoutError}
              compact={compactStoryMap}
              hasCompanion={hasCompanion}
              orientationAvailable={Boolean(orientationChapter)}
              onStartOrientation={selectOrientationChapter}
              onSkipOrientation={selectFirstStoryChapter}
            />
          ) : null}

          <h1 className="story-map-title">{activeStory?.title ?? 'Story'}</h1>

          {activeChapter.is_orientation ? (
            <OrientationLessonWorkspace chapter={activeChapter} />
          ) : overviewQuery.isError ? (
            <ErrorState title="Could not load chapter levels" description={overviewQuery.error.message} />
          ) : (
            <StoryAdventurePath
              chapter={activeChapter}
              levels={levels}
              challenges={challenges}
              challengesLocked={challengesLocked}
              loading={overviewQuery.isLoading}
            />
          )}
        </section>

        <aside
          id="story-map-utilities"
          className={`story-map-right ${showingOrientation ? 'story-map-right--orientation' : ''} ${rightRailOpen ? 'is-open' : ''}`}
          aria-label={showingOrientation ? 'Chapters' : 'Story chapters and companion'}
          aria-hidden={rightRailHidden || undefined}
          inert={rightRailHidden || undefined}
        >
          <button
            type="button"
            className="story-map-rail-close"
            aria-label={showingOrientation ? 'Close chapters' : 'Close story utilities'}
            onClick={() => setRightRailOpen(false)}
          >
            <X aria-hidden="true" />
          </button>
          {!rightRailHidden ? (
            <>
              <StoryChapterList
                chapters={chapters}
                activeChapterId={activeChapter.id}
                onSelectChapter={selectChapter}
              />
              {!showingOrientation ? <StorySkillFocusPanel
                levels={levels}
                companionSlug={hasCompanion ? companionSlug : null}
                companionLabel={hasCompanion ? companion.label : null}
                loading={overviewQuery.isLoading}
              /> : null}
              {!showingOrientation ? <StoryCompanionPanel companion={hasCompanion ? companion : null} /> : null}
            </>
          ) : null}
        </aside>
      </div>
    </div>
  )
}
