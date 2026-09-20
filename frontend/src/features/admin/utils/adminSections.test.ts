import { describe, expect, it } from 'vitest'

import { ADMIN_ROUTES } from '@/shared/navigation/routes'

import { ADMIN_NAV_SECTIONS, ADMIN_SECTIONS } from './adminSections'

describe('admin section registry', () => {
  it('registers all admin routes for the router', () => {
    expect(ADMIN_SECTIONS.map((section) => section.path)).toEqual(
      Object.values(ADMIN_ROUTES),
    )
    expect(new Set(ADMIN_SECTIONS.map((section) => section.path)).size).toBe(
      ADMIN_SECTIONS.length,
    )
    expect(ADMIN_SECTIONS.every((section) => section.label && section.load)).toBe(true)
  })

  it('nav sections are a subset of all sections with no duplicates', () => {
    const allPaths = new Set(ADMIN_SECTIONS.map((s) => s.path))
    expect(ADMIN_NAV_SECTIONS.every((s) => allPaths.has(s.path))).toBe(true)
    expect(new Set(ADMIN_NAV_SECTIONS.map((s) => s.path)).size).toBe(ADMIN_NAV_SECTIONS.length)
    expect(ADMIN_NAV_SECTIONS.every((s) => !s.hidden)).toBe(true)
  })
})
