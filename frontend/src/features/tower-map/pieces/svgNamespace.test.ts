import { describe, expect, it } from 'vitest'

import { namespaceSvgIds } from './svgNamespace'

describe('namespaceSvgIds', () => {
  it('rewrites ids and their url(#) references', () => {
    const svg = '<defs><linearGradient id="wall"/></defs><rect fill="url(#wall)"/>'
    const out = namespaceSvgIds(svg, 'abc')
    expect(out).toBe('<defs><linearGradient id="wall__abc"/></defs><rect fill="url(#wall__abc)"/>')
  })

  it('rewrites href and clip-path references', () => {
    const svg = '<clipPath id="c"/><g clip-path="url(#c)"/><use href="#c"/>'
    const out = namespaceSvgIds(svg, 'x1')
    expect(out).toContain('id="c__x1"')
    expect(out).toContain('clip-path="url(#c__x1)"')
    expect(out).toContain('href="#c__x1"')
  })

  it('does not clobber an id that is a prefix of another', () => {
    const svg = '<g id="g"/><filter id="glow"/><rect filter="url(#glow)" fill="url(#g)"/>'
    const out = namespaceSvgIds(svg, 'u')
    expect(out).toContain('id="g__u"')
    expect(out).toContain('id="glow__u"')
    expect(out).toContain('filter="url(#glow__u)"')
    expect(out).toContain('fill="url(#g__u)"')
  })

  it('leaves svg without ids untouched', () => {
    const svg = '<rect width="10" height="10" fill="#fff"/>'
    expect(namespaceSvgIds(svg, 'u')).toBe(svg)
  })

  it('namespaces the same svg differently per uid (no cross-instance collision)', () => {
    const svg = '<linearGradient id="a"/><rect fill="url(#a)"/>'
    expect(namespaceSvgIds(svg, '1')).not.toBe(namespaceSvgIds(svg, '2'))
  })
})
