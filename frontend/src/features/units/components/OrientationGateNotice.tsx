import { ShieldAlert } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'

export function OrientationGateNotice({ complete }: { complete: boolean }) {
  if (complete) return null
  return (
    <Card className="border-amber-400/30 bg-amber-400/10 p-4 shadow-none">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-start gap-3">
          <ShieldAlert className="mt-0.5 size-5 text-amber-300" />
          <div>
            <div className="font-semibold text-amber-100">Orientation gate active</div>
            <p className="mt-1 text-sm leading-6 text-amber-100/80">
              Complete all Unit 1 lessons before starting your first scenario session.
            </p>
          </div>
        </div>
        <Button asChild variant="outline" size="sm">
          <Link to="/units">Open Unit 1</Link>
        </Button>
      </div>
    </Card>
  )
}
