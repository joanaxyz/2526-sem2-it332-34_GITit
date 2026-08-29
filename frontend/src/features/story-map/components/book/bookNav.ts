import type { BookPage } from '@/features/story-map/components/book/bookTypes'

// Sub-navigation for a command: the option and argument sections it teaches
// (e.g. `git init` -> `-q / --quiet`, `-b / --initial-branch`, `<directory>`).
export type BookNavAnchor = {
  // The page id the anchor scrolls to.
  pageId: string
  label: string
  kind: 'option' | 'argument'
}

export function bookNavAnchors(content: { pages: BookPage[] }): BookNavAnchor[] {
  const anchors: BookNavAnchor[] = []
  const seen = new Set<string>()
  content.pages.forEach((page, index) => {
    if (page.section_type !== 'option' && page.section_type !== 'argument') return
    const label = (page.eyebrow || page.heading || page.title || '')
      .replace(/^Option:\s*/i, '')
      .replace(/^Argument:\s*/i, '')
      .trim()
    if (!label) return
    const key = label.toLowerCase()
    if (seen.has(key)) return
    seen.add(key)
    anchors.push({ pageId: bookPageId(page.id, page.title, index), label, kind: page.section_type })
  })
  return anchors
}

// Stable id for a page so the rail anchor and the rendered section agree.
export function bookPageId(id: string | undefined, title: string, index: number): string {
  return id ?? `${slugForDomId(title)}-${index}`
}

export function bookAnchorDomId(commandSlug: string, pageId: string): string {
  return `book-anchor-${slugForDomId(commandSlug)}-${slugForDomId(pageId)}`
}

function slugForDomId(value: string): string {
  return (
    value
      .toLowerCase()
      .replace(/[^a-z0-9_-]+/g, '-')
      .replace(/^-+|-+$/g, '') || 'section'
  )
}
