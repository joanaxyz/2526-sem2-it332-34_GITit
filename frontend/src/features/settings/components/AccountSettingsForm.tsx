import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { queryKeys } from '@/shared/api/queryKeys'
import { useServerFieldErrors } from '@/shared/api/useServerFieldErrors'
import { authApi } from '@/shared/auth/authApi'
import type { User } from '@/shared/auth/types'
import { confirmAuthSession, useAuthStore } from '@/shared/auth/useAuth'

const accountSchema = z.object({
  username: z.string().trim().min(3, 'Use at least three characters.').max(30, 'Use at most 30 characters.')
    .regex(/^[A-Za-z0-9._-]+$/, 'Use letters, numbers, dots, underscores, or hyphens only.'),
  email: z.string().trim().email('Enter a valid email address.'),
})
const codeSchema = z.object({ code: z.string().trim().regex(/^\d{6}$/, 'Enter the 6-digit code from the email.') })

export function AccountSettingsForm({ user }: { user: User }) {
  const queryClient = useQueryClient()
  const [pendingEmail, setPendingEmail] = useState<string | null>(null)
  const [resendReady, setResendReady] = useState(false)
  const form = useForm<z.infer<typeof accountSchema>>({
    resolver: zodResolver(accountSchema),
    mode: 'onBlur',
    defaultValues: { username: user.username, email: user.email },
  })
  const codeForm = useForm<z.infer<typeof codeSchema>>({ resolver: zodResolver(codeSchema) })

  function updateUser(updated: User) {
    const { accessToken, sessionGeneration } = useAuthStore.getState()
    if (accessToken) confirmAuthSession(accessToken, updated, sessionGeneration)
    queryClient.setQueryData(queryKeys.authBootstrap, updated)
    void queryClient.invalidateQueries({ queryKey: queryKeys.homeSummary })
  }

  const mutation = useMutation({
    mutationFn: authApi.updateAccount,
    onSuccess: (result) => {
      updateUser(result.user)
      form.reset({ username: result.user.username, email: result.user.email })
      if (result.pending_email) form.setValue('email', result.pending_email, { shouldDirty: true })
      setPendingEmail(result.pending_email)
      setResendReady(false)
      codeForm.reset({ code: '' })
      confirmation.reset()
      if (result.pending_email) toast.success('Check your new email for a verification code')
      else toast.success('Account updated')
    },
  })
  const confirmation = useMutation({
    mutationFn: authApi.confirmEmailChange,
    onSuccess: (updated) => {
      updateUser(updated)
      form.reset({ username: updated.username, email: updated.email })
      setPendingEmail(null)
      codeForm.reset({ code: '' })
      toast.success('Email updated')
    },
  })
  const serverFields = useServerFieldErrors(form, mutation.error, ['username', 'email'])
  const codeServerFields = useServerFieldErrors(codeForm, confirmation.error, ['code'])
  const busy = mutation.isPending || confirmation.isPending

  useEffect(() => {
    if (!pendingEmail || resendReady) return
    const timer = window.setTimeout(() => setResendReady(true), 60_000)
    return () => window.clearTimeout(timer)
  }, [pendingEmail, resendReady])

  return (
    <div className="settings-account">
      <form className="settings-account-form" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
        <div className="settings-fields settings-fields--two">
          <label>
            <span id="account-username-label">Username</span>
            <input autoComplete="username" maxLength={30} disabled={busy || !!pendingEmail} aria-labelledby="account-username-label" aria-invalid={!!form.formState.errors.username} aria-describedby={form.formState.errors.username ? 'account-username-error' : undefined} {...form.register('username')} />
            {form.formState.errors.username ? <small id="account-username-error" role="alert">{form.formState.errors.username.message}</small> : null}
          </label>
          <label>
            <span id="account-email-label">Email</span>
            <input type="email" autoComplete="email" maxLength={254} disabled={busy || !!pendingEmail} aria-labelledby="account-email-label" aria-invalid={!!form.formState.errors.email} aria-describedby={form.formState.errors.email ? 'account-email-note account-email-error' : 'account-email-note'} {...form.register('email')} />
            {form.formState.errors.email ? <small id="account-email-error" role="alert">{form.formState.errors.email.message}</small> : null}
          </label>
        </div>
        <p id="account-email-note" className="settings-note">A new email address needs a verification code before it becomes your sign-in email.</p>
        {mutation.isError && serverFields.length === 0 ? <p className="settings-error" role="alert">{mutation.error.message}</p> : null}
        {!pendingEmail ? <button type="submit" className="settings-primary-action ui-drawn-plate" disabled={busy || !form.formState.isDirty}><Save aria-hidden="true" />{mutation.isPending ? 'Saving…' : 'Save account'}</button> : null}
      </form>

      {pendingEmail ? (
        <form className="settings-account-form" onSubmit={codeForm.handleSubmit((values) => confirmation.mutate(values))}>
          <p className="settings-note" role="status">Enter the code sent to <strong>{pendingEmail}</strong>. Your current email stays active until you confirm.</p>
          <div className="settings-fields">
            <label>
              <span id="account-code-label">Email verification code</span>
              <input autoComplete="one-time-code" inputMode="numeric" maxLength={6} disabled={busy} aria-labelledby="account-code-label" aria-invalid={!!codeForm.formState.errors.code} aria-describedby={codeForm.formState.errors.code ? 'account-code-error' : undefined} {...codeForm.register('code')} />
              {codeForm.formState.errors.code ? <small id="account-code-error" role="alert">{codeForm.formState.errors.code.message}</small> : null}
            </label>
          </div>
          {confirmation.isError && codeServerFields.length === 0 ? <p className="settings-error" role="alert">{confirmation.error.message}</p> : null}
          <div className="settings-session-actions">
            <button type="submit" className="settings-primary-action ui-drawn-plate" disabled={busy}><ShieldCheck aria-hidden="true" />{confirmation.isPending ? 'Confirming…' : 'Confirm email'}</button>
            <button type="button" disabled={busy || !resendReady} onClick={() => mutation.mutate(form.getValues())}>Send a new code</button>
            <button type="button" disabled={busy} onClick={() => { setPendingEmail(null); mutation.reset(); confirmation.reset() }}>Edit email</button>
          </div>
          <p className="settings-note">Codes expire after 15 minutes. You can send a new code after one minute.</p>
        </form>
      ) : null}
    </div>
  )
}
