import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ModulePerformanceCard } from '@/features/dashboard/components/ModulePerformanceCard'
import type { DashboardSummary } from '@/features/dashboard/types'

const summary: DashboardSummary = {
  kpis: {
    orientation_completion: { value: 50, numerator: 1, denominator: 2 },
    scr: { value: 75, numerator: 3, denominator: 4 },
    arc: { value: 1.2, numerator: 6, denominator: 5 },
    car: { value: 80, numerator: 400, denominator: 5 },
    hlcr: { value: 75, numerator: 3, denominator: 4 },
    rta: { value: 33.3, numerator: 1, denominator: 3 },
    sar: { value: 10, numerator: 1, denominator: 10 },
    review_scr: { value: 60, numerator: 3, denominator: 5 },
  },
  module_kpis: {
    1: {
      hlcr: { value: 66.7, numerator: 2, denominator: 3 },
      rta: { value: 50, numerator: 1, denominator: 2 },
    },
    2: {
      hlcr: { value: 100, numerator: 1, denominator: 1 },
      rta: { value: 0, numerator: 0, denominator: 1 },
    },
    3: {
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rta: { value: null, numerator: 0, denominator: 0 },
    },
    4: {
      hlcr: { value: null, numerator: 0, denominator: 0 },
      rta: { value: null, numerator: 0, denominator: 0 },
    },
  },
  counts: {
    started: 4,
    completed: 3,
    failed: 1,
    abandoned: 0,
    review_started: 1,
  },
  streak: {
    current: 2,
    longest: 3,
    last_completed_on: '2026-05-18',
  },
  first_attempt_stars: 1,
  retry_trends: [],
}

describe('ModulePerformanceCard', () => {
  it('renders module rows in order and shows module percentages', () => {
    render(<ModulePerformanceCard summary={summary} />)

    expect(screen.getAllByText(/module [1-4]/i).map((node) => node.textContent)).toEqual([
      'Module 1',
      'Module 2',
      'Module 3',
      'Module 4',
    ])
    expect(screen.getByText('66.7%')).toBeInTheDocument()
    expect(screen.getByText('50%')).toBeInTheDocument()
  })

  it('shows no-data fallback when module denominator is zero', () => {
    render(<ModulePerformanceCard summary={summary} />)

    expect(screen.getAllByText('No data').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Waiting for practice').length).toBeGreaterThan(0)
  })
})
