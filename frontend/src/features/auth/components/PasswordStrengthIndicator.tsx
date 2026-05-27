import { Info } from 'lucide-react'
import { useMemo, useState } from 'react'

import {
  getMissingPasswordRequirements,
  getPasswordStrength,
} from '@/features/auth/utils/passwordStrength'
import { cn } from '@/shared/utils/cn'

type PasswordStrengthIndicatorProps = {
  password: string
}

export function PasswordStrengthIndicator({ password }: PasswordStrengthIndicatorProps) {
  const [showMissing, setShowMissing] = useState(false)
  const strength = useMemo(() => getPasswordStrength(password), [password])
  const missing = useMemo(() => getMissingPasswordRequirements(password), [password])
  const showIndicator = password.length > 0

  if (!showIndicator) return null

  return (
    <div className="space-y-2 pt-1">
      <div className="flex gap-1">
        {Array.from({ length: 4 }).map((_, index) => (
          <span
            key={index}
            className={cn(
              'h-1 flex-1 rounded-full transition-colors',
              index < strength.filledSegments ? strength.segmentClass : 'bg-border',
            )}
          />
        ))}
      </div>
      <div className="flex items-center justify-end gap-1.5">
        <span className={cn('text-sm font-medium', strength.labelClass)}>{strength.label}</span>
        {missing.length > 0 ? (
          <div className="relative">
            <button
              type="button"
              className="grid size-5 place-items-center rounded-full bg-sky-500/15 text-sky-500 transition hover:bg-sky-500/25"
              aria-label="Show missing password requirements"
              aria-expanded={showMissing}
              onClick={() => setShowMissing((value) => !value)}
              onBlur={() => setShowMissing(false)}
            >
              <Info className="size-3.5" />
            </button>
            {showMissing ? (
              <div
                role="tooltip"
                className="absolute bottom-full right-0 z-10 mb-2 w-52 rounded-md border border-border bg-card p-3 text-left shadow-panel"
              >
                <p className="text-xs font-semibold text-foreground">Still needed</p>
                <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                  {missing.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  )
}
