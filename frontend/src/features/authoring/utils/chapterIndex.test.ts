import { describe, expect, it } from 'vitest'

import { findChapterForIndex } from '@/features/authoring/utils/chapterIndex'
import type { AuthoringChapter } from '@/features/authoring/types'

function makeChapter(id: number, title: string, sort_order: number): AuthoringChapter {
  return {
    id,
    owner_id: 1,
    slug: title.toLowerCase().replace(/\s+/g, '-'),
    title,
    summary: '',
    sort_order,
    created_at: '',
    updated_at: '',
  }
}

describe('findChapterForIndex', () => {
  it('maps a map band to the chapter with the matching sort order', () => {
    const chapters = [makeChapter(10, 'Chapter 1', 0), makeChapter(11, 'Chapter 2', 1)]

    expect(findChapterForIndex(chapters, 2)?.id).toBe(11)
  })

  it('returns null for invalid or missing chapter indexes', () => {
    const chapters = [makeChapter(10, 'Chapter 1', 0)]

    expect(findChapterForIndex(chapters, null)).toBeNull()
    expect(findChapterForIndex(chapters, 0)).toBeNull()
    expect(findChapterForIndex(chapters, Number.NaN)).toBeNull()
  })
})
