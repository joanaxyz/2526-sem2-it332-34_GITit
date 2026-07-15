import { BookOpen, CheckCircle2, Ghost, Map as MapIcon, Swords } from 'lucide-react'
import { useState } from 'react'

import { ShopCarousel } from '@/features/shop/components/ShopCarousel'
import { StoryMonsterShowcase } from '@/features/shop/components/StoryMonsterShowcase'
import { actionDisabled, actionLabel, formatCoins, statusLabel, unlocksLabel, type ShopDisplayItem } from '@/features/shop/utils/shopDisplay'
import { EmptyState } from '@/shared/components/EmptyState'
import { environmentSlides, storyPreview, type EnvSlide, type StoryPreview } from '@/shared/story-worlds/storyPreviews'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

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

  if (!selectedStory) {
    return (
      <section className="shop-view shop-empty-panel">
        <EmptyState title="No stories available" description="The shop catalog has no story bundles right now." />
      </section>
    )
  }

  const slides = bundle ? environmentSlides(bundle) : []
  const selectedWorldSlug = worldSlugForStory(selectedStory)

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
                  <h2 className="shop-world-title">{story.label}</h2>
                  <p className="shop-world-sub">Story Map &amp; Battle World</p>
                </div>
              </article>
            )
          }}
        />
      </div>

      <StoryDetailPanel
        balance={balance}
        onAction={onAction}
        pending={pending}
        story={selectedStory}
        walletPending={walletPending}
      />

      <StoryContents bundle={bundle} slides={slides} story={selectedStory} worldSlug={selectedWorldSlug} key={selectedStory.slug} />
    </section>
  )
}

function StoryDetailPanel({
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
    <aside className="ref-panel shop-detail-panel">
      <p className="shop-detail-eyebrow">Story Bundle</p>
      <h1 id="story-shop-title">{story.label}</h1>
      <span className="shop-panel-rule" aria-hidden="true" />
      <div className="shop-includes-list">
        <span><BookOpen aria-hidden="true" /> Story chapters</span>
        <span><MapIcon aria-hidden="true" /> Map environment &amp; sky</span>
        <span><Swords aria-hidden="true" /> Battle parallax backdrops</span>
        <span><Ghost aria-hidden="true" /> Story monster roster</span>
      </div>
      {unlocksLabel(story.unlocks_story) ? (
        <p className="shop-unlocks-note">
          <MapIcon aria-hidden="true" />
          {unlocksLabel(story.unlocks_story)}
        </p>
      ) : null}
      <div className="shop-buy-block">
        <div className="shop-price-block">
          {story.price > 0 ? (
            <>
              <GitCoinIcon />
              <span>
                <strong>{formatCoins(story.price)}</strong>
                <small>GitCoins</small>
              </span>
            </>
          ) : (
            <span>
              <strong>Free</strong>
              <small>Included with your account</small>
            </span>
          )}
        </div>
        <button
          type="button"
          className="shop-primary-action"
          disabled={actionDisabled(story, pending, balance, walletPending)}
          onClick={() => onAction(story)}
        >
          {story.owned ? <CheckCircle2 aria-hidden="true" /> : null}
          {actionLabel(story, balance, walletPending)}
        </button>
      </div>
      <p className="shop-purchase-note">
        <span aria-hidden="true">i</span>
        Owned stories are permanent account unlocks. Entering a story controls its map, battle world, and monsters.
      </p>
    </aside>
  )
}

function StoryContents({
  bundle,
  slides,
  story,
  worldSlug,
}: {
  bundle: StoryPreview | undefined
  slides: EnvSlide[]
  story: ShopDisplayItem
  worldSlug: string
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

  const active = slides[Math.min(envIndex, slides.length - 1)]

  return (
    <section className="shop-contents-shelf" aria-label={`${story.label} contents`}>
      <div className="shop-contents-block shop-contents-block--env">
        <header className="shop-block-head">
          <span>Environments</span>
          <small>{active ? active.label : ''}</small>
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

      <StoryMonsterShowcase battleStageSrc={active?.src} storyLabel={story.label} worldSlug={worldSlug} />
    </section>
  )
}
