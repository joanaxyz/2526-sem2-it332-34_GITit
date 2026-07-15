import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { KeyRound, LogOut, MonitorCog, Save, ShieldCheck, UserRound } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { z } from 'zod'

import { preferencesApi } from '@/shared/preferences/preferencesApi'
import { queryKeys } from '@/shared/api/queryKeys'
import { authApi } from '@/shared/auth/authApi'
import { useAuthStore } from '@/shared/auth/useAuth'
import {
  applyPreferences,
  persistPreferences,
  type MotionMode,
  type PlayerPreferences,
} from '@/shared/preferences/preferences'

const passwordSchema = z.object({
  current_password: z.string().min(1, 'Enter your current password.'),
  password: z.string().min(8, 'Use at least eight characters.'),
  password_confirm: z.string().min(8, 'Confirm your new password.'),
}).refine((values) => values.password === values.password_confirm, {
  path: ['password_confirm'],
  message: 'Passwords do not match.',
})
type PasswordValues = z.infer<typeof passwordSchema>

export function SettingsPage() {
  const user = useAuthStore((state) => state.user)
  const setSession = useAuthStore((state) => state.setSession)
  const clearSession = useAuthStore((state) => state.clearSession)
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const preferences = useQuery({ queryKey: queryKeys.preferences, queryFn: preferencesApi.get })
  const preferenceMutation = useMutation({
    mutationFn: preferencesApi.update,
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.preferences, data)
      persistPreferences(data)
      applyPreferences(data)
      toast.success('Preferences saved')
    },
    onError: () => {
      const saved = queryClient.getQueryData<PlayerPreferences>(queryKeys.preferences)
      if (saved) {
        persistPreferences(saved)
        applyPreferences(saved)
      }
    },
  })
  const passwordForm = useForm<PasswordValues>({ resolver: zodResolver(passwordSchema), mode: 'onBlur' })
  const passwordMutation = useMutation({
    mutationFn: authApi.changePassword,
    onSuccess: (session) => {
      setSession(session.access, session.user)
      passwordForm.reset()
      toast.success('Password updated')
    },
  })
  const revokeOthers = useMutation({
    mutationFn: authApi.revokeOtherSessions,
    onSuccess: (result) => toast.success(result.detail),
  })
  const revokeAll = useMutation({
    mutationFn: authApi.revokeAllSessions,
    onSuccess: () => {
      queryClient.clear()
      clearSession()
      navigate('/login', { replace: true })
    },
  })

  const currentPreferences: PlayerPreferences = preferences.data ?? { motion_mode: 'system' }

  function updatePreference(payload: Partial<PlayerPreferences>) {
    const next = { ...currentPreferences, ...payload }
    persistPreferences(next)
    applyPreferences(next)
    preferenceMutation.mutate(payload)
  }

  return (
    <section className="settings-page" aria-labelledby="settings-title">
      <header className="settings-hero">
        <span><MonitorCog aria-hidden="true" /></span>
        <div>
          <p>Player preferences</p>
          <h1 id="settings-title">Settings</h1>
          <p>Manage your account security and motion preferences.</p>
        </div>
      </header>

      <div className="settings-sheet">
        <section className="settings-section" aria-labelledby="account-settings-title">
          <div className="settings-section__head">
            <p className="settings-eyebrow" id="account-settings-title"><UserRound aria-hidden="true" />Account</p>
            <p className="settings-section__desc">Your current sign-in identity.</p>
          </div>
          <div className="settings-section__body">
            <div className="settings-fields settings-fields--two">
              <label><span>Username</span><input value={user?.username ?? ''} readOnly /></label>
              <label><span>Email</span><input value={user?.email ?? ''} readOnly /></label>
            </div>
            <p className="settings-note">Username and email changes require a verified-change flow and are intentionally read-only for now.</p>
          </div>
        </section>

        <section className="settings-section" aria-labelledby="motion-settings-title">
          <div className="settings-section__head">
            <p className="settings-eyebrow" id="motion-settings-title"><MonitorCog aria-hidden="true" />Motion</p>
            <p className="settings-section__desc">Choose how animated interface effects behave on this device.</p>
          </div>
          <div className="settings-section__body">
            <div className="settings-fields">
              <label>
                <span>Motion</span>
                <select
                  value={currentPreferences.motion_mode}
                  disabled={preferences.isPending || preferenceMutation.isPending}
                  onChange={(event) => updatePreference({ motion_mode: event.target.value as MotionMode })}
                >
                  <option value="system">Follow system</option>
                  <option value="reduced">Reduced</option>
                  <option value="full">Full</option>
                </select>
              </label>
            </div>
            {preferenceMutation.isError ? <p className="settings-error">{preferenceMutation.error.message}</p> : null}
          </div>
        </section>

        <section className="settings-section" aria-labelledby="security-settings-title">
          <div className="settings-section__head">
            <p className="settings-eyebrow" id="security-settings-title"><KeyRound aria-hidden="true" />Password</p>
            <p className="settings-section__desc">Changing your password invalidates older access and refresh tokens.</p>
          </div>
          <div className="settings-section__body">
            <form className="settings-password-form" onSubmit={passwordForm.handleSubmit((values) => passwordMutation.mutate(values))}>
              <label><span>Current password</span><input type="password" autoComplete="current-password" {...passwordForm.register('current_password')} />{passwordForm.formState.errors.current_password ? <small>{passwordForm.formState.errors.current_password.message}</small> : null}</label>
              <label><span>New password</span><input type="password" autoComplete="new-password" {...passwordForm.register('password')} />{passwordForm.formState.errors.password ? <small>{passwordForm.formState.errors.password.message}</small> : null}</label>
              <label><span>Confirm new password</span><input type="password" autoComplete="new-password" {...passwordForm.register('password_confirm')} />{passwordForm.formState.errors.password_confirm ? <small>{passwordForm.formState.errors.password_confirm.message}</small> : null}</label>
              {passwordMutation.isError ? <p className="settings-error">{passwordMutation.error.message}</p> : null}
              <button type="submit" className="settings-primary-action" disabled={passwordMutation.isPending}><Save aria-hidden="true" />{passwordMutation.isPending ? 'Updating' : 'Update password'}</button>
            </form>
          </div>
        </section>

        <section className="settings-section" aria-labelledby="sessions-settings-title">
          <div className="settings-section__head">
            <p className="settings-eyebrow" id="sessions-settings-title"><ShieldCheck aria-hidden="true" />Sessions</p>
            <p className="settings-section__desc">Remove access from browsers or devices you no longer use.</p>
          </div>
          <div className="settings-section__body">
            <div className="settings-session-actions">
              <button type="button" onClick={() => revokeOthers.mutate()} disabled={revokeOthers.isPending || revokeAll.isPending}><ShieldCheck aria-hidden="true" />Sign out other sessions</button>
              <button type="button" className="is-danger" onClick={() => revokeAll.mutate()} disabled={revokeAll.isPending}><LogOut aria-hidden="true" />Sign out everywhere</button>
            </div>
            {revokeOthers.isError ? <p className="settings-error">{revokeOthers.error.message}</p> : null}
            {revokeAll.isError ? <p className="settings-error">{revokeAll.error.message}</p> : null}
          </div>
        </section>
      </div>
    </section>
  )
}
