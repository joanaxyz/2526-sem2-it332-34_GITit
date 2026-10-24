import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { Eye, EyeOff, Loader2, UserPlus } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useForm, useWatch } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { authApi, type RegisterPayload } from '@/shared/auth/authApi'
import { presentAuthError } from '@/features/auth/api/authError'
import { verifyEmailPath } from '@/features/auth/api/emailVerification'
import { OAuthButtons } from '@/features/auth/components/OAuthButtons'
import { PasswordStrengthIndicator } from '@/features/auth/components/PasswordStrengthIndicator'
import { useServerFieldErrors } from '@/shared/api/useServerFieldErrors'
import { cn } from '@/shared/utils/cn'

const usernamePattern = /^[A-Za-z0-9._-]{3,30}$/

const schema = z
  .object({
    username: z
      .string()
      .trim()
      .min(3, 'Use at least three characters.')
      .max(30, 'Use at most 30 characters.')
      .regex(usernamePattern, 'Use letters, numbers, dots, underscores, or hyphens only.'),
    email: z
      .string()
      .trim()
      .email('Enter a valid email address.')
      .transform((value) => value.toLowerCase()),
    password: z.string().min(8, 'Use at least eight characters.'),
    password_confirm: z.string().min(8, 'Confirm your password.'),
  })
  .refine((data) => data.password === data.password_confirm, {
    path: ['password_confirm'],
    message: 'Passwords do not match.',
  })

type FormValues = z.infer<typeof schema>

export function RegisterForm() {
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)
  const [lastSubmittedValues, setLastSubmittedValues] = useState<FormValues | null>(null)
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    mode: 'onBlur',
    reValidateMode: 'onBlur',
  })
  const passwordValue = useWatch({ control: form.control, name: 'password' }) ?? ''
  const mutation = useMutation({
    mutationFn: (payload: RegisterPayload) => authApi.register(payload),
    // The account stays locked until the emailed code is entered; confirming
    // it on the next screen signs the player straight in.
    onSuccess: (response) => navigate(verifyEmailPath(response.user.email), { replace: true }),
  })
  const errorPresentation = useMemo(
    () => (mutation.error ? presentAuthError(mutation.error) : null),
    [mutation.error],
  )
  // Server-side rules the form cannot know (Django's password validators, a
  // username taken since the page loaded) belong on the offending input.
  const serverFields = useServerFieldErrors(
    form,
    mutation.error,
    ['username', 'email', 'password', 'password_confirm'],
    errorPresentation?.fieldErrors,
  )

  function submitRegistration(values: FormValues) {
    mutation.mutate({
      username: values.username,
      email: values.email,
      password: values.password,
      password_confirm: values.password_confirm,
    })
  }

  return (
    <form
      className="auth-form auth-form--compact"
      onSubmit={form.handleSubmit((values) => {
        setLastSubmittedValues(values)
        submitRegistration(values)
      })}
    >
      <div className="auth-form-heading">
        <h2>Create account</h2>
        <p>Begin your journey up the Spire.</p>
      </div>
      <label className="auth-field">
        <span>Username</span>
        <input
          className={cn('auth-input', form.formState.errors.username && 'is-error')}
          placeholder="Username"
          autoComplete="username"
          {...form.register('username')}
        />
        {form.formState.errors.username ? <small className="auth-error">{form.formState.errors.username.message}</small> : null}
      </label>
      <label className="auth-field">
        <span>Email</span>
        <input
          className={cn('auth-input', form.formState.errors.email && 'is-error')}
          placeholder="Email"
          autoComplete="email"
          {...form.register('email')}
        />
        {form.formState.errors.email ? <small className="auth-error">{form.formState.errors.email.message}</small> : null}
      </label>
      <label className="auth-field">
        <span>Password</span>
        <div className="auth-password-field">
          <input
            className={cn('auth-input', form.formState.errors.password && 'is-error')}
            type={showPassword ? 'text' : 'password'}
            placeholder="Password"
            autoComplete="new-password"
            {...form.register('password')}
          />
          <button
            type="button"
            className="auth-password-toggle"
            onClick={() => setShowPassword((value) => !value)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          </button>
        </div>
        {form.formState.errors.password ? <small className="auth-error">{form.formState.errors.password.message}</small> : null}
        <PasswordStrengthIndicator password={passwordValue} />
      </label>
      <label className="auth-field">
        <span>Confirm password</span>
        <div className="auth-password-field">
          <input
            className={cn('auth-input', form.formState.errors.password_confirm && 'is-error')}
            type={showPasswordConfirm ? 'text' : 'password'}
            placeholder="Confirm password"
            autoComplete="new-password"
            {...form.register('password_confirm')}
          />
          <button
            type="button"
            className="auth-password-toggle"
            onClick={() => setShowPasswordConfirm((value) => !value)}
            aria-label={showPasswordConfirm ? 'Hide password confirmation' : 'Show password confirmation'}
          >
            {showPasswordConfirm ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          </button>
        </div>
        {form.formState.errors.password_confirm ? <small className="auth-error">{form.formState.errors.password_confirm.message}</small> : null}
      </label>
      {errorPresentation && serverFields.length === 0 ? (
        <div className="auth-error-box">
          <p>{errorPresentation.message}</p>
          {errorPresentation.retryable && lastSubmittedValues ? (
            <button
              type="button"
              className="auth-retry"
              onClick={() => submitRegistration(lastSubmittedValues)}
            >
              Retry
            </button>
          ) : null}
        </div>
      ) : null}
      <button type="submit" className="auth-submit ui-drawn-plate" disabled={mutation.isPending}>
        {mutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <UserPlus data-icon="inline-start" />}
        {mutation.isPending ? 'Creating account' : 'Create account'}
      </button>
      <OAuthButtons />
      <p className="auth-alt-link">
        Already registered?{' '}
        <Link to="/login">
          Sign in
        </Link>
      </p>
    </form>
  )
}
