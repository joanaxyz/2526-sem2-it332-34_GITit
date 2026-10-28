import { Check } from 'lucide-react'
import { type CSSProperties, type Ref, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import { FloatingMascotLauncher } from '@/shared/mascot/FloatingMascotLauncher'

/**
 * Git-It floating over the workspace. A click reopens the current command
 * guide; once the run has met several, its badge lists them to pick from.
 */
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
      const pressed = event.target
      // Presses on the launcher toggle or drag it; dragging closes the picker itself.
      if (pressed instanceof Element && (pickerRef.current?.contains(pressed) || pressed.closest('.mascot-launcher'))) return
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

  const currentGuide = guides.find((guide) => guide.teaching_key === currentGuideKey) ?? guides[guides.length - 1]
  const selectGuide = (teachingKey: string) => {
    setPickerOpen(false)
    onSelectGuide(teachingKey)
  }

  return (
    <>
      <FloatingMascotLauncher
        name="command-guide"
        homeSlot="upper"
        label={guideOpen ? 'Command guide is open' : 'Open command guide'}
        caption="Guide"
        open={guideOpen}
        buttonRef={triggerRef}
        onOpen={() => selectGuide(currentGuide.teaching_key)}
        onDragStart={() => setPickerOpen(false)}
      >
        {guides.length > 1 ? (
          <button
            type="button"
            className="mascot-launcher__badge"
            aria-label="Browse command guides"
            aria-controls={pickerId}
            aria-expanded={pickerOpen}
            title={`Browse ${guides.length} command guides`}
            onClick={() => setPickerOpen((open) => !open)}
          >
            {guides.length}
          </button>
        ) : null}
      </FloatingMascotLauncher>

      {pickerOpen && pickerStyle ? createPortal(
        <CommandGuidePicker
          pickerRef={pickerRef}
          id={pickerId}
          style={pickerStyle}
          guides={guides}
          currentGuideKey={currentGuideKey}
          onSelect={selectGuide}
        />,
        document.body,
      ) : null}
    </>
  )
}

function CommandGuidePicker({ pickerRef, id, style, guides, currentGuideKey, onSelect }: {
  pickerRef: Ref<HTMLDivElement>
  id: string
  style: CSSProperties
  guides: readonly CommandIntroduction[]
  currentGuideKey?: string | null
  onSelect: (teachingKey: string) => void
}) {
  return (
    <div
      ref={pickerRef}
      id={id}
      className="command-guide-picker dropdown-menu app-scrollbar"
      style={style}
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
            onClick={() => onSelect(guide.teaching_key)}
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
    </div>
  )
}
