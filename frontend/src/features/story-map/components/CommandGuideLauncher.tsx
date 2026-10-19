import { Check } from 'lucide-react'
import { type CSSProperties, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import { FloatingGuideMascot } from '@/shared/mascot/FloatingGuideMascot'

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
    const below = window.innerHeight - triggerRect.bottom - viewportGap * 2
    const above = triggerRect.top - viewportGap * 2
    const upward = below < 240 && above > below
    setPickerStyle({
      left: Math.max(viewportGap, Math.min(triggerRect.right - width, window.innerWidth - viewportGap - width)),
      maxHeight: Math.max(100, upward ? above : below),
      ...(upward ? { bottom: window.innerHeight - triggerRect.top + 8 } : { top: triggerRect.bottom + 8 }),
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
      if (target instanceof Element && target.closest('.guide-mascot')) return
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
    : 'Open command guide'

  const selectGuide = (teachingKey: string) => {
    setPickerOpen(false)
    onSelectGuide(teachingKey)
  }

  return (
    <>
      <FloatingGuideMascot buttonRef={triggerRef} label={label} active={guideOpen}
        onDragStart={() => setPickerOpen(false)}
        onActivate={() => selectGuide(guides.find((guide) => guide.teaching_key === currentGuideKey)?.teaching_key ?? guides[guides.length - 1].teaching_key)}>
        {hasSelection ? <button type="button" className="guide-mascot__history"
          aria-label="Browse command guides" aria-controls={pickerId} aria-expanded={pickerOpen}
          title={`Browse ${guides.length} command guides`} disabled={guideOpen}
          onClick={() => setPickerOpen((open) => !open)}>{guides.length}</button> : null}
      </FloatingGuideMascot>

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
    </>
  )
}
