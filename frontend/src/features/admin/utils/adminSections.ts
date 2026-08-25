import {
  BarChart3,
  BookText,
  Coins,
  LayoutDashboard,
  Layers,
  Settings,
  ShieldAlert,
  Users,
  type LucideIcon,
} from 'lucide-react'
import type { ComponentType } from 'react'

import { ADMIN_ROUTES } from '@/shared/navigation/routes'

type AdminSection = {
  path: (typeof ADMIN_ROUTES)[keyof typeof ADMIN_ROUTES]
  label: string
  icon: LucideIcon
  end?: boolean
  load: () => Promise<ComponentType>
}

export const ADMIN_SECTIONS: readonly AdminSection[] = [
  {
    path: ADMIN_ROUTES.dashboard,
    label: 'Dashboard',
    icon: LayoutDashboard,
    end: true,
    load: async () => (await import('../pages/AdminDashboardPage')).AdminDashboardPage,
  },
  {
    path: ADMIN_ROUTES.users,
    label: 'Users',
    icon: Users,
    load: async () => (await import('../pages/AdminUsersPage')).AdminUsersPage,
  },
  {
    path: ADMIN_ROUTES.economy,
    label: 'Economy',
    icon: Coins,
    load: async () => (await import('../pages/AdminEconomyPage')).AdminEconomyPage,
  },
  {
    path: ADMIN_ROUTES.curriculum,
    label: 'Curriculum',
    icon: Layers,
    load: async () => (await import('../pages/AdminCurriculumPage')).AdminCurriculumPage,
  },
  {
    path: ADMIN_ROUTES.content,
    label: 'Content',
    icon: BookText,
    load: async () => (await import('../pages/AdminContentPage')).AdminContentPage,
  },
  {
    path: ADMIN_ROUTES.analytics,
    label: 'Analytics',
    icon: BarChart3,
    load: async () => (await import('../pages/AdminAnalyticsPage')).AdminAnalyticsPage,
  },
  {
    path: ADMIN_ROUTES.moderation,
    label: 'Moderation',
    icon: ShieldAlert,
    load: async () => (await import('../pages/AdminModerationPage')).AdminModerationPage,
  },
  {
    path: ADMIN_ROUTES.settings,
    label: 'Settings',
    icon: Settings,
    load: async () => (await import('../pages/AdminSettingsPage')).AdminSettingsPage,
  },
]
