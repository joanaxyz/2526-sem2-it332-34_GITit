import { ChevronDown } from 'lucide-react'

import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

export function ExpandToggleButton({
  expanded,
  controlsId,
  label,
  onToggle,
}: {
  expanded: boolean
  controlsId: string
  label: string
  onToggle: () => void
}) {
  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      aria-expanded={expanded}
      aria-controls={controlsId}
      aria-label={expanded ? `Collapse ${label}` : `Expand ${label}`}
      onClick={(event) => {
        event.stopPropagation()
        onToggle()
      }}
    >
      <ChevronDown className={cn('size-5 transition-transform', expanded && 'rotate-180')} />
    </Button>
  )
}
