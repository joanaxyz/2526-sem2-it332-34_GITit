import { cleanup, render, screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import type { UserKpisResponse } from '@/features/admin/api/adminApi'

import { LearnerKpiPanel } from './LearnerKpiPanel'

type Kpis = NonNullable<UserKpisResponse['kpis']>

const NONE = { value: null, numerator: 0, denominator: 0 }
const rate = (value: number, numerator: number, denominator: number) => ({ value, numerator, denominator })

const KPIS: Kpis = {
  scr: rate(90, 9, 10), // met (>= 80)
  car: rate(17.6, 22, 125), // missed (< 70)
  hlcr: rate(75, 3, 4), // met
  arc: rate(0.1, 1, 10), // met (<= 2)
  rta: rate(50, 1, 2), // missed (< 65)
  retry_success_rate: rate(100, 5, 5), // would "pass" anything, but has no target
}

const MODULES: UserKpisResponse['modules'] = [
  {
    number: 3,
    title: 'Conflict Resolution',
    scr: rate(50, 1, 2),
    hlcr: NONE,
    arc: NONE,
    rta: rate(50, 1, 2),
    retry_success_rate: rate(80, 4, 5),
  },
]

function tile(abbr: string) {
  return screen.getByText(abbr, { selector: '.kp-cell-abbr' }).closest('.kp-cell') as HTMLElement
}

describe('LearnerKpiPanel', () => {
  afterEach(cleanup)

  it('shows six tiles but counts only the five evaluation KPIs in targets met', () => {
    render(<LearnerKpiPanel kpis={KPIS} modules={MODULES} />)

    expect(document.querySelectorAll('.kp-grid .kp-cell')).toHaveLength(6)
    const summary = screen.getByText('Targets met').closest('.kp-summary') as HTMLElement
    expect(summary).toHaveTextContent('3/5')
  })

  it('shows the supplementary rate as a sixth tile with no target and the tooltip', () => {
    render(<LearnerKpiPanel kpis={KPIS} modules={MODULES} />)

    const supplementary = tile('RSR')
    expect(supplementary).toHaveTextContent('100%')
    expect(supplementary).toHaveTextContent('No target')
    expect(supplementary).toHaveTextContent('5 of 5 retry sessions completed')
    expect(supplementary.getAttribute('title')).toMatch(/RTA is the evaluation KPI/)
    expect(supplementary.className).not.toMatch(/--met|--miss/)
    expect(supplementary.querySelector('.kp-cell-icon')).toBeNull()
  })

  it('labels each tile with the unit its formula counts', () => {
    render(<LearnerKpiPanel kpis={KPIS} modules={MODULES} />)

    expect(tile('SCR')).toHaveTextContent('9 of 10 sessions completed')
    expect(tile('CAR')).toHaveTextContent('22 processable / 125 submitted commands')
    expect(tile('HLCR')).toHaveTextContent('3 of 4 hard sessions completed')
    expect(tile('ARC')).toHaveTextContent('1 retry across 10 completed sessions')
    expect(tile('RTA')).toHaveTextContent('1 of 2 eligible retries succeeded')
  })

  it('adds the supplementary rate as a By module column', () => {
    render(<LearnerKpiPanel kpis={KPIS} modules={MODULES} />)

    const table = screen.getByRole('table')
    const headers = within(table).getAllByRole('columnheader').map((th) => th.textContent)
    expect(headers).toEqual(['Mod', 'SCR', 'HLCR', 'ARC', 'RTA', 'RSR'])
    const cells = within(table).getAllByRole('row')[1].querySelectorAll('td')
    const supplementary = cells[cells.length - 1]
    expect(supplementary).toHaveTextContent('80%')
    expect(supplementary).toHaveAttribute('title', '4 of 5 retry sessions completed')
    expect(supplementary.className).not.toMatch(/--met|--miss/)
    expect(cells[1]).toHaveAttribute('title', '1 of 2 sessions completed')
  })
})
