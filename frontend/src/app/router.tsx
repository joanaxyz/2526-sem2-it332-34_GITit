import { Navigate, createBrowserRouter, type RouteObject } from 'react-router-dom'

import { AuthLayout } from '@/app/layouts/AuthLayout'
import { DashboardLayout } from '@/app/layouts/DashboardLayout'
import { PracticeLayout } from '@/app/layouts/PracticeLayout'
import { Protected } from '@/app/Protected'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage'
import { StatsPage } from '@/features/stats/pages/StatsPage'
import { AdventureRunPage } from '@/features/command-adventures/pages/AdventureRunPage'
import { CommandAdventurePage } from '@/features/command-adventures/pages/CommandAdventurePage'
import { ChallengeRunPage } from '@/features/challenges/pages/ChallengeRunPage'
import { StoreyMapPage } from '@/features/storeys/pages/StoreyMapPage'

/**
 * ⚠ Dev-only design previews: the real Dashboard/Stats views inside the real
 * layout chrome, fed by fixture data instead of the API (no auth required).
 * `import.meta.env.DEV` is statically false in production builds, so these
 * routes — and their lazily imported fixture modules — are compiled away.
 */
const designPreviewRoutes: RouteObject[] = import.meta.env.DEV
  ? [
      {
        element: <DashboardLayout />,
        children: [
          {
            path: '/design-preview/dashboard',
            lazy: () => import('@/features/dashboard/preview/DashboardPreviewPage'),
          },
          {
            path: '/design-preview/stats',
            lazy: () => import('@/features/stats/preview/StatsPreviewPage'),
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
        <DashboardLayout />
      </Protected>
    ),
    children: [
      { path: '/', element: <Navigate replace to="/dashboard" /> },
      { path: '/dashboard', element: <DashboardPage /> },
      { path: '/tower', element: <StoreyMapPage /> },
      { path: '/stats', element: <StatsPage /> },
      { path: '/performance', element: <Navigate replace to="/stats" /> },
    ],
  },
  {
    element: (
      <Protected>
        <PracticeLayout />
      </Protected>
    ),
    children: [
      { path: '/challenge-runs/:runId', element: <ChallengeRunPage /> },
      { path: '/command-adventures/:adventureSlug', element: <CommandAdventurePage /> },
      { path: '/adventure-runs/:runId', element: <AdventureRunPage /> },
    ],
  },
])
