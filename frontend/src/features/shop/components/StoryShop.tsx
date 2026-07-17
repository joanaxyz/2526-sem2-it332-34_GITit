import { CheckCircle2 } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { ShopCarousel } from '@/features/shop/components/ShopCarousel'
import { StoryMonsterShowcase } from '@/features/shop/components/StoryMonsterShowcase'
import { actionDisabled, compactActionLabel, statusLabel, type ShopDisplayItem } from '@/features/shop/utils/shopDisplay'
import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import type { LearningChapter } from '@/features/story-map/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { EmptyState } from '@/shared/components/EmptyState'
import { environmentSlides, storyPreview, type EnvSlide, type StoryPreview } from '@/shared/story-worlds/storyPreviews'

/* Stories ----------------------------------------------------------------- */


function previewForStory(story: ShopDisplayItem | undefined): StoryPreview | undefined {
  if (!story) return undefined
  return storyPreview(story.unlocks_story?.world_slug ?? story.slug)
}

function worldSlugForStory(story: ShopDisplayItem): string {
  return story.unlocks_story?.world_slug ?? story.slug
}

export function StoryShop({
  balance,
  onAction,
  pending,
  stories,
  walletPending,
}: {
  balance: number
  onAction: (item: ShopDisplayItem) => void
  pending: boolean
  stories: ShopDisplayItem[]
  walletPending: boolean
}) {
  const [index, setIndex] = useState(0)
  const selectedStory = stories[Math.min(index, stories.length - 1)]
  const bundle = previewForStory(selectedStory)
  const selectedStorySlug = selectedStory ? worldSlugForStory(selectedStory) : null
  const chapters = useQuery({
    queryKey: queryKeys.storyChapters(selectedStorySlug),
    queryFn: () => storyMapApi.listChapters(selectedStorySlug),
    enabled: Boolean(selectedStorySlug),
    staleTime: 60 * 1000,
  })

  if (!selectedStory) {
    return (
      <section className="shop-view shop-empty-panel">
        <EmptyState title="No stories available" description="The shop catalog has no story bundles right now." />
      </section>
    )
  }

  const slides = bundle ? environmentSlides(bundle) : []
  const selectedWorldSlug = worldSlugForStory(selectedStory)
  const scope = chapters.data ? chapterScope(chapters.data) : null

  return (
    <section className="shop-view shop-view--stories" aria-labelledby="story-shop-title">
      <div className="shop-stage" data-tone={selectedStory.tone}>
        <ShopCarousel
          className="shop-story-carousel"
          ariaLabel="Story worlds"
          items={stories}
          index={index}
          onIndexChange={setIndex}
          getKey={(story) => story.slug}
          renderSlide={(story, _i, active) => {
            const storyBundle = previewForStory(story)
            return (
              <article className="shop-world-slide" data-tone={story.tone} data-active={active}>
                <div className="shop-world-art">
                  {storyBundle ? <img src={storyBundle.storyMap} alt={`${story.label} map`} loading="lazy" /> : null}
                </div>
                <div className="shop-world-caption">
                  <span className="shop-status-chip" data-state={story.owned ? 'owned' : 'locked'}>
                    {statusLabel(story)}
                  </span>
                  <h2 id={active ? 'story-shop-title' : undefined} className="shop-world-title">{story.label}</h2>
                  <p className="shop-world-sub">Story Map &amp; Battle World</p>
                </div>
              </article>
            )
          }}
        />
        <StoryActionDock
          balance={balance}
          onAction={onAction}
          pending={pending}
          story={selectedStory}
          walletPending={walletPending}
        />
      </div>

      <StoryMonsterShowcase storyLabel={selectedStory.label} worldSlug={selectedWorldSlug} key={`monsters-${selectedStory.slug}`} />

      <StoryContents
        bundle={bundle}
        scope={scope}
        slides={slides}
        story={selectedStory}
        key={`environments-${selectedStory.slug}`}
      />
    </section>
  )
}

function StoryActionDock({
  balance,
  onAction,
  pending,
  story,
  walletPending,
}: {
  balance: number
  onAction: (item: ShopDisplayItem) => void
  pending: boolean
  story: ShopDisplayItem
  walletPending: boolean
}) {
  return (
    <div className="shop-stage-action-dock" aria-label={`${story.label} purchase status`}>
      <button
        type="button"
        className="shop-stage-action-button"
        disabled={actionDisabled(story, pending, balance, walletPending)}
        onClick={() => onAction(story)}
      >
        {story.owned ? <CheckCircle2 aria-hidden="true" /> : null}
        {compactActionLabel(story, balance, walletPending)}
      </button>
    </div>
  )
}

function StoryContents({
  bundle,
  scope,
  slides,
  story,
}: {
  bundle: StoryPreview | undefined
  scope: StoryScope | null
  slides: EnvSlide[]
  story: ShopDisplayItem
}) {
  // Start the gallery on the first battle backdrop so it doesn't just echo the
  // story map already shown in the hero carousel above.
  const [envIndex, setEnvIndex] = useState(() => (slides.length > 1 ? 1 : 0))
  if (!bundle) {
    return (
      <section className="shop-contents-shelf shop-contents-shelf--empty">
        <EmptyState title="No preview assets" description="This story is listed, but no local preview art is registered yet." />
      </section>
    )
  }

  const battleEnvironmentCount = slides.filter((slide) => slide.kind === 'battle').length

  return (
    <section className="shop-contents-shelf" aria-label={`${story.label} contents`}>
      <div className="shop-contents-block shop-contents-block--env">
        <header className="shop-block-head">
          <span>Environments</span>
          <small className="shop-story-scope">
            {scope ? (
              <>
                <span>{scope.chapters} chapters</span>
                <span>{scope.adventures} adventure levels</span>
                <span>{scope.challenges} challenges</span>
              </>
            ) : (
              <span>{battleEnvironmentCount} battle {battleEnvironmentCount === 1 ? 'scene' : 'scenes'}</span>
            )}
          </small>
        </header>
        <ShopCarousel
          className="shop-env-carousel"
          ariaLabel={`${story.label} battle parallax and environments`}
          items={slides}
          index={envIndex}
          onIndexChange={setEnvIndex}
          getKey={(slide) => slide.key}
          renderSlide={(slide) => (
            <article className="shop-env-slide">
              <img src={slide.src} alt={slide.label} loading="lazy" />
              <span>{slide.label}</span>
            </article>
          )}
        />
      </div>
    </section>
  )
}

type StoryScope = { chapters: number; adventures: number; challenges: number }

function chapterScope(chapters: LearningChapter[]): StoryScope {
  return chapters.reduce<StoryScope>(
    (scope, chapter) => ({
      chapters: scope.chapters + 1,
      adventures: scope.adventures + chapter.adventure_level_count,
      challenges: scope.challenges + chapter.challenge_count,
    }),
    { chapters: 0, adventures: 0, challenges: 0 },
  )
}
