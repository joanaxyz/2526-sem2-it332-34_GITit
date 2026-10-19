import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check } from 'lucide-react'
import { useState } from 'react'

import rewardChestActiveImage from '@/assets/images/chest_active.png'
import rewardChestNormalImage from '@/assets/images/chest_normal.png'
import rewardChestOpenImage from '@/assets/images/chest_open.png'
import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import type { LearningChapter } from '@/features/story-map/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { GamePanel } from '@/shared/components/GamePanel'
import { Modal } from '@/shared/components/Modal'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

export function ChapterProgressRewards({ chapter, preview = false }: {
  chapter: LearningChapter
  preview?: boolean
}) {
  const queryClient = useQueryClient()
  const [selected, setSelected] = useState<{ threshold: number; coinsAwarded: number } | null>(null)
  const rewards = useQuery({
    queryKey: queryKeys.chapterChests(chapter.id),
    queryFn: () => storyMapApi.getChapterChests(chapter.id),
    enabled: !preview && !chapter.locked && chapter.chest_schedule.length > 0,
  })
  const openChest = useMutation({
    mutationFn: (threshold: number) => storyMapApi.openChapterChest(chapter.id, threshold),
    onSuccess: (summary, threshold) => {
      queryClient.setQueryData(queryKeys.chapterChests(chapter.id), summary)
      void queryClient.invalidateQueries({ queryKey: queryKeys.wallet })
      void queryClient.invalidateQueries({ queryKey: queryKeys.homeSummary })
      setSelected({ threshold, coinsAwarded: summary.coins_awarded })
    },
  })
  const chests = [...chapter.chest_schedule].sort((a, b) => a.threshold - b.threshold).map((chest) => {
    const saved = !chapter.locked ? rewards.data?.results.find((row) => row.threshold === chest.threshold) : undefined
    const previewEarned = preview && chapter.level_completion.value >= chest.threshold
    return {
      ...chest,
      unlocked: preview ? previewEarned : saved?.unlocked ?? false,
      claimed: preview ? previewEarned : saved?.claimed ?? false,
    }
  })
  const selectedChest = chests.find((chest) => chest.threshold === selected?.threshold)
  const checking = !preview && !chapter.locked && rewards.isPending

  return (
    <GamePanel as="section" eyebrow="Progress Rewards" className="story-skill-reward-panel">
      <p className="story-reward-help">GitCoins are added at each milestone. Open an earned chest for details.</p>
      <div className="story-skill-reward-grid" aria-label={`${chapter.title} progress rewards`} aria-busy={checking}>
        {chests.map((chest) => {
          const earned = chest.claimed || chest.unlocked
          const pending = openChest.isPending && openChest.variables === chest.threshold
          const label = checking ? 'Checking…' : chest.claimed ? 'Collected' : chest.unlocked ? 'Open chest' : 'Locked'
          return (
            <button
              type="button"
              className="story-skill-reward"
              data-earned={earned}
              data-claimed={chest.claimed}
              key={chest.threshold}
              disabled={!earned || checking || openChest.isPending}
              aria-label={`${chest.threshold}% chest: ${pending ? 'Opening' : label}, ${chest.coins} GitCoins`}
              title={earned ? `${chest.coins} GitCoins at ${chest.threshold}% completion` : `Reach ${chest.threshold}% chapter completion`}
              onClick={() => {
                openChest.reset()
                if (chest.claimed) setSelected({ threshold: chest.threshold, coinsAwarded: 0 })
                else openChest.mutate(chest.threshold)
              }}
            >
              <span className="story-reward-chest" aria-hidden="true">
                <img src={chest.claimed ? rewardChestOpenImage : chest.unlocked ? rewardChestActiveImage : rewardChestNormalImage} alt="" />
              </span>
              <span className="story-skill-threshold">
                {chest.claimed ? <Check aria-hidden="true" /> : null}{chest.threshold}%
              </span>
              <span className="story-skill-reward-amount"><GitCoinIcon className="size-3" />+{chest.coins}</span>
              {label !== 'Locked' ? (
                <span className="story-reward-status">{pending ? 'Opening…' : label}</span>
              ) : null}
            </button>
          )
        })}
      </div>
      {rewards.isError && !preview ? (
        <div className="story-reward-feedback" role="alert">
          <p>Could not check chest rewards.</p>
          <Button type="button" variant="ghost" size="sm" onClick={() => void rewards.refetch()}>Retry rewards</Button>
        </div>
      ) : null}
      {openChest.isError ? <p className="story-reward-feedback" role="alert">{openChest.error.message || 'Could not open this chest. Try again.'}</p> : null}
      <Modal
        open={Boolean(selectedChest)}
        title={`${selected?.threshold}% progress chest`}
        className="story-reward-reveal-shell"
        contentClassName="story-reward-reveal-content"
        overlayClassName="game-outcome-backdrop story-reward-reveal-backdrop"
        hideHeader
        dismissOnClick
        onClose={() => setSelected(null)}
      >
        {selectedChest ? (
          <div className="story-reward-reveal">
            <p className="story-reward-reveal-milestone">{selectedChest.threshold}% milestone</p>
            <img src={rewardChestOpenImage} alt="Opened reward chest filled with GitCoins" draggable={false} />
            <h3 className="story-reward-reveal-title"><span>+{selectedChest.coins}</span> GitCoins</h3>
            <p className="story-reward-reveal-status">{preview ? 'Preview reward · Earned by playing the chapter.' : selected?.coinsAwarded ? 'Reward collected! GitCoins added to your wallet.' : 'Reward collected · Already in your wallet.'}</p>
            <p className="story-reward-reveal-hint">Click anywhere to close<span className="sr-only">, or press Enter, Space, or Escape.</span></p>
          </div>
        ) : null}
      </Modal>
    </GamePanel>
  )
}
