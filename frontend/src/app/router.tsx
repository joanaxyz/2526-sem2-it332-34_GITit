import { Navigate, createBrowserRouter } from 'react-router-dom'

import { AuthLayout } from '@/app/layouts/AuthLayout'
import { DashboardLayout } from '@/app/layouts/DashboardLayout'
import { PracticeLayout } from '@/app/layouts/PracticeLayout'
import { Protected } from '@/app/Protected'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage'
import { PerformancePage } from '@/features/dashboard/pages/PerformancePage'
import { AdventureRunPage } from '@/features/command-adventures/pages/AdventureRunPage'
import { CommandAdventurePage } from '@/features/command-adventures/pages/CommandAdventurePage'
import { ChallengeRunPage } from '@/features/challenges/pages/ChallengeRunPage'
import { StoreyMapPage } from '@/features/storeys/pages/StoreyMapPage'

export const router = createBrowserRouter([
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
      { path: '/performance', element: <PerformancePage /> },
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
