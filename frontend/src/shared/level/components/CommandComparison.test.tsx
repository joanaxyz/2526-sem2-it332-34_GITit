import { render, screen, cleanup } from '@testing-library/react'
import { afterEach, expect, it } from 'vitest'
import { CommandComparison } from './CommandComparison'

afterEach(cleanup)
it('hides unavailable references', () => {
  const { container } = render(<CommandComparison />)
  expect(container).toBeEmptyDOMElement()
})
it('separates the completion headline from the reference', () => {
  render(<CommandComparison comparison={{ learner_count: 2, example_count: 1, relation: 'more' }} />)
  const region = screen.getByRole('region', { name: 'Solution command comparison' })
  expect(region.querySelector('.outcome-comparison-headline')).toHaveTextContent('Scenario completed in 2 counted commands!')
  expect(region.querySelector('.outcome-comparison-reference')).toHaveTextContent('Our example solution uses 1 command.')
})
it('uses singular counts and highlights a shorter solution', () => {
  render(<CommandComparison comparison={{ learner_count: 1, example_count: 3, relation: 'fewer' } as never} />)
  expect(screen.getByText('1 counted command!')).toBeInTheDocument()
  expect(screen.getByText('2 fewer commands than the example.')).toBeInTheDocument()
})
