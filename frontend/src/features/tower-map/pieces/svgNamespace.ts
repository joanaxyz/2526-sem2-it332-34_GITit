/**
 * Rewrite every `id` in an inline SVG string (and the references to it) to be
 * unique per render instance. A tower piece's SVG is inlined from asset data and
 * the same asset can appear many times on one page (e.g. the crown repeats on
 * every storey); without namespacing, duplicate `<linearGradient id="wall">`s
 * collide and `url(#wall)` resolves to the first one in the document.
 *
 * Handles the reference forms SVG actually uses: `url(#id)` (quoted or not, in
 * attributes and inline `style`), and `href="#id"` / `xlink:href="#id"`.
 */
export function namespaceSvgIds(svg: string, uid: string): string {
  const ids = new Set<string>()
  const idRe = /\bid="([^"]+)"/g
  let match: RegExpExecArray | null
  while ((match = idRe.exec(svg)) !== null) ids.add(match[1])
  if (ids.size === 0) return svg

  let out = svg
  // Replace longer ids first so an id that is a prefix of another (e.g. "g" and
  // "glow") can't partially clobber the longer one.
  for (const id of [...ids].sort((a, b) => b.length - a.length)) {
    const ns = `${id}__${uid}`
    out = out
      .replaceAll(`id="${id}"`, `id="${ns}"`)
      .replaceAll(`url(#${id})`, `url(#${ns})`)
      .replaceAll(`url("#${id}")`, `url("#${ns}")`)
      .replaceAll(`url('#${id}')`, `url('#${ns}')`)
      .replaceAll(`href="#${id}"`, `href="#${ns}"`)
  }
  return out
}
