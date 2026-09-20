import {
  BarChart3,
  BookText,
  Coins,
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
  hidden?: boolean
  load: () => Promise<ComponentType>
}

export const ADMIN_SECTIONS: readonly AdminSection[] = [
  {
    path: ADMIN_ROUTES.dashboard,
    label: 'KPI Overview',
    icon: BarChart3,
    end: true,
    load: async () => (await import('../pages/AdminDashboardPage')).AdminDashboardPage,
  },
  {
    path: ADMIN_ROUTES.users,
    label: 'Learners',
    icon: Users,
    load: async () => (await import('../pages/AdminUsersPage')).AdminUsersPage,
  },
  {
    path: ADMIN_ROUTES.economy,
    label: 'Economy',
    icon: Coins,
    hidden: true,
    load: async () => (await import('../pages/AdminEconomyPage')).AdminEconomyPage,
  },
  {
    path: ADMIN_ROUTES.curriculum,
    label: 'Curriculum',
    icon: Layers,
    hidden: true,
    load: async () => (await import('../pages/AdminCurriculumPage')).AdminCurriculumPage,
  },
  {
    path: ADMIN_ROUTES.content,
    label: 'Content',
    icon: BookText,
    hidden: true,
    load: async () => (await import('../pages/AdminContentPage')).AdminContentPage,
  },
  {
    path: ADMIN_ROUTES.analytics,
    label: 'Analytics',
    icon: BarChart3,
    hidden: true,
    load: async () => (await import('../pages/AdminAnalyticsPage')).AdminAnalyticsPage,
  },
  {
    path: ADMIN_ROUTES.moderation,
    label: 'Moderation',
    icon: ShieldAlert,
    hidden: true,
    load: async () => (await import('../pages/AdminModerationPage')).AdminModerationPage,
  },
  {
    path: ADMIN_ROUTES.settings,
    label: 'Settings',
    icon: Settings,
    hidden: true,
    load: async () => (await import('../pages/AdminSettingsPage')).AdminSettingsPage,
  },
]

export const ADMIN_NAV_SECTIONS = ADMIN_SECTIONS.filter((s) => !s.hidden)
