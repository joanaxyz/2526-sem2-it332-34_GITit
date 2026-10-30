import { cleanup, render } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { ScenarioInline } from './ScenarioInline'

afterEach(cleanup)

function renderInline(text: string) {
  return render(<p><ScenarioInline text={text} /></p>).container.firstElementChild as HTMLElement
}

describe('ScenarioInline', () => {
  it('renders code, strong, emphasis, and underline marks', () => {
    const paragraph = renderInline('Use `main` and **never push**, *quietly*, before __Friday__.')

    expect(paragraph.querySelector('code')?.textContent).toBe('main')
    expect(paragraph.querySelector('strong')?.textContent).toBe('never push')
    expect(paragraph.querySelector('em')?.textContent).toBe('quietly')
    expect(paragraph.querySelector('u')?.textContent).toBe('Friday')
    expect(paragraph.textContent).toBe('Use main and never push, quietly, before Friday.')
  })

  it('nests marks inside strong text but keeps code spans literal', () => {
    const paragraph = renderInline('**Keep `*.log` out, *always*.** Then `__init__.py` stays.')

    const strong = paragraph.querySelector('strong')
    expect(strong?.querySelector('code')?.textContent).toBe('*.log')
    expect(strong?.querySelector('em')?.textContent).toBe('always')
    expect(paragraph.querySelectorAll('code')[1]?.textContent).toBe('__init__.py')
    expect(paragraph.querySelector('u')).toBeNull()
  })

  it('leaves unmatched or spaced markers, HTML, and links as text', () => {
    const paragraph = renderInline('2 * 3 is * not emphasis, <b>x</b> and [link](https://x.test) stay text.')

    expect(paragraph.querySelector('em, strong, u, b, a')).toBeNull()
    expect(paragraph.textContent).toBe('2 * 3 is * not emphasis, <b>x</b> and [link](https://x.test) stay text.')
  })
})
