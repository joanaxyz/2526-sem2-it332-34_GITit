import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { MemoryRouter, useLocation } from 'react-router-dom'
import type { PerformanceSummary } from '@/features/performance/types'

import { emptyPerformanceFixture, richPerformanceFixture } from '@/features/performance/preview/fixtures'
import { LearnerPerformanceInstrument } from './LearnerPerformanceInstrument'

afterEach(cleanup)

function objective(code: string) {
  return screen.getByRole('listitem', { name: new RegExp(`^${code.replaceAll('.', String.fromCharCode(92) + '.')} `) })
}
function moduleMetric(module: number, name: string) {
  return within(screen.getByRole('group', { name: `Module ${module} KPIs` })).getByText(name).closest<HTMLElement>('.objective-metric')!
}

function LocationReading() {
  const location = useLocation()
  return <output data-testid="location">{location.search}{location.hash}</output>
}
function renderRecord(data: PerformanceSummary, entry = '/home?view=progress') {
  return render(<MemoryRouter initialEntries={[entry]}><LocationReading /><LearnerPerformanceInstrument data={data} /></MemoryRouter>)
}
function selectModule(number: number) {
  fireEvent.click(screen.getByRole('tab', { name: `Module ${number}` }))
}

describe('learner learning objectives', () => {
  it('keeps overall readings independent of the selected module and objective', () => {
    const data = structuredClone(richPerformanceFixture)
    data.kpis.car = { value: 95, numerator: 95, denominator: 1 }
    data.modules[0].car = { value: 82, numerator: 82, denominator: 1 }
    data.objectives['SO 1.1'] = { value: 70, numerator: 70, denominator: 1 }
    Object.freeze(data)
    renderRecord(data)
    const overall = screen.getByRole('group', { name: 'Overall KPIs' })
    const car = within(overall).getByText('Command Accuracy Rate').closest('.objective-metric')!
    expect(car).toHaveTextContent('95%')
    expect(moduleMetric(1, 'Command Accuracy Rate')).toHaveTextContent('82%')
    expect(objective('SO 1.1')).toHaveTextContent('70%')
    expect(overall.querySelectorAll('.objective-metric')).toHaveLength(5)
    selectModule(4)
    expect(car).toHaveTextContent('95%')
    expect(moduleMetric(4, 'Hard-Level Completion Rate')).toHaveTextContent('Goal ≥65%')
    expect(screen.queryByRole('meter')).not.toBeInTheDocument()
  })

  it('compares all modules by a chosen measure without changing selection or the URL', () => {
    renderRecord(richPerformanceFixture, '/home?view=progress&range=week#learning-module-3')
    const measure = screen.getByRole('combobox', { name: 'Compare by' })
    const tabs = screen.getByRole('tablist', { name: 'Learning modules' })
    expect(within(tabs).getAllByRole('tab')).toHaveLength(4)
    expect(within(tabs).getByRole('tab', { name: 'Module 1' })).toHaveTextContent('100%')
    expect(within(tabs).getByRole('tab', { name: 'Module 2' })).toHaveTextContent('77.8%')
    fireEvent.change(measure, { target: { value: 'arc' } })
    expect(within(tabs).getByRole('tab', { name: 'Module 1' })).toHaveTextContent('1.18')
    expect(screen.getByText('Average retries before mastery · lower is better')).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Module 3' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByTestId('location')).toHaveTextContent('?view=progress&range=week#learning-module-3')
    fireEvent.change(measure, { target: { value: 'rta' } })
    expect(within(tabs).getByRole('tab', { name: 'Module 1' })).toHaveTextContent('Not applicable')
    expect(within(tabs).getByRole('tab', { name: 'Module 2' })).toHaveTextContent('Not applicable')
    expect(within(tabs).getByRole('tab', { name: 'Module 4' })).toHaveTextContent('100%')
    expect(within(tabs).getByRole('tab', { name: 'Module 1' })).not.toHaveTextContent('0%')
  })

  it('shows retry counts directly with their direction, including large unsuccessful averages', () => {
    const data = structuredClone(richPerformanceFixture)
    data.modules[3].arc = { value: 8, numerator: 8, denominator: 1 }
    renderRecord(data)
    expect(moduleMetric(1, 'Average Retry Count')).toHaveTextContent('1.18')
    expect(moduleMetric(1, 'Average Retry Count')).toHaveTextContent('Lower is better')
    selectModule(4)
    const reading = within(objective('SO 4.5')).getByText('Average Retry Count').closest('.objective-reading')!
    expect(reading).toHaveTextContent('8.00')
    expect(reading).toHaveTextContent('Goal ≤3')
    expect(reading).toHaveTextContent('Lower is better')
    expect(reading).toHaveAttribute('data-state', 'miss')
    expect(reading).toHaveTextContent('Keep practicing')
    const countRail = moduleMetric(4, 'Average Retry Count').querySelector('.measurement-rail')!
    expect(countRail).toHaveAttribute('data-count', 'true')
    expect(countRail.querySelector('.measurement-rail-fill')).not.toBeInTheDocument()
    expect(countRail.querySelector('.measurement-rail-reading')).toBeInTheDocument()
    expect(screen.queryByRole('meter')).not.toBeInTheDocument()
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
  })

  it('places percentage readings and their goals on the same calibrated scale', () => {
    renderRecord(richPerformanceFixture)
    const car = moduleMetric(1, 'Command Accuracy Rate')
    const rail = car.querySelector<HTMLElement>('.measurement-rail')!
    expect(rail.style.getPropertyValue('--rail-reading')).toBe('91%')
    expect(rail.style.getPropertyValue('--rail-goal')).toBe('70%')
    expect(rail.querySelector('.measurement-rail-fill')).toBeInTheDocument()
    const overall = screen.getByRole('group', { name: 'Overall KPIs' })
    const overallScr = within(overall).getByText('Scenario Completion Rate').closest('.objective-metric')!
    expect(overallScr).toHaveTextContent('75.4%')
    expect(overallScr).toHaveTextContent('Goal ≥80%')
    expect(overallScr.querySelector<HTMLElement>('.measurement-rail')!.style.getPropertyValue('--rail-reading')).toBe('75.4%')
  })

  it('compares large retry counts against one shared scale without filling a success bar', () => {
    const data = structuredClone(richPerformanceFixture)
    data.modules[0].arc = { value: 8, numerator: 8, denominator: 1 }
    data.modules[1].arc = { value: 10, numerator: 10, denominator: 1 }
    renderRecord(data)
    fireEvent.change(screen.getByRole('combobox', { name: 'Compare by' }), { target: { value: 'arc' } })
    const first = screen.getByRole('tab', { name: 'Module 1' }).querySelector<HTMLElement>('.measurement-rail')!
    const second = screen.getByRole('tab', { name: 'Module 2' }).querySelector<HTMLElement>('.measurement-rail')!
    expect(first.style.getPropertyValue('--rail-reading')).toBe('80%')
    expect(second.style.getPropertyValue('--rail-reading')).toBe('100%')
    expect(first.querySelector('.measurement-rail-fill')).not.toBeInTheDocument()
    expect(second.querySelector('.measurement-rail-fill')).not.toBeInTheDocument()
  })

  it('keeps unmeasured readings separate from a measured zero', () => {
    const data = structuredClone(emptyPerformanceFixture)
    data.modules[0].arc = { value: 0, numerator: 0, denominator: 1 }
    renderRecord(data)
    const empty = objective('SO 1.1')
    expect(empty).toHaveAttribute('data-state', 'none')
    expect(empty.querySelector('.objective-reading-result')).toHaveTextContent('—')
    expect(objective('SO 1.8').querySelector('.objective-reading-result')).toHaveTextContent('0.00')
    expect(objective('SO 1.8')).toHaveAttribute('data-state', 'met')
  })

  it('keeps evidence and the general objective available without expanding the default record', () => {
    renderRecord(richPerformanceFixture)
    const overall = screen.getByText('Overall evidence').closest('details')!
    expect(overall).not.toHaveAttribute('open')
    fireEvent.click(screen.getByText('Overall evidence'))
    expect(overall).toHaveTextContent('43 of 57 required tiers mastered')
    const disclosure = screen.getByText('General objective').closest('details')!
    expect(disclosure).not.toHaveAttribute('open')
    fireEvent.click(screen.getByText('General objective'))
    expect(disclosure).toHaveAttribute('open')
    expect(disclosure).toHaveTextContent('independently manage local Git repositories')
    expect(screen.getByText('CAR by objective · other measures by module')).toBeInTheDocument()
    const row = objective('SO 1.1')
    const evidence = within(row).getByText('Evidence').closest('details')!
    expect(evidence).not.toHaveAttribute('open')
    fireEvent.click(within(row).getByText('Evidence'))
    expect(evidence).toHaveTextContent('91 score points across 1 assessed tier')
    expect(evidence).toHaveTextContent('This objective’s first-mastery assessments')
  })

  it('honors a linked module and supports keyboard selection without losing query parameters', () => {
    renderRecord(richPerformanceFixture, '/home?view=progress&range=week#learning-module-3')
    const third = screen.getByRole('tab', { name: 'Module 3' })
    expect(third).toHaveAttribute('aria-selected', 'true')
    expect(screen.queryByRole('group', { name: 'Module 1 KPIs' })).not.toBeInTheDocument()
    third.focus()
    fireEvent.keyDown(third, { key: 'ArrowRight' })
    const fourth = screen.getByRole('tab', { name: 'Module 4' })
    expect(fourth).toHaveFocus()
    expect(fourth).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByTestId('location')).toHaveTextContent('?view=progress&range=week#learning-module-4')
    fireEvent.keyDown(fourth, { key: 'ArrowRight' })
    const first = screen.getByRole('tab', { name: 'Module 1' })
    expect(first).toHaveFocus()
    fireEvent.keyDown(first, { key: 'ArrowLeft' })
    expect(fourth).toHaveFocus()
    fireEvent.keyDown(fourth, { key: 'Home' })
    expect(first).toHaveFocus()
    fireEvent.keyDown(first, { key: 'End' })
    expect(fourth).toHaveFocus()
    expect(screen.getAllByRole('tabpanel')).toHaveLength(1)
  })

  it('defaults invalid links to Module 1', () => {
    renderRecord(richPerformanceFixture, '/home#learning-module-99')
    expect(screen.getByRole('tab', { name: 'Module 1' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getAllByRole('tabpanel')).toHaveLength(1)
    expect(screen.getByRole('group', { name: 'Module 1 KPIs' })).toBeInTheDocument()
  })

  it('shows every objective in four ordered modules even when no module data exists', () => {
    renderRecord({ ...emptyPerformanceFixture, modules: [] })
    const counts = [8, 11, 5, 5]
    counts.forEach((count, index) => {
      selectModule(index + 1)
      const list = screen.getByRole('list', { name: `Module ${index + 1} specific objectives` })
      expect(within(list).getAllByRole('listitem')).toHaveLength(count)
      expect(list.firstElementChild).toHaveTextContent(`SO ${index + 1}.1`)
      expect(list.lastElementChild).toHaveTextContent(`SO ${index + 1}.${count}`)
    })
    expect(screen.getAllByRole('listitem')).toHaveLength(5)
    selectModule(1)
    expect(objective('SO 1.1')).toHaveTextContent('Not measured yet')
    expect(objective('SO 1.1').querySelector('.objective-reading-result')).toHaveTextContent('—')
    expect(screen.queryByRole('list', { name: 'Module 4 specific objectives' })).not.toBeInTheDocument()
  })

  it('uses objective CAR rather than copying the module or overall value', () => {
    const data = structuredClone(richPerformanceFixture)
    data.objectives['SO 1.1'] = { value: 70, numerator: 70, denominator: 1 }
    data.objectives['SO 1.2'] = { value: 35, numerator: 35, denominator: 1 }
    delete data.objectives['SO 1.3']
    Object.freeze(data)
    renderRecord(data)
    expect(moduleMetric(1, 'Command Accuracy Rate')).toHaveTextContent('91%')
    expect(objective('SO 1.1')).toHaveTextContent('70%')
    expect(objective('SO 1.1')).toHaveAttribute('data-state', 'met')
    expect(objective('SO 1.2')).toHaveTextContent('35%')
    expect(objective('SO 1.2')).toHaveAttribute('data-state', 'miss')
    expect(objective('SO 1.3')).toHaveAttribute('data-state', 'none')
    expect(objective('SO 1.3')).not.toHaveTextContent('91%')
    expect(objective('SO 1.1')).toHaveTextContent('70 score points across 1 assessed tier')
  })

  it('uses module-specific targets including inclusive Module 4 thresholds', () => {
    const data = structuredClone(richPerformanceFixture)
    data.modules[0].scr = { value: 80, numerator: 4, denominator: 5 }
    data.modules[0].arc = { value: 2, numerator: 2, denominator: 1 }
    data.modules[0].hlcr = { value: 70, numerator: 7, denominator: 10 }
    data.modules[3].hlcr = { value: 65, numerator: 13, denominator: 20 }
    data.modules[3].arc = { value: 3, numerator: 3, denominator: 1 }
    data.modules[3].rta = { value: 65, numerator: 13, denominator: 20 }
    renderRecord(data)
    expect(moduleMetric(1, 'Scenario Completion Rate')).toHaveAttribute('data-state', 'met')
    expect(objective('SO 1.7')).toHaveAttribute('data-state', 'met')
    expect(objective('SO 1.8')).toHaveAttribute('data-state', 'met')
    selectModule(4)
    expect(objective('SO 4.4')).toHaveTextContent('Goal ≥65%')
    expect(objective('SO 4.4')).toHaveAttribute('data-state', 'met')
    expect(objective('SO 4.5')).toHaveTextContent('Goal ≤3')
    expect(objective('SO 4.5')).toHaveAttribute('data-state', 'met')
    expect(moduleMetric(4, 'Hard-Level Completion Rate')).toHaveTextContent('Goal ≥65%')
    expect(moduleMetric(4, 'Average Retry Count')).toHaveTextContent('Goal ≤3')
  })

  it('requires both metrics for combined objectives and keeps partial evidence visible', () => {
    const data = structuredClone(richPerformanceFixture)
    data.modules[2].rta = { value: 65, numerator: 13, denominator: 20 }
    data.modules[2].arc = { value: 2.01, numerator: 201, denominator: 100 }
    data.modules[3].rta = { value: null, numerator: 0, denominator: 0 }
    data.modules[3].arc = { value: 4, numerator: 4, denominator: 1 }
    renderRecord(data)
    selectModule(3)
    expect(objective('SO 3.5')).toHaveAttribute('data-state', 'miss')
    expect(objective('SO 3.5')).toHaveTextContent('Both targets required')
    expect(within(objective('SO 3.5')).getByText('Retry Transfer Accuracy')).toBeInTheDocument()
    expect(within(objective('SO 3.5')).getByText('Average Retry Count')).toBeInTheDocument()
    selectModule(4)
    expect(objective('SO 4.5')).toHaveAttribute('data-state', 'partial')
    expect(objective('SO 4.5')).toHaveTextContent('Incomplete evidence')
    const known = within(objective('SO 4.5')).getByText('Average Retry Count').closest('.objective-reading')!
    expect(known).toHaveAttribute('data-state', 'miss')
    expect(known).toHaveTextContent('Keep practicing')
    expect(objective('SO 4.5')).toHaveTextContent('Not measured yet')
  })

  it('keeps measured zero visible and limits transfer KPIs to Modules 3–4', () => {
    const data = structuredClone(emptyPerformanceFixture)
    data.modules[0].hlcr = { value: 0, numerator: 0, denominator: 2 }
    data.modules[0].arc = { value: 0, numerator: 0, denominator: 2 }
    renderRecord(data)
    expect(objective('SO 1.7')).toHaveTextContent('0%')
    expect(objective('SO 1.7')).toHaveAttribute('data-state', 'miss')
    expect(objective('SO 1.8')).toHaveTextContent('0.00')
    expect(objective('SO 1.8')).toHaveAttribute('data-state', 'met')
    for (const number of [1, 2]) {
      selectModule(number)
      expect(within(screen.getByRole('group', { name: `Module ${number} KPIs` })).queryByText('Retry Transfer Accuracy')).not.toBeInTheDocument()
    }
    selectModule(3)
    expect(moduleMetric(3, 'Retry Transfer Accuracy')).toHaveTextContent('Not measured yet')
  })

  it('preserves calculation explanations and supplementary recovery without a target', () => {
    renderRecord(richPerformanceFixture)
    const disclosure = screen.getByText('How these KPIs are measured').closest('details')!
    fireEvent.click(within(disclosure).getByText('How these KPIs are measured'))
    expect(disclosure).toHaveTextContent('Mean of 100 × S × min(1, T ÷ max(1, A))')
    const recovery = screen.getByText('Module 1 retry recovery · supplementary').closest('details')!
    fireEvent.click(within(recovery).getByText('Module 1 retry recovery · supplementary'))
    expect(recovery).toHaveTextContent('83.3%')
    expect(recovery).toHaveTextContent('no target')
    expect(recovery).not.toHaveTextContent('Target met')
  })

  it('preserves start and resume links for reserved transfer checkpoints', () => {
    const data = structuredClone(emptyPerformanceFixture)
    data.samples.transfer_pending = 1
    data.samples.transfer_missing = 2
    data.transfers = [
      { tier_id: 9, title: 'Resolve a novel conflict', run_id: null },
      { tier_id: 10, title: 'Recover novel history', run_id: 42 },
    ]
    renderRecord(data)
    selectModule(3)
    fireEvent.click(screen.getByText('Available transfer checkpoints · Modules 3–4'))
    expect(screen.getByRole('link', { name: /Start transfer checkpoint/ })).toHaveAttribute('href', '/adventure-level-tiers/9/runs?transfer=1')
    expect(screen.getByRole('link', { name: /Resume transfer checkpoint/ })).toHaveAttribute('href', '/adventure-tier-runs/42')
    expect(screen.getByText(/1 pending · 2 mastered tiers without eligible transfer evidence/)).toBeInTheDocument()
  })
})
