import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
import { RouterProvider, matchRoutes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '@/shared/auth/useAuth'
import { router } from './router'

vi.mock('@/app/layouts/HomeLayout', async () => {
  const { Outlet } = await import('react-router-dom')
  return { HomeLayout: () => <Outlet /> }
})
vi.mock('@/features/home/pages/HomePage', () => ({ HomePage: () => <h1>Home</h1> }))
vi.mock('@/features/story-map/pages/StoryMapPage', () => ({ StoryMapPage: () => <h1>Story map</h1> }))

describe('app entry routing', () => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  afterEach(() => {
    cleanup()
    client.clear()
    useAuthStore.setState({ accessToken: null, user: null })
  })

  it.each([
    ['/', 'Story map', '/stories/arcane-spire'],
    ['/home', 'Home', '/home'],
  ])('opens %s at the correct destination', async (entry, title, expectedPath) => {
    useAuthStore.setState({
      accessToken: 'test-token',
      user: { id: 13, username: 'archivist', email: 'archivist@example.test', is_staff: false },
    })
    await router.navigate(entry)
    render(<QueryClientProvider client={client}><RouterProvider router={router} /></QueryClientProvider>)
    expect(await screen.findByRole('heading', { name: title })).toBeInTheDocument()
    expect(router.state.location.pathname).toBe(expectedPath)
  })

  it('shows a not-found page for an address with no route', async () => {
    await router.navigate('/this-route-does-not-exist')
    render(<QueryClientProvider client={client}><RouterProvider router={router} /></QueryClientProvider>)
    expect(await screen.findByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Back to GIT it!' })).toBeInTheDocument()
    expect(screen.queryByText(/Hey developer/)).not.toBeInTheDocument()
  })

  it.each([
    '/stories',
    '/stories/',
    '/tower',
    '/towers',
    '/towers/arcane-spire',
    '/tower/shared/1',
    '/tower/editor',
    '/tower/editor/official',
    '/tower/editor/1',
    '/archive',
    '/archive/shared/1',
    '/archive/editor',
    '/archive/editor/1',
    '/my-tower',
    '/level-editor',
    '/level-editor/new/adventure',
    '/level-editor/chapters/1',
    '/design-preview/tower',
    '/performance',
    '/gallery',
    '/dashboard',
    '/stats',
    '/store',
  ])('does not register the retired URL %s', (pathname) => {
    expect(matchRoutes(router.routes, pathname)).toBeNull()
  })

  it.each([
    '/stories/arcane-spire',
    '/shop',
    '/adventure-level-tiers/1/runs',
    '/adventure-level-tiers/1/replay',
    '/admin/analytics',
  ])('keeps the current URL %s registered', (pathname) => {
    expect(matchRoutes(router.routes, pathname)).not.toBeNull()
  })
})
