import { Navigate, createBrowserRouter } from 'react-router-dom'

import { AuthLayout } from '@/app/layouts/AuthLayout'
import { DashboardLayout } from '@/app/layouts/DashboardLayout'
import { PracticeLayout } from '@/app/layouts/PracticeLayout'
import { Protected } from '@/app/Protected'
import { LoginPage } from '@/features/auth/pages/LoginPage'
import { RegisterPage } from '@/features/auth/pages/RegisterPage'
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage'
import { PerformancePage } from '@/features/dashboard/pages/PerformancePage'
import { PracticePage } from '@/features/practice/pages/PracticePage'
import { ReviewPracticePage } from '@/features/review/pages/ReviewPracticePage'
import { TowerPage } from '@/features/modules/pages/ModulesPage'

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
      { path: '/tower', element: <TowerPage /> },
      { path: '/modules', element: <TowerPage /> },
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
      { path: '/practice/:sessionId', element: <PracticePage /> },
      { path: '/review/:sessionId', element: <ReviewPracticePage /> },
    ],
  },
])
