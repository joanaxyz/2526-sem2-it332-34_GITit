import { Navigate, Outlet, createBrowserRouter, type RouteObject } from 'react-router-dom'

import { AdminLayout } from '@/features/admin/components/AdminLayout'
import { ADMIN_SECTIONS } from '@/features/admin/utils/adminSections'
import { AuthLayout } from '@/app/layouts/AuthLayout'
import { HomeLayout } from '@/app/layouts/HomeLayout'
import { LevelLayout } from '@/app/layouts/LevelLayout'
import { Protected } from '@/app/Protected'
import { RouteErrorPage } from '@/app/RouteErrorPage'
import { RequireCompanion } from '@/app/RequireCompanion'
import { ForgotPasswordPage } from '@/features/auth/pages/ForgotPasswordPage'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { OAuthCallbackPage } from '@/features/auth/pages/OAuthCallbackPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { ResetPasswordPage } from '@/features/auth/pages/ResetPasswordPage'
import { VerifyEmailPage } from '@/features/auth/pages/VerifyEmailPage'
import { HomePage } from '@/features/home/pages/HomePage'
import { LandingPage } from '@/features/landing/pages/LandingPage'
import { ChallengeStartPage } from '@/features/challenges/pages/ChallengeStartPage'
import { TierStartPage } from '@/features/story-map/pages/TierStartPage'
import { loadTierRunPage } from '@/features/story-map/pages/loadTierRunPage'
import {
  DESIGN_PREVIEW_STORY_MAP_ROUTE,
  ADMIN_ROUTES,
  HOME_ROUTE,
  SHOP_ROUTE,
  STORY_DETAIL_ROUTE,
} from '@/shared/navigation/routes'
import { LoadingScreen } from '@/shared/components/LoadingScreen'

/**
 * Dev-only design preview: the real Home hub view inside the real layout
 * chrome, fed by fixture data instead of the API (no auth required).
 * `import.meta.env.DEV` is statically false in production builds, so this
 * route - and its lazily imported fixture modules - are compiled away.
 */
const designPreviewRoutes: RouteObject[] = import.meta.env.DEV
  ? [
      {
        path: '/design-preview/home',
        lazy: async () => ({
          Component: (await import('@/features/home/preview/HomePreviewPage')).HomePreviewLayout,
        }),
        children: [{
          index: true,
          lazy: async () => ({
            Component: (await import('@/features/home/preview/HomePreviewPage')).Component,
          }),
        }],
      },
      {
        element: <HomeLayout />,
        children: [
          {
            path: '/design-preview/shop',
            lazy: async () => ({
              Component: (await import('@/features/shop/pages/ShopPage')).ShopPage,
            }),
          },
        ],
      },
      {
        path: '/dev/battle',
        lazy: () => import('@/features/dev/pages/BattlePlayground'),
      },
      {
        path: '/dev/drill',
        lazy: () => import('@/features/dev/pages/DrillPlayground'),
      },
      {
        path: '/dev/guides',
        lazy: () => import('@/features/dev/pages/GuidancePlayground'),
      },
      {
        path: '/dev/monster-scales',
        lazy: () => import('@/features/dev/pages/MonsterScalePlayground'),
      },
      {
        path: '/dev/outcomes',
        lazy: () => import('@/features/dev/pages/OutcomePreviewPage'),
      },
      {
        path: '/dev/loading',
        lazy: () => import('@/features/dev/pages/LoadingPreviewPage'),
      },
      {
        path: DESIGN_PREVIEW_STORY_MAP_ROUTE,
        lazy: () => import('@/features/story-map/pages/StoryMapPreviewPage'),
      },
    ]
  : []

const appRoutes: RouteObject[] = [
  ...designPreviewRoutes,
  // The public front door. It forwards a live session to the story map itself.
  { path: '/', element: <LandingPage /> },
  {
    element: <AuthLayout />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/register', element: <RegisterPage /> },
      { path: '/verify-email', element: <VerifyEmailPage /> },
      { path: '/oauth/callback', element: <OAuthCallbackPage /> },
      { path: '/forgot-password', element: <ForgotPasswordPage /> },
      { path: '/reset-password/:uid/:token', element: <ResetPasswordPage /> },
    ],
  },
  {
    element: (
      <Protected>
        <HomeLayout />
      </Protected>
    ),
    children: [
      { path: HOME_ROUTE, element: <HomePage /> },
      // Browsing Home, the story map, and repository-only challenges does not require
      // a companion. Adventure play remains protected below.
      {
        path: STORY_DETAIL_ROUTE,
        lazy: async () => ({
          Component: (await import('@/features/story-map/pages/StoryMapPage')).StoryMapPage,
        }),
      },
      {
        path: SHOP_ROUTE,
        lazy: async () => ({
          Component: (await import('@/features/shop/pages/ShopPage')).ShopPage,
        }),
      },
      {
        path: '/settings',
        lazy: async () => ({
          Component: (await import('@/features/settings/pages/SettingsPage')).SettingsPage,
        }),
      },
    ],
  },
  // Staff-only admin console (its own full-screen shell; AdminLayout redirects
  // non-staff back to /home). Pages are lazy so they stay out of the app entry.
  {
    element: (
      <Protected>
        <AdminLayout />
      </Protected>
    ),
    children: [
      ...ADMIN_SECTIONS.map((section) => ({
        path: section.path,
        lazy: async () => ({ Component: await section.load() }),
      })),
      { path: '/admin/*', element: <Navigate replace to={ADMIN_ROUTES.dashboard} /> },
    ],
  },
  {
    element: (
      <Protected>
        <LevelLayout />
      </Protected>
    ),
    children: [
      // Squire's Drill is recall practice on text, not a battle, so it sits
      // outside RequireCompanion: the rung that exists to unstick beginners
      // must not be gated behind owning a companion.
      {
        path: '/adventure-levels/:levelId/drill',
        lazy: async () => ({
          Component: (await import('@/features/drills/pages/DrillPage')).DrillPage,
        }),
      },
      { path: '/challenge-trials/:trialId', element: <ChallengeStartPage mode="start" /> },
      { path: '/challenge-trials/:trialId/replay', element: <ChallengeStartPage mode="replay" /> },
      { path: '/challenge-runs/:runId/retry', element: <ChallengeStartPage mode="retry" /> },
      {
        path: '/challenge-runs/:runId',
        lazy: async () => ({
          Component: (await import('@/features/challenges/pages/ChallengeRunPage')).ChallengeRunPage,
        }),
      },
    ],
  },
  {
    element: (
      <Protected>
        <RequireCompanion>
          <LevelLayout />
        </RequireCompanion>
      </Protected>
    ),
    children: [
      { path: '/adventure-level-tiers/:tierId/runs', element: <TierStartPage mode="start" /> },
      { path: '/adventure-level-tiers/:tierId/replay', element: <TierStartPage mode="replay" /> },
      { path: '/adventure-tier-runs/:runId/retry', element: <TierStartPage mode="retry" /> },
      {
        path: '/adventure-tier-runs/:runId',
        lazy: async () => ({
          Component: (await loadTierRunPage()).TierRunPage,
        }),
      },
    ],
  },
]

export const router = createBrowserRouter([
  {
    element: <Outlet />,
    errorElement: <RouteErrorPage />,
    hydrateFallbackElement: <LoadingScreen label="Loading application" />,
    children: appRoutes,
  },
])
