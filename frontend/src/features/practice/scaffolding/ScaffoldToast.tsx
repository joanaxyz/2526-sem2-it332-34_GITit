import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

export type ScaffoldToastProps = {
  message: string
  trigger: 'T1' | 'T2' | 'T3'
  difficulty: 'easy' | 'medium' | 'hard'
  onProceedToCommandPreview: () => void
  onContinue: () => void
}

const BORDER_COLOR: Record<'T1' | 'T2' | 'T3', string> = {
  T1: 'border-blue-500/60',
  T2: 'border-yellow-500/60',
  T3: 'border-red-500/60',
}

export function ScaffoldToast({
  message,
  trigger,
  onProceedToCommandPreview,
  onContinue,
}: ScaffoldToastProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      data-testid="scaffold-toast"
      className={cn(
        'w-[26rem] max-w-[90vw] rounded-lg border bg-background/95 p-4 shadow-xl backdrop-blur-sm',
        BORDER_COLOR[trigger],
      )}
    >
      {/* Message is plain text — no markdown or anchor rendering */}
      <p className="whitespace-pre-line text-sm leading-6 text-foreground">{message}</p>

      <div className="mt-4 flex justify-end gap-2">
        <Button
          type="button"
          size="sm"
          variant="ghost"
          onClick={onContinue}
          data-testid="scaffold-continue"
        >
          Continue
        </Button>
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={onProceedToCommandPreview}
          data-testid="scaffold-proceed"
        >
          Proceed to Command Preview
        </Button>
      </div>
    </div>
  )
}
