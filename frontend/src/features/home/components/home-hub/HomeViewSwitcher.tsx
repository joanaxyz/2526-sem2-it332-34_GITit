import { ChevronDown } from 'lucide-react'
import { useCallback, useEffect, useId, useRef, useState } from 'react'

import { HOME_VIEWS, homeViewOption, type HomeView } from './homeViews'

/**
 * Home's primary navigation. A listbox rather than a tab strip: four categories
 * with a sentence of explanation each do not fit a strip, and the explanation is
 * what tells a learner which one they want. Keyboard behaviour follows the ARIA
 * listbox pattern (Up/Down/Home/End to move, Enter/Space to commit, Escape to
 * cancel), and the popup is positioned against a wrapper that never clips.
 */
export function HomeViewSwitcher({
  view,
  onSelectView,
}: {
  view: HomeView
  onSelectView: (next: HomeView) => void
}) {
  const listboxId = `home-views-${useId().replace(/:/g, '')}`
  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(() =>
    HOME_VIEWS.findIndex((option) => option.id === view),
  )
  const rootRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const selected = homeViewOption(view)

  const close = useCallback((restoreFocus = true) => {
    setOpen(false)
    if (restoreFocus) triggerRef.current?.focus()
  }, [])

  const commit = useCallback(
    (index: number) => {
      const option = HOME_VIEWS[index]
      if (option) onSelectView(option.id)
      close()
    },
    [close, onSelectView],
  )

  useEffect(() => {
    if (!open) return
    setActiveIndex(HOME_VIEWS.findIndex((option) => option.id === view))
    listRef.current?.focus()
  }, [open, view])

  useEffect(() => {
    if (!open) return
    function handlePointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handlePointerDown)
    return () => document.removeEventListener('mousedown', handlePointerDown)
  }, [open])

  function handleKeyDown(event: React.KeyboardEvent<HTMLDivElement>) {
    const last = HOME_VIEWS.length - 1
    if (event.key === 'Escape') {
      event.preventDefault()
      close()
    } else if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActiveIndex((index) => Math.min(last, index + 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((index) => Math.max(0, index - 1))
    } else if (event.key === 'Home') {
      event.preventDefault()
      setActiveIndex(0)
    } else if (event.key === 'End') {
      event.preventDefault()
      setActiveIndex(last)
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      commit(activeIndex)
    } else if (event.key === 'Tab') {
      setOpen(false)
    }
  }

  return (
    <div className="home-switcher" ref={rootRef} data-onboarding="home-views">
      <span className="home-switcher-label" id={`${listboxId}-label`}>
        Showing
      </span>
      <div className="home-switcher-control">
        <button
          type="button"
          ref={triggerRef}
          className={`home-switcher-trigger${open ? ' is-open' : ''}`}
          aria-haspopup="listbox"
          aria-expanded={open}
          aria-controls={open ? listboxId : undefined}
          aria-labelledby={`${listboxId}-label ${listboxId}-value`}
          onClick={() => setOpen((value) => !value)}
        >
          <selected.Icon aria-hidden="true" />
          <span id={`${listboxId}-value`}>{selected.label}</span>
          <ChevronDown aria-hidden="true" />
        </button>

        {open ? (
          <div
            className="dropdown-menu home-switcher-menu"
            id={listboxId}
            ref={listRef}
            role="listbox"
            tabIndex={-1}
            aria-labelledby={`${listboxId}-label`}
            aria-activedescendant={`${listboxId}-option-${activeIndex}`}
            onKeyDown={handleKeyDown}
          >
            {HOME_VIEWS.map((option, index) => (
              <div
                key={option.id}
                id={`${listboxId}-option-${index}`}
                role="option"
                aria-selected={option.id === view}
                className={`home-switcher-option${index === activeIndex ? ' is-active' : ''}`}
                onMouseEnter={() => setActiveIndex(index)}
                onClick={() => commit(index)}
              >
                <option.Icon aria-hidden="true" />
                <span>
                  <strong>{option.label}</strong>
                  <small>{option.blurb}</small>
                </span>
              </div>
            ))}
          </div>
        ) : null}
      </div>
      <p className="home-switcher-blurb">{selected.blurb}</p>
    </div>
  )
}
