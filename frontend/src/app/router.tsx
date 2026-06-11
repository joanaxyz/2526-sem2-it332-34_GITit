import { Navigate, createBrowserRouter, type RouteObject } from 'react-router-dom'

import { AuthLayout } from '@/app/layouts/AuthLayout'
import { HomeLayout } from '@/app/layouts/HomeLayout'
import { PracticeLayout } from '@/app/layouts/PracticeLayout'
import { Protected } from '@/app/Protected'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { HomePage } from '@/features/home/pages/HomePage'
import { AdventureRunPage } from '@/features/command-adventures/pages/AdventureRunPage'
import { AdventureStartPage } from '@/features/command-adventures/pages/AdventureStartPage'
import { ChallengeRunPage } from '@/features/challenges/pages/ChallengeRunPage'
import { ChallengeStartPage } from '@/features/challenges/pages/ChallengeStartPage'
import { StoreyMapPage } from '@/features/storeys/pages/StoreyMapPage'

/**
 * ⚠ Dev-only design preview: the real Home hub view inside the real layout
 * chrome, fed by fixture data instead of the API (no auth required).
 * `import.meta.env.DEV` is statically false in production builds, so this
 * route — and its lazily imported fixture modules — are compiled away.
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
  {
    element: (
      <Protected>
        <HomeLayout />
      </Protected>
    ),
    children: [
      { path: '/', element: <Navigate replace to="/home" /> },
      { path: '/home', element: <HomePage /> },
      { path: '/tower', element: <StoreyMapPage /> },
      /* Legacy routes — stats/performance now live on Home's Stats tab. */
      { path: '/dashboard', element: <Navigate replace to="/home" /> },
      { path: '/stats', element: <Navigate replace to="/home?tab=stats" /> },
      { path: '/performance', element: <Navigate replace to="/home?tab=stats" /> },
    ],
  },
  {
    element: (
      <Protected>
        <PracticeLayout />
      </Protected>
    ),
    children: [
      { path: '/challenge-quests/:questId', element: <ChallengeStartPage mode="start" /> },
      { path: '/challenge-quests/:questId/review', element: <ChallengeStartPage mode="review" /> },
      { path: '/challenge-runs/:runId/retry', element: <ChallengeStartPage mode="retry" /> },
      { path: '/challenge-runs/:runId', element: <ChallengeRunPage /> },
      { path: '/command-adventures/:adventureSlug', element: <AdventureStartPage /> },
      { path: '/adventure-runs/:runId', element: <AdventureRunPage /> },
    ],
  },
])
