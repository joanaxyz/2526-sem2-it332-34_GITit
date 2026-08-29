import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { Eye, EyeOff, KeyRound, Loader2 } from 'lucide-react'
import { useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { Link, useParams } from 'react-router-dom'
import { z } from 'zod'

import { PasswordStrengthIndicator } from '@/features/auth/components/PasswordStrengthIndicator'
import { authApi } from '@/shared/auth/authApi'

const schema = z.object({
  password: z.string().min(8, 'Use at least eight characters.'),
  password_confirm: z.string().min(8, 'Confirm your password.'),
}).refine((values) => values.password === values.password_confirm, {
  path: ['password_confirm'],
  message: 'Passwords do not match.',
})
type FormValues = z.infer<typeof schema>

export function ResetPasswordForm() {
  const { uid = '', token = '' } = useParams()
  const [showPassword, setShowPassword] = useState(false)
  const form = useForm<FormValues>({ resolver: zodResolver(schema), mode: 'onBlur' })
  const password = useWatch({ control: form.control, name: 'password' }) ?? ''
  const mutation = useMutation({
    mutationFn: (values: FormValues) => authApi.confirmPasswordReset({ uid, token, ...values }),
  })

  if (mutation.isSuccess) {
    return (
      <div className="auth-form auth-forgot" role="status">
        <span className="auth-reset-icon"><KeyRound aria-hidden="true" /></span>
        <div className="auth-form-heading"><h2>Password updated</h2><p>{mutation.data.detail}</p></div>
        <Link className="auth-submit auth-link-button" to="/login">Sign in</Link>
      </div>
    )
  }

  return (
    <form className="auth-form" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <div className="auth-form-heading"><h2>Choose a new password</h2><p>This link can only be used once.</p></div>
      <label className="auth-field">
        <span>New password</span>
        <div className="auth-password-field">
          <input className="auth-input" type={showPassword ? 'text' : 'password'} autoComplete="new-password" {...form.register('password')} />
          <button type="button" className="auth-password-toggle" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? 'Hide password' : 'Show password'}>
            {showPassword ? <EyeOff /> : <Eye />}
          </button>
        </div>
        {form.formState.errors.password ? <small className="auth-error">{form.formState.errors.password.message}</small> : null}
        <PasswordStrengthIndicator password={password} />
      </label>
      <label className="auth-field">
        <span>Confirm new password</span>
        <input className="auth-input" type={showPassword ? 'text' : 'password'} autoComplete="new-password" {...form.register('password_confirm')} />
        {form.formState.errors.password_confirm ? <small className="auth-error">{form.formState.errors.password_confirm.message}</small> : null}
      </label>
      {mutation.isError ? <p className="auth-error-box">{mutation.error.message}</p> : null}
      <button type="submit" className="auth-submit" disabled={mutation.isPending || !uid || !token}>
        {mutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <KeyRound aria-hidden="true" />}
        {mutation.isPending ? 'Updating password' : 'Reset password'}
      </button>
    </form>
  )
}
