import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useRef, type PointerEvent, type ReactNode } from 'react'

type ShopCarouselProps<T> = {
  items: T[]
  index: number
  onIndexChange: (index: number) => void
  getKey: (item: T, index: number) => string
  renderSlide: (item: T, index: number, active: boolean) => ReactNode
  ariaLabel: string
  className?: string
}

/**
 * Dependency-free single-item carousel. The story slides by whole slides;
 * dragging past a threshold, the arrows, dots, and arrow keys all move by one.
 * Honors `prefers-reduced-motion` by dropping the slide transition (the active
 * slide still changes instantly).
 */
export function ShopCarousel<T>({
  items,
  index,
  onIndexChange,
  getKey,
  renderSlide,
  ariaLabel,
  className,
}: ShopCarouselProps<T>) {
  const dragStart = useRef<number | null>(null)
  const dragged = useRef(false)
  const trackRef = useRef<HTMLDivElement>(null)
  const count = items.length
  const clamped = Math.max(0, Math.min(count - 1, index))

  const go = (next: number) => {
    onIndexChange(Math.max(0, Math.min(count - 1, next)))
  }

  const onPointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (count < 2 || event.button !== 0) return
    dragStart.current = event.clientX
    dragged.current = false
  }

  const onPointerMove = (event: PointerEvent<HTMLDivElement>) => {
    if (dragStart.current === null) return
    const delta = event.clientX - dragStart.current
    if (Math.abs(delta) > 8) dragged.current = true
    const story = trackRef.current
    if (story) {
      const damp = delta * 0.32
      story.style.transition = 'none'
      story.style.transform = `translate3d(calc(${-clamped * 100}% + ${damp}px), 0, 0)`
    }
  }

  const endDrag = (event: PointerEvent<HTMLDivElement>) => {
    const story = trackRef.current
    if (story) {
      story.style.transition = ''
      story.style.transform = ''
    }
    if (dragStart.current === null) return
    const delta = event.clientX - dragStart.current
    dragStart.current = null
    const threshold = 56
    if (delta <= -threshold) go(clamped + 1)
    else if (delta >= threshold) go(clamped - 1)
  }

  return (
    <div
      className={`shop-carousel ${className ?? ''}`}
      role="group"
      aria-roledescription="carousel"
      aria-label={ariaLabel}
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === 'ArrowRight') {
          event.preventDefault()
          go(clamped + 1)
        } else if (event.key === 'ArrowLeft') {
          event.preventDefault()
          go(clamped - 1)
        }
      }}
    >
      <span className="sr-only" aria-live="polite" aria-atomic="true">
        {ariaLabel}: item {count ? clamped + 1 : 0} of {count}
      </span>
      <div
        className="shop-carousel-viewport"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
        onPointerLeave={(event) => {
          if (dragStart.current !== null) endDrag(event)
        }}
      >
        <div
          ref={trackRef}
          className="shop-carousel-story"
          style={{ transform: `translate3d(${-clamped * 100}%, 0, 0)` }}
        >
          {items.map((item, i) => (
            <div
              className="shop-carousel-slide"
              key={getKey(item, i)}
              aria-hidden={i !== clamped}
              onClickCapture={(event) => {
                // Swallow the click that ends a drag so slide taps don't fire.
                if (dragged.current) {
                  event.preventDefault()
                  event.stopPropagation()
                  dragged.current = false
                }
              }}
            >
              {renderSlide(item, i, i === clamped)}
            </div>
          ))}
        </div>
      </div>

      {count > 1 ? (
        <>
          <button
            type="button"
            className="shop-carousel-arrow shop-carousel-arrow--left"
            aria-label="Previous"
            disabled={clamped === 0}
            onClick={() => go(clamped - 1)}
          >
            <ChevronLeft aria-hidden="true" />
          </button>
          <button
            type="button"
            className="shop-carousel-arrow shop-carousel-arrow--right"
            aria-label="Next"
            disabled={clamped === count - 1}
            onClick={() => go(clamped + 1)}
          >
            <ChevronRight aria-hidden="true" />
          </button>
          <div className="shop-carousel-dots" role="tablist" aria-label={`${ariaLabel} pages`}>
            {items.map((item, i) => (
              <button
                key={getKey(item, i)}
                type="button"
                role="tab"
                aria-selected={i === clamped}
                aria-label={`Slide ${i + 1} of ${count}`}
                data-active={i === clamped}
                onClick={() => go(i)}
              />
            ))}
          </div>
        </>
      ) : null}
    </div>
  )
}

export type { ReactNode }
