import { Navigate, createBrowserRouter } from 'react-router-dom'
import type { ReactElement } from 'react'

import { AuthLayout } from '@/app/layouts/AuthLayout'
import { DashboardLayout } from '@/app/layouts/DashboardLayout'
import { PracticeLayout } from '@/app/layouts/PracticeLayout'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage'
import { ReviewPracticePage } from '@/features/review/pages/ReviewPracticePage'
import { ScenarioPracticePage } from '@/features/scenarios/pages/ScenarioPracticePage'
import { ScenarioSelectionPage } from '@/features/scenarios/pages/ScenarioSelectionPage'
import { LessonOverviewPage } from '@/features/units/pages/LessonOverviewPage'
import { UnitsPage } from '@/features/units/pages/UnitsPage'
import { useAuthStore } from '@/features/auth/hooks/useAuth'

function Protected({ children }: { children: ReactElement }) {
  const token = useAuthStore.getState().accessToken
  if (!token) return <Navigate replace to="/login" />
  return children
}

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
      { path: '/units', element: <UnitsPage /> },
      { path: '/lessons/:lessonId', element: <LessonOverviewPage /> },
      { path: '/lessons/:lessonId/scenarios', element: <ScenarioSelectionPage /> },
    ],
  },
  {
    element: (
      <Protected>
        <PracticeLayout />
      </Protected>
    ),
    children: [
      { path: '/practice/:sessionId', element: <ScenarioPracticePage /> },
      { path: '/review/:sessionId', element: <ReviewPracticePage /> },
    ],
  },
])
