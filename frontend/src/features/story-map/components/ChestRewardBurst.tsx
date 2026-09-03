import type { CSSProperties } from 'react'

import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

const SPARK_COLORS = ['rgb(var(--theme-primary-rgb))', 'rgb(var(--theme-spark-rgb))', 'hsl(var(--warning))']
const SPARK_COUNT = 10

const sparks = Array.from({ length: SPARK_COUNT }, (_, index) => {
  const angle = (index / SPARK_COUNT) * Math.PI * 2
  const radius = 24 + (index % 3) * 8
  return {
    color: SPARK_COLORS[index % SPARK_COLORS.length],
    delay: `${(index % 5) * 28}ms`,
    size: `${3 + (index % 3)}px`,
    x: `${Math.cos(angle) * radius}px`,
    y: `${Math.sin(angle) * radius}px`,
  }
})

/**
 * One-shot sparkle burst plus a floating "+N GitCoins" toast, played over a
 * progress-reward chest the moment its threshold is crossed. Mirrors the
 * CSS-custom-property particle technique from GameOutcomeConfetti, scaled
 * down to a small anchored burst instead of a full-screen layer.
 */
export function ChestRewardBurst({ coins }: { coins: number }) {
  return (
    <span className="story-reward-chest-burst" aria-hidden="true">
      <span className="story-reward-chest-sparkle-layer">
        {sparks.map((spark, index) => (
          <span
            className="story-reward-chest-sparkle"
            key={index}
            style={
              {
                '--spark-color': spark.color,
                '--spark-delay': spark.delay,
                '--spark-size': spark.size,
                '--spark-x': spark.x,
                '--spark-y': spark.y,
              } as CSSProperties
            }
          />
        ))}
      </span>
      {coins > 0 ? (
        <span className="story-reward-claim-toast">
          <GitCoinIcon className="story-reward-claim-coin-icon" />+{coins}
        </span>
      ) : null}
    </span>
  )
}
