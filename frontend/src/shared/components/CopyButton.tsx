import { Check, Copy } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

import { cn } from '@/shared/utils/cn'

async function copyText(value: string) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value)
      return
    }
  } catch {
    // Fall through to the legacy path below (e.g. non-secure context / denied).
  }
  // Legacy fallback: a throwaway textarea + execCommand keeps copy working when
  // the async Clipboard API is unavailable.
  const textarea = document.createElement('textarea')
  textarea.value = value
  textarea.setAttribute('readonly', '')
  textarea.style.position = 'absolute'
  textarea.style.left = '-9999px'
  document.body.appendChild(textarea)
  textarea.select()
  try {
    document.execCommand('copy')
  } finally {
    document.body.removeChild(textarea)
  }
}

/**
 * Small icon button that copies a literal to the clipboard and flips to a check
 * for a moment. Used for the hard-to-retype values a level story surfaces
 * (remote URLs, branch/commit refs).
 */
export function CopyButton({
  value,
  label,
  className,
}: {
  value: string
  /** Appended to the title/aria-label, e.g. "Copy remote URL". */
  label?: string
  className?: string
}) {
  const [copied, setCopied] = useState(false)
  const timerRef = useRef<number | undefined>(undefined)

  useEffect(() => () => window.clearTimeout(timerRef.current), [])

  async function handleCopy() {
    await copyText(value)
    setCopied(true)
    window.clearTimeout(timerRef.current)
    timerRef.current = window.setTimeout(() => setCopied(false), 1500)
  }

  const title = copied ? 'Copied' : label ? `Copy ${label}` : 'Copy'

  return (
    <button
      type="button"
      onClick={handleCopy}
      title={title}
      aria-label={title}
      className={cn(
        'grid size-6 shrink-0 place-items-center rounded-sm text-muted-foreground transition hover:bg-secondary hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        className,
      )}
    >
      {copied ? <Check className="size-3 text-primary" /> : <Copy className="size-3" />}
    </button>
  )
}
