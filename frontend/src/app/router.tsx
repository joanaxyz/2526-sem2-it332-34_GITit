import { Navigate, createBrowserRouter } from 'react-router-dom'

import { AuthLayout } from '@/app/layouts/AuthLayout'
import { DashboardLayout } from '@/app/layouts/DashboardLayout'
import { PracticeLayout } from '@/app/layouts/PracticeLayout'
import { Protected } from '@/app/Protected'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage'
import { ReviewPracticePage } from '@/features/review/pages/ReviewPracticePage'
import { ScenarioPracticePage } from '@/features/scenarios/pages/ScenarioPracticePage'
import { LessonPage } from '@/features/modules/pages/LessonPage'
import { ModulesPage } from '@/features/modules/pages/ModulesPage'

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
      { path: '/units', element: <ModulesPage /> },
      { path: '/modules', element: <ModulesPage /> },
      { path: '/lessons/:lessonId', element: <LessonPage /> },
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
