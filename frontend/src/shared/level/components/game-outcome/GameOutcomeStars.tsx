import { useState } from 'react'
import type { CSSProperties } from 'react'

import { cn } from '@/shared/utils/cn'
import { useLazyImage } from '@/shared/utils/useLazyImage'

import { STAR_REVEAL_DELAY_MS, STAR_REVEAL_STAGGER_MS, useStarRewardAudio } from './useStarRewardAudio'

// Each grade uses its original artwork. CSS crops its three star regions and
// footer into independently animated sprites; no replacement star art is drawn.
const STAR_ART_LOADERS = {
  lose: () => import('@/assets/images/battle-outcome/lose-0.webp'),
  'win-1': () => import('@/assets/images/battle-outcome/win-1.webp'),
  'win-2': () => import('@/assets/images/battle-outcome/win-2.webp'),
  'win-3': () => import('@/assets/images/battle-outcome/win-3.webp'),
}

/** Mount once per result so a reopened outcome replays its award sequence. */
export function GameOutcomeStars({ stars }: { stars: number }) {
  const artKey = stars === 0 ? 'lose' : `win-${stars}`
  const src = useLazyImage(artKey, STAR_ART_LOADERS)
  const [ready, setReady] = useState(false)
  const playRewardCue = useStarRewardAudio(stars, ready)

  return (
    <div
      className={cn('game-outcome-star-art', stars === 0 && 'is-empty', ready && 'is-ready')}
      role="img"
      aria-label={stars === 0 ? 'No stars earned' : `${stars} of 3 stars earned`}
      style={{
        '--outcome-star-image': src ? `url("${src}")` : undefined,
        '--outcome-star-count': stars,
        '--outcome-star-delay': `${STAR_REVEAL_DELAY_MS}ms`,
        '--outcome-star-stagger': `${STAR_REVEAL_STAGGER_MS}ms`,
      } as CSSProperties}
    >
      {src ? (
        <>
          <img
            className="game-outcome-star-source"
            src={src}
            width={1774}
            height={887}
            alt=""
            aria-hidden="true"
            onLoad={() => setReady(true)}
          />
          <div className="game-outcome-star-sprites" aria-hidden="true">
            {[0, 1, 2].map((index) => (
              <span
                key={index}
                className={cn('game-outcome-star-cell', index < stars && 'is-earned')}
                style={{ '--star-index': index } as CSSProperties}
                onAnimationStart={(event) => {
                  if (event.animationName === 'game-outcome-star-award-in' && index < stars) {
                    playRewardCue(index + 1)
                  } else if (event.animationName === 'game-outcome-star-unlit-in' && stars === 0 && index === 0) {
                    playRewardCue(0)
                  }
                }}
              >
                <span className="game-outcome-star-face game-outcome-star-rest" />
                {index < stars ? (
                  <>
                    <span className="game-outcome-star-face game-outcome-star-award" />
                    <span className="game-outcome-star-glint" />
                  </>
                ) : null}
              </span>
            ))}
            <span className="game-outcome-star-ornament" />
          </div>
        </>
      ) : null}
    </div>
  )
}
