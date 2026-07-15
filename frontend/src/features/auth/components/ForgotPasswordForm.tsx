import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { ArrowLeft, Loader2, Mail } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'

import { authApi } from '@/shared/auth/authApi'

const schema = z.object({ email: z.string().trim().email('Enter a valid email address.') })
type FormValues = z.infer<typeof schema>

export function ForgotPasswordForm() {
  const form = useForm<FormValues>({ resolver: zodResolver(schema), mode: 'onBlur' })
  const mutation = useMutation({ mutationFn: authApi.requestPasswordReset })

  if (mutation.isSuccess) {
    return (
      <div className="auth-form auth-forgot" role="status">
        <span className="auth-reset-icon"><Mail aria-hidden="true" /></span>
        <div className="auth-form-heading">
          <h2>Check your email</h2>
          <p>{mutation.data.detail}</p>
        </div>
        <p className="auth-muted-copy">The same confirmation is shown whether or not an account exists.</p>
        <Link to="/login" className="auth-back-link"><ArrowLeft aria-hidden="true" />Back to sign in</Link>
      </div>
    )
  }

  return (
    <form className="auth-form" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <div className="auth-form-heading">
        <h2>Forgot your password?</h2>
        <p>Enter your account email and we’ll send a secure reset link.</p>
      </div>
      <label className="auth-field">
        <span>Email address</span>
        <input className="auth-input" type="email" autoComplete="email" placeholder="you@example.com" {...form.register('email')} />
        {form.formState.errors.email ? <small className="auth-error">{form.formState.errors.email.message}</small> : null}
      </label>
      {mutation.isError ? <p className="auth-error-box">{mutation.error.message}</p> : null}
      <button type="submit" className="auth-submit" disabled={mutation.isPending}>
        {mutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <Mail aria-hidden="true" />}
        {mutation.isPending ? 'Sending reset link' : 'Send reset link'}
      </button>
      <Link to="/login" className="auth-back-link"><ArrowLeft aria-hidden="true" />Back to sign in</Link>
    </form>
  )
}
