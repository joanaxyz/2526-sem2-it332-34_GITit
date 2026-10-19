import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { emptyPerformanceFixture, richPerformanceFixture } from '@/features/performance/preview/fixtures'
import { LearnerPerformanceInstrument } from './LearnerPerformanceInstrument'

afterEach(cleanup)

describe('learner performance', () => {
  it('shows exact server values and selects only the requested comparison', () => {
    const data = structuredClone(richPerformanceFixture)
    Object.freeze(data)
    const first = render(<LearnerPerformanceInstrument data={data} />)
    const measures = screen.getByRole('group', { name: 'Practice measures' })
    const finish = within(measures).getByRole('button', { name: /Runs finished/ })
    expect(finish).toHaveAttribute('aria-pressed', 'true')
    expect(finish).toHaveTextContent('75.4%')
    expect(finish).toHaveTextContent('Goal ≥80%')
    expect(within(measures).getByRole('button', { name: /Commands accepted/ })).toHaveTextContent('Goal ≥70%')
    const retries = within(measures).getByRole('button', { name: /Retries per finish/ })
    expect(retries).toHaveTextContent('1.60')
    expect(retries).toHaveTextContent('On track')
    expect(retries).toHaveTextContent('Goal ≤2')
    fireEvent.click(retries)
    expect(retries).toHaveAttribute('aria-pressed', 'true')
    expect(finish).toHaveAttribute('aria-pressed', 'false')
    expect(screen.getByRole('region', { name: 'Module comparison' })).toHaveTextContent('Relative scale')
    first.unmount()
    render(<LearnerPerformanceInstrument data={data} />)
    expect(screen.getByRole('button', { name: /Runs finished/ })).toHaveAttribute('aria-pressed', 'true')
  })

  it('restricts changed retries to Modules 3–4 and keeps recovery supplementary', () => {
    render(<LearnerPerformanceInstrument data={richPerformanceFixture} />)
    fireEvent.click(screen.getByRole('button', { name: /Changed retries cleared/ }))
    const comparison = screen.getByRole('region', { name: 'Module comparison' })
    expect(within(comparison).getAllByRole('listitem')).toHaveLength(2)
    expect(comparison).toHaveTextContent('Conflict Resolution')
    expect(comparison).not.toHaveTextContent('Local Repository')
    expect(comparison).not.toHaveTextContent('On track')
    const recovery = screen.getByRole('button', { name: /Retry recovery/ })
    expect(recovery).toHaveTextContent('For context')
    expect(recovery).toHaveTextContent('No target')
    expect(recovery).not.toHaveTextContent('On track')
    fireEvent.click(recovery)
    expect(within(screen.getByRole('region', { name: 'Module comparison' })).getAllByRole('listitem')).toHaveLength(4)
  })

  it('states why CAR has no per-module comparison and exposes formula disclosure', () => {
    render(<LearnerPerformanceInstrument data={richPerformanceFixture} />)
    fireEvent.click(screen.getByRole('button', { name: /Commands accepted/ }))
    expect(screen.getByText(/A per-module breakdown is not available/)).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Module comparison' })).not.toBeInTheDocument()
    const disclosure = screen.getByText('How this is measured').closest('details')!
    fireEvent.click(within(disclosure).getByText('How this is measured'))
    expect(disclosure).toHaveTextContent('Processable commands ÷ Total submitted commands × 100')
  })

  it('never treats missing observations as failure and keeps measured zero visible', () => {
    const data = structuredClone(emptyPerformanceFixture)
    data.kpis.hlcr = { value: 0, numerator: 0, denominator: 2 }
    render(<LearnerPerformanceInstrument data={data} />)
    const hard = screen.getByRole('button', { name: /Hard runs cleared/ })
    expect(hard).toHaveTextContent('0%')
    expect(hard).toHaveTextContent('Keep practicing')
    const changed = screen.getByRole('button', { name: /Changed retries cleared/ })
    expect(changed).toHaveTextContent('Not measured yet')
    expect(changed).not.toHaveTextContent('0%')
    fireEvent.click(changed)
    expect(screen.getByText(/Measured on changed retries in Modules 3–4/)).toBeInTheDocument()
    expect(changed).toHaveAttribute('data-state', 'empty')
  })
})
