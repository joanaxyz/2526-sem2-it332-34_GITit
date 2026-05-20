import { ArrowRight, BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'

export function CurrentTrackCard() {
  return (
    <Card className="overflow-hidden bg-gradient-to-br from-secondary to-card p-7">
      <div className="flex min-h-52 flex-col justify-between gap-6">
        <div>
          <div className="mb-4 inline-flex items-center gap-2 rounded-sm border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
            <BookOpen className="size-3" />
            Student practice track
          </div>
          <h1 className="max-w-3xl text-4xl font-extrabold leading-tight tracking-tight">
            Build Git confidence through Unit lessons, practice repo state, and replayable scenarios.
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
            Start with the Git foundations when you need them, then choose a practice topic and work from Easy toward Hard.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button asChild>
            <Link to="/units">
              Open Units
              <ArrowRight data-icon="inline-end" />
            </Link>
          </Button>
        </div>
      </div>
    </Card>
  )
}
