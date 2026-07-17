import { type CSSProperties, useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { PanelLeftOpen, PanelRightOpen, X } from 'lucide-react'

import { StoryAdventurePath } from '@/features/story-map/components/path/StoryAdventurePath'
import { ChapterOverview } from '@/features/story-map/components/ChapterOverview'
import { StoryChapterList } from '@/features/story-map/components/StoryChapterList'
import { StoryCompanionPanel, StorySkillFocusPanel } from '@/features/story-map/components/StorySidePanels'
import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import { useStories } from '@/features/story-map/hooks/useStories'
import { chapterTitle, firstOpenChapter } from '@/features/story-map/utils/storyMapChapter'
import { queryKeys } from '@/shared/api/queryKeys'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { STORIES_ROUTE } from '@/shared/navigation/routes'
import { getStoryWorld } from '@/shared/story-worlds/registry'
import { storyWorldStyle } from '@/shared/story-worlds/theme'

export function StoryMapPage() {
  const { storySlug: routeStorySlug } = useParams<{ storySlug: string }>()
  const storySlug = routeStorySlug ?? 'arcane-spire'
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
  const activeStory = useMemo(
    () => storiesQuery.data?.find((story) => story.slug === storySlug) ?? null,
    [storySlug, storiesQuery.data],
  )
  const { companion, companionSlug } = usePlayerLoadout()
  const storyWorld = useMemo(() => getStoryWorld(activeStory?.world_slug ?? storySlug), [activeStory?.world_slug, storySlug])
  const storyMapStyle = {
    ...storyWorldStyle(storyWorld),
    backgroundImage: `url("${storyWorld.map?.background.src ?? '/cosmetics/story-worlds/arcane-spire/backgrounds/level-map.png'}")`,
  } as CSSProperties
  const [activeChapterId, setActiveChapterId] = useState<number | null>(null)
  const [leftRailOpen, setLeftRailOpen] = useState(false)
  const [rightRailOpen, setRightRailOpen] = useState(false)

  useEffect(() => {
    if (!chapters.length) return

    setActiveChapterId((current) => {
      if (focusedChapterId && chapters.some((chapter) => chapter.id === focusedChapterId)) {
        return focusedChapterId
      }
      if (current && chapters.some((chapter) => chapter.id === current)) return current
      return firstOpenChapter(chapters)?.id ?? null
    })
  }, [chapters, focusedChapterId])

  useEffect(() => {
    setLeftRailOpen(false)
    setRightRailOpen(false)
  }, [activeChapterId, storySlug])

  const activeChapter = useMemo(
    () => chapters.find((chapter) => chapter.id === activeChapterId) ?? firstOpenChapter(chapters),
    [activeChapterId, chapters],
  )

  const overviewQuery = useQuery({
    queryKey: queryKeys.chapterOverview(activeChapter?.id ?? 0),
    queryFn: () => storyMapApi.getChapterOverview(activeChapter!.id),
    enabled: Boolean(activeChapter),
    staleTime: 2 * 60 * 1000,
  })

  if (chaptersQuery.isLoading) {
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
  const challengesLocked = activeChapter.locked || (adventures.length > 0 && adventures.some((adventure) => !adventure.is_passed))

  return (
    <div className="story-page-shell" style={storyWorldStyle(storyWorld)}>
      <div className="story-map-backdrop" style={storyMapStyle} aria-hidden="true" />

      <div className="story-map-rail-controls" aria-label="Map panels">
        <button
          type="button"
          aria-expanded={leftRailOpen}
          aria-controls="story-map-tools"
          onClick={() => setLeftRailOpen((open) => !open)}
        >
          <PanelLeftOpen aria-hidden="true" />
          Chapter tools
        </button>
        <button
          type="button"
          aria-expanded={rightRailOpen}
          aria-controls="story-map-utilities"
          onClick={() => setRightRailOpen((open) => !open)}
        >
          <PanelRightOpen aria-hidden="true" />
          Story utilities
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

      <div className="story-map-layout">
        <aside id="story-map-tools" className={`story-map-left ${leftRailOpen ? 'is-open' : ''}`} aria-label="Chapter tools">
          <button type="button" className="story-map-rail-close" aria-label="Close chapter tools" onClick={() => setLeftRailOpen(false)}>
            <X aria-hidden="true" />
          </button>
          <ChapterOverview chapter={{ ...activeChapter, title: chapterTitle(activeChapter) }} />
        </aside>

        <section className="story-map-stage" aria-label={`${activeStory?.title ?? 'Story'} chapter map`}>
          <div className="story-switcher story-switcher--map">
            <Link to={STORIES_ROUTE} className="story-link">
              Stories
            </Link>
            {activeStory ? <span>{activeStory.title}</span> : null}
          </div>

          <h1 className="story-map-title">{activeStory?.title ?? 'Story'}</h1>

          {overviewQuery.isError ? (
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

        <aside id="story-map-utilities" className={`story-map-right ${rightRailOpen ? 'is-open' : ''}`} aria-label="Story chapters and companion">
          <button type="button" className="story-map-rail-close" aria-label="Close story utilities" onClick={() => setRightRailOpen(false)}>
            <X aria-hidden="true" />
          </button>
          <StoryChapterList
            chapters={chapters}
            activeChapterId={activeChapter.id}
            onSelectChapter={setActiveChapterId}
          />
          <StorySkillFocusPanel
            levels={levels}
            companionSlug={companionSlug}
            companionLabel={companion.label}
            loading={overviewQuery.isLoading}
          />
          <StoryCompanionPanel companion={companion} />
        </aside>
      </div>
    </div>
  )
}
