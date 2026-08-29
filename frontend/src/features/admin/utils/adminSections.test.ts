import { describe, expect, it } from 'vitest'

import { ADMIN_ROUTES } from '@/shared/navigation/routes'

import { ADMIN_SECTIONS } from './adminSections'

describe('admin section registry', () => {
  it('is the complete route and navigation registry', () => {
    expect(ADMIN_SECTIONS.map((section) => section.path)).toEqual(
      Object.values(ADMIN_ROUTES),
    )
    expect(new Set(ADMIN_SECTIONS.map((section) => section.path)).size).toBe(
      ADMIN_SECTIONS.length,
    )
    expect(ADMIN_SECTIONS.every((section) => section.label && section.load)).toBe(true)
  })
})
