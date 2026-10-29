import { render, screen, cleanup } from '@testing-library/react'
import { afterEach, expect, it } from 'vitest'
import { CommandComparison } from './CommandComparison'
afterEach(cleanup)
it('hides unavailable references', () => { const {container}=render(<CommandComparison />); expect(container).toBeEmptyDOMElement() })
it('shows the example sentence', () => { render(<CommandComparison comparison={{learner_count:2,example_count:1,relation:'more'} as never}/>); expect(screen.getByRole('region', {name: 'Solution command comparison'})).toHaveTextContent('Scenario completed in 2 counted commands! Our example solution uses 1 command.') })
