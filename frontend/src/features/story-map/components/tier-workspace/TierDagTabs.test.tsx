import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import type { RepositorySnapshot } from '@/shared/level/types'

// Each diagram mock exposes the props the tabs hand it, so the test can see
// that both stay mounted and which one was asked to refit.
vi.mock('@/features/story-map/components/TierDagStage', () => ({
  TierDagStage: ({ showHeader, refitKey }: { showHeader?: boolean; refitKey?: string }) => (
    <div data-testid="live-view" data-header={String(showHeader)} data-refit={refitKey} />
  ),
}))

vi.mock('@/shared/level/components/LiveDagPanel', () => ({
  LiveDagPanel: ({ showHeader, refitKey, zoomStorageKey }: { showHeader?: boolean; refitKey?: string; zoomStorageKey?: string }) => (
    <div data-testid="expected-view" data-header={String(showHeader)} data-refit={refitKey} data-zoom-key={zoomStorageKey} />
  ),
}))

import { TierDagTabs } from './TierDagTabs'

const animation = {
  activity: 'idle',
  animating: false,
  onCommandStart: vi.fn(),
  onCommandResolved: vi.fn(),
  onCommandError: vi.fn(),
} satisfies TierDagAnimationController

const snapshot = { repository_initialized: true, commits: [], branches: {} } as unknown as RepositorySnapshot

function tabs(countedCommands: number) {
  return <TierDagTabs snapshot={snapshot} expectedState={snapshot} countedCommands={countedCommands} animation={animation} />
}

function renderTabs() {
  const view = render(tabs(0))
  return {
    rerender: view.rerender,
    liveTab: screen.getByRole('tab', { name: 'Live' }),
    expectedTab: screen.getByRole('tab', { name: 'Expected' }),
    livePane: screen.getByTestId('live-view').parentElement as HTMLElement,
    expectedPane: screen.getByTestId('expected-view').parentElement as HTMLElement,
  }
}

afterEach(cleanup)

describe('TierDagTabs', () => {
  it('opens on the Live DAG with both diagrams mounted and the tab bar as their heading', () => {
    const { liveTab, expectedTab, livePane, expectedPane } = renderTabs()

    expect(liveTab).toHaveAttribute('aria-selected', 'true')
    expect(liveTab).toHaveAttribute('tabindex', '0')
    expect(expectedTab).toHaveAttribute('tabindex', '-1')
    expect(livePane).toHaveClass('is-active')
    expect(livePane).not.toHaveClass('is-inactive')
    expect(livePane).not.toHaveAttribute('inert')
    expect(expectedPane).toHaveClass('is-inactive')
    expect(expectedPane).not.toHaveClass('is-active')
    expect(expectedPane).toHaveAttribute('inert')
    expect(screen.getByTestId('live-view')).toHaveAttribute('data-header', 'false')
    expect(screen.getByTestId('expected-view')).toHaveAttribute('data-header', 'false')
    expect(liveTab).toHaveAttribute('aria-controls', livePane.id)
    expect(livePane).toHaveAttribute('aria-labelledby', liveTab.id)
  })

  it('switches panes on click without unmounting, and refits only the pane being shown', () => {
    const { expectedTab, livePane, expectedPane } = renderTabs()
    const liveView = screen.getByTestId('live-view')

    fireEvent.click(expectedTab)

    expect(expectedTab).toHaveAttribute('aria-selected', 'true')
    expect(expectedPane).toHaveClass('is-active')
    expect(expectedPane).not.toHaveAttribute('inert')
    expect(livePane).toHaveClass('is-inactive')
    expect(livePane).toHaveAttribute('inert')
    expect(screen.getByTestId('live-view')).toBe(liveView)
    expect(screen.getByTestId('expected-view')).toHaveAttribute('data-refit', '1:0')
    expect(screen.getByTestId('live-view')).toHaveAttribute('data-refit', '0:0')

    fireEvent.click(screen.getByRole('tab', { name: 'Live' }))
    expect(screen.getByTestId('live-view')).toHaveAttribute('data-refit', '1:0')
  })

  it('does not refit when the active tab is clicked again', () => {
    const { liveTab } = renderTabs()

    fireEvent.click(liveTab)

    expect(screen.getByTestId('live-view')).toHaveAttribute('data-refit', '0:0')
  })

  it('moves between tabs with the arrow, Home and End keys', () => {
    const { liveTab, expectedTab } = renderTabs()

    fireEvent.keyDown(liveTab, { key: 'ArrowRight' })
    expect(expectedTab).toHaveAttribute('aria-selected', 'true')
    expect(expectedTab).toHaveFocus()

    fireEvent.keyDown(expectedTab, { key: 'ArrowRight' })
    expect(liveTab).toHaveAttribute('aria-selected', 'true')

    fireEvent.keyDown(liveTab, { key: 'End' })
    expect(expectedTab).toHaveAttribute('aria-selected', 'true')

    fireEvent.keyDown(expectedTab, { key: 'Home' })
    expect(liveTab).toHaveAttribute('aria-selected', 'true')
  })

  it('switches back to the Live DAG, refit, when a counted command runs on the Expected tab', () => {
    const { rerender, expectedTab } = renderTabs()
    fireEvent.click(expectedTab)
    expectedTab.focus()

    rerender(tabs(1))

    expect(screen.getByRole('tab', { name: 'Live' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByTestId('live-view')).toHaveAttribute('data-refit', '1:0')
    // The switch does not steal focus from wherever the learner is.
    expect(expectedTab).toHaveFocus()
  })

  it('stays on the Live DAG without a refit when a counted command runs there', () => {
    const { rerender } = renderTabs()

    rerender(tabs(1))

    expect(screen.getByRole('tab', { name: 'Live' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByTestId('live-view')).toHaveAttribute('data-refit', '0:0')
  })

  it('refits both views when the host reveals the card', () => {
    const { rerender } = render(
      <TierDagTabs snapshot={snapshot} expectedState={snapshot} countedCommands={0} animation={animation} refitToken={1} />,
    )
    rerender(<TierDagTabs snapshot={snapshot} expectedState={snapshot} countedCommands={0} animation={animation} refitToken={2} />)

    expect(screen.getByTestId('live-view')).toHaveAttribute('data-refit', '0:2')
    expect(screen.getByTestId('expected-view')).toHaveAttribute('data-refit', '0:2')
  })

  it('drops its tour anchors while it sits in a closed drawer', () => {
    render(
      <TierDagTabs snapshot={snapshot} expectedState={snapshot} countedCommands={0} animation={animation} tourAnchors={false} />,
    )

    expect(document.querySelector('[data-tour-target="expected-state"]')).toBeNull()
    expect(document.querySelector('[data-tour-target="live-dag"]')).toBeNull()
  })

  it('keeps separate zoom keys and the tour anchors', () => {
    const { expectedTab, livePane } = renderTabs()

    expect(screen.getByTestId('expected-view').dataset.zoomKey).toMatch(/:expected$/)
    expect(expectedTab).toHaveAttribute('data-tour-target', 'expected-state')
    expect(livePane).toHaveAttribute('data-tour-target', 'live-dag')
  })
})
