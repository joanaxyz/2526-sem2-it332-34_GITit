import { Navigate, createBrowserRouter, type RouteObject } from 'react-router-dom'

import { AuthLayout } from '@/app/layouts/AuthLayout'
import { HomeLayout } from '@/app/layouts/HomeLayout'
import { LevelLayout } from '@/app/layouts/LevelLayout'
import { Protected } from '@/app/Protected'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { HomePage } from '@/features/home/pages/HomePage'
import { AdventureStartPage } from '@/features/command-adventures/pages/AdventureStartPage'
import { ChallengeStartPage } from '@/features/challenges/pages/ChallengeStartPage'

/**
 * Dev-only design preview: the real Home hub view inside the real layout
 * chrome, fed by fixture data instead of the API (no auth required).
 * `import.meta.env.DEV` is statically false in production builds, so this
 * route - and its lazily imported fixture modules - are compiled away.
 */
const designPreviewRoutes: RouteObject[] = import.meta.env.DEV
  ? [
      {
        element: <HomeLayout />,
        children: [
          {
            path: '/design-preview/home',
            lazy: () => import('@/features/home/preview/HomePreviewPage'),
          },
        ],
      },
      {
        path: '/dev/battle',
        lazy: () => import('@/features/dev/BattlePlayground'),
      },
    ]
  : []

export const router = createBrowserRouter([
  ...designPreviewRoutes,
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
    ],
  },
  // Public, no-auth view of a shared tower (copiable link target).
  {
    path: '/tower/shared/:designId',
    lazy: async () => ({
      Component: (await import('@/features/tower-designs/pages/SharedTowerPage')).SharedTowerPage,
    }),
  },
  {
    element: (
      <Protected>
        <HomeLayout />
      </Protected>
    ),
    children: [
      { path: '/', element: <Navigate replace to="/home" /> },
      { path: '/home', element: <HomePage /> },
      // Route-level code splitting: the tower (motion) and the run pages
      // (reactflow + dagre via the level workspace) carry the heaviest
      // dependencies, so they load on navigation instead of in the entry chunk.
      {
        path: '/tower',
        lazy: async () => ({
          Component: (await import('@/features/tower-map/pages/TowerMapPage')).TowerMapPage,
        }),
      },
      /* Mine moved inside the Tower page via the in-tower picker (?view=mine). */
      { path: '/my-tower', element: <Navigate replace to="/tower?view=mine" /> },
      {
        path: '/tower/editor',
        lazy: async () => ({
          Component: (await import('@/features/tower-designs/pages/TowerEditorPage')).TowerEditorPage,
        }),
      },
      {
        path: '/tower/editor/:designId',
        lazy: async () => ({
          Component: (await import('@/features/tower-designs/pages/TowerEditorPage')).TowerEditorPage,
        }),
      },
      {
        path: '/authoring',
        lazy: async () => ({
          Component: (await import('@/features/authoring/pages/AuthoringLibraryPage')).AuthoringLibraryPage,
        }),
      },
      {
        path: '/authoring/new/:kind',
        lazy: async () => ({
          Component: (await import('@/features/authoring/pages/ContentEditorPage')).ContentEditorPage,
        }),
      },
      {
        path: '/authoring/:definitionId',
        lazy: async () => ({
          Component: (await import('@/features/authoring/pages/ContentEditorPage')).ContentEditorPage,
        }),
      },
      { path: '/store', element: <Navigate replace to="/shop" /> },
      { path: '/marketplace', element: <Navigate replace to="/shop" /> },
      {
        path: '/shop',
        lazy: async () => ({
          Component: (await import('@/features/marketplace/pages/MarketplacePage')).MarketplacePage,
        }),
      },
      {
        path: '/gallery',
        lazy: async () => ({
          Component: (await import('@/features/gallery/pages/GalleryPage')).GalleryPage,
        }),
      },
      /* Legacy routes - stats/performance now live on Home's Stats tab. */
      { path: '/dashboard', element: <Navigate replace to="/home" /> },
      { path: '/stats', element: <Navigate replace to="/home?tab=stats" /> },
      { path: '/performance', element: <Navigate replace to="/home?tab=stats" /> },
    ],
  },
  {
    element: (
      <Protected>
        <LevelLayout />
      </Protected>
    ),
    children: [
      { path: '/challenge-levels/:levelId', element: <ChallengeStartPage mode="start" /> },
      { path: '/challenge-levels/:levelId/review', element: <ChallengeStartPage mode="review" /> },
      { path: '/challenge-runs/:runId/retry', element: <ChallengeStartPage mode="retry" /> },
      {
        path: '/challenge-runs/:runId',
        lazy: async () => ({
          Component: (await import('@/features/challenges/pages/ChallengeRunPage')).ChallengeRunPage,
        }),
      },
      { path: '/command-adventures/:adventureSlug', element: <AdventureStartPage /> },
      {
        path: '/adventure-runs/:runId',
        lazy: async () => ({
          Component: (await import('@/features/command-adventures/pages/AdventureRunPage'))
            .AdventureRunPage,
        }),
      },
    ],
  },
])
