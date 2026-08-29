import { CheckCircle2, DoorOpen, Lock, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { Story } from '@/features/story-map/types'
import { Button } from '@/shared/components/Button'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'
import { storyPath } from '@/shared/navigation/routes'
import { cn } from '@/shared/utils/cn'

export function StoryCard({ story }: { story: Story }) {
  return (
    <article
      className={cn(
        'story-select-card',
        story.completed && 'is-complete',
        story.locked && 'is-locked',
      )}
    >
      <div className="story-select-card-glow" aria-hidden="true" />
      <div className="story-select-card-header">
        {story.locked ? (
          <span className="story-select-state is-locked">
            <Lock className="size-4" />
            Locked
          </span>
        ) : story.completed ? (
          <span className="story-select-state is-complete">
            <CheckCircle2 className="size-4" />
            Mastered
          </span>
        ) : (
          <span className="story-select-state is-open">
            <Sparkles className="size-4" />
            Open
          </span>
        )}
      </div>

      <div>
        <h2>{story.title}</h2>
        <p>{story.locked ? story.lock_reason || story.summary : story.summary}</p>
      </div>

      <div className="story-select-card-actions">
        {story.locked && !story.owned ? (
          <Button asChild>
            <Link to="/shop?tab=stories">
              <GitCoinIcon />
              Unlock for {story.price}
            </Link>
          </Button>
        ) : story.locked && story.prerequisite_story ? (
          <Button asChild>
            <Link to={storyPath(story.prerequisite_story.slug)}>
              <DoorOpen data-icon="inline-start" />
              Continue {story.prerequisite_story.title}
            </Link>
          </Button>
        ) : (
          <Button asChild>
            <Link to={storyPath(story.slug)}>
              <DoorOpen data-icon="inline-start" />
              Enter
            </Link>
          </Button>
        )}
      </div>
    </article>
  )
}
