import { describe, expect, it } from 'vitest'

import { ADMIN_ROUTES } from './routes'

describe('admin routes', () => {
  it('contains only live, unique admin destinations', () => {
    const routes = Object.values(ADMIN_ROUTES)

    expect(new Set(routes).size).toBe(routes.length)
    expect(routes).not.toContain('/admin/assets')
    expect(routes).not.toContain('/admin/shop')
    expect(routes).toEqual([
      '/admin',
      '/admin/users',
      '/admin/economy',
      '/admin/curriculum',
      '/admin/content',
      '/admin/analytics',
      '/admin/moderation',
      '/admin/settings',
    ])
  })
})
