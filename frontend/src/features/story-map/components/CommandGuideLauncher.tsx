import { BookOpen, Check } from 'lucide-react'
import { type CSSProperties, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'

export function CommandGuideLauncher({
  guides,
  currentGuideKey,
  guideOpen,
  onSelectGuide,
}: {
  guides: readonly CommandIntroduction[]
  currentGuideKey?: string | null
  guideOpen: boolean
  onSelectGuide: (teachingKey: string) => void
}) {
  const [pickerOpen, setPickerOpen] = useState(false)
  const [pickerStyle, setPickerStyle] = useState<CSSProperties | null>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const pickerRef = useRef<HTMLDivElement>(null)
  const pickerId = useId()

  const positionPicker = useCallback(() => {
    const trigger = triggerRef.current
    if (!trigger) return
    const triggerRect = trigger.getBoundingClientRect()
    const viewportGap = 12
    const width = Math.min(320, window.innerWidth - viewportGap * 2)
    setPickerStyle({
      left: Math.max(viewportGap, Math.min(triggerRect.right - width, window.innerWidth - viewportGap - width)),
      maxHeight: Math.max(180, window.innerHeight - triggerRect.bottom - viewportGap * 2),
      top: triggerRect.bottom + 8,
      width,
    })
  }, [])

  useLayoutEffect(() => {
    if (!pickerOpen) return
    positionPicker()
  }, [pickerOpen, positionPicker])

  useEffect(() => {
    if (!pickerOpen) return
    const closeOnOutsidePointer = (event: PointerEvent) => {
      const target = event.target as Node
      if (triggerRef.current?.contains(target) || pickerRef.current?.contains(target)) return
      setPickerOpen(false)
    }
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return
      setPickerOpen(false)
      triggerRef.current?.focus()
    }
    document.addEventListener('pointerdown', closeOnOutsidePointer)
    document.addEventListener('keydown', closeOnEscape)
    document.addEventListener('scroll', positionPicker, true)
    window.addEventListener('resize', positionPicker)
    return () => {
      document.removeEventListener('pointerdown', closeOnOutsidePointer)
      document.removeEventListener('keydown', closeOnEscape)
      document.removeEventListener('scroll', positionPicker, true)
      window.removeEventListener('resize', positionPicker)
    }
  }, [pickerOpen, positionPicker])

  useEffect(() => {
    if (guideOpen) setPickerOpen(false)
  }, [guideOpen])

  if (guides.length === 0) return null

  const hasSelection = guides.length > 1
  const label = guideOpen
    ? 'Command guide is open'
    : hasSelection
      ? 'Choose command guide'
      : 'Open command guide'

  const selectGuide = (teachingKey: string) => {
    setPickerOpen(false)
    onSelectGuide(teachingKey)
  }

  return (
    <div className="gameplay-header-guide-picker">
      <button
        ref={triggerRef}
        type="button"
        className={`gameplay-header-button gameplay-header-icon-button gameplay-header-command-guide${guideOpen ? ' is-active' : ''}`}
        aria-label={label}
        aria-controls={hasSelection ? pickerId : undefined}
        aria-expanded={hasSelection ? pickerOpen : undefined}
        title={label}
        data-command-guide-launcher
        disabled={guideOpen}
        onClick={() => {
          if (hasSelection) setPickerOpen((open) => !open)
          else selectGuide(guides[0].teaching_key)
        }}
      >
        <BookOpen aria-hidden="true" />
      </button>

      {pickerOpen && pickerStyle ? createPortal(
        <div
          ref={pickerRef}
          id={pickerId}
          className="command-guide-picker dropdown-menu app-scrollbar"
          style={pickerStyle}
          role="group"
          aria-label="Command guides"
        >
          <div className="command-guide-picker__heading">
            <strong>Command guides</strong>
            <span>{guides.length} found</span>
          </div>
          {guides.map((guide, index) => {
            const current = guide.teaching_key === currentGuideKey
            return (
              <button
                type="button"
                className="command-guide-picker__option"
                key={guide.teaching_key}
                data-current={current || undefined}
                onClick={() => selectGuide(guide.teaching_key)}
              >
                <span className="command-guide-picker__number">{String(index + 1).padStart(2, '0')}</span>
                <span className="command-guide-picker__copy">
                  <strong>{guide.title}</strong>
                  <code>{guide.command_form.usage_form}</code>
                </span>
                {current ? (
                  <span className="command-guide-picker__current">
                    <Check aria-hidden="true" />
                    Current
                  </span>
                ) : null}
              </button>
            )
          })}
        </div>,
        document.body,
      ) : null}
    </div>
  )
}
