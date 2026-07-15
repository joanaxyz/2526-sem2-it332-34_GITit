import { GitBranch } from 'lucide-react'

import { StoryCard } from '@/features/story-map/components/StoryCard'
import { useStories } from '@/features/story-map/hooks/useStories'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function StorySelectPage() {
  const stories = useStories()

  if (stories.isLoading) {
    return <LoadingState description="Reading the story registry." label="Loading stories" variant="page" />
  }

  if (stories.isError) {
    return <ErrorState title="Could not load stories" description={stories.error.message} />
  }

  const items = stories.data ?? []
  if (!items.length) {
    return <EmptyState title="No stories available" description="Publish a curriculum story to start learning." />
  }

  return (
    <section className="story-select-page" aria-labelledby="story-select-title">
      <div className="story-select-header">
        <span className="story-select-sigil">
          <GitBranch className="size-5" />
        </span>
        <div>
          <h1 id="story-select-title">Choose a Story</h1>
          <p>Follow the foundations path, then unlock deeper Git disciplines as you progress.</p>
        </div>
      </div>

      <div className="story-select-grid">
        {items.map((story) => (
          <StoryCard key={story.id} story={story} />
        ))}
      </div>

    </section>
  )
}
