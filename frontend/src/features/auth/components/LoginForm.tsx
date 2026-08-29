import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Eye, EyeOff, Loader2, LogIn } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { authApi } from '@/shared/auth/authApi'
import { presentAuthError } from '@/features/auth/api/authError'
import { useAuthStore } from '@/shared/auth/useAuth'
import { cn } from '@/shared/utils/cn'

const usernamePattern = /^[A-Za-z0-9._-]{3,30}$/

const schema = z.object({
  identifier: z
    .string()
    .trim()
    .min(1, 'Username or email is required.')
    .refine(
      (value) => (value.includes('@') ? z.string().email().safeParse(value).success : usernamePattern.test(value)),
      'Use your username or a valid email address.',
    ),
  password: z.string().min(1, 'Password is required.'),
})

type FormValues = z.infer<typeof schema>

export function LoginForm() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setSession = useAuthStore((state) => state.setSession)
  const [showPassword, setShowPassword] = useState(false)
  const [lastSubmittedValues, setLastSubmittedValues] = useState<FormValues | null>(null)
  const [lockoutRemaining, setLockoutRemaining] = useState(0)
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    mode: 'onBlur',
    reValidateMode: 'onBlur',
  })
  const mutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      queryClient.clear()
      setSession(data.access, data.user)
      navigate('/home')
    },
  })
  const errorPresentation = useMemo(
    () => (mutation.error ? presentAuthError(mutation.error) : null),
    [mutation.error],
  )
  const isLocked = lockoutRemaining > 0

  useEffect(() => {
    if (!errorPresentation?.retryAfterSeconds) return
    const timeoutId = window.setTimeout(() => {
      setLockoutRemaining(errorPresentation.retryAfterSeconds ?? 0)
    }, 0)
    return () => window.clearTimeout(timeoutId)
  }, [errorPresentation])

  useEffect(() => {
    if (!isLocked) return
    const intervalId = window.setInterval(() => {
      setLockoutRemaining((value) => Math.max(0, value - 1))
    }, 1000)
    return () => window.clearInterval(intervalId)
  }, [isLocked])

  return (
    <form
      className="auth-form"
      onSubmit={form.handleSubmit((values) => {
        setLastSubmittedValues(values)
        mutation.mutate(values)
      })}
    >
      <div className="auth-form-heading">
        <h2>Sign in</h2>
        <p>Welcome back, Archivist.</p>
      </div>

      <label className="auth-field">
        <span>Username or email</span>
        <input
          className={cn('auth-input', form.formState.errors.identifier && 'is-error')}
          placeholder="Username or email"
          autoComplete="username"
          disabled={isLocked}
          {...form.register('identifier')}
        />
        {form.formState.errors.identifier ? (
          <small className="auth-error">{form.formState.errors.identifier.message}</small>
        ) : null}
      </label>

      <label className="auth-field">
        <span className="auth-field-row">
          Password
          <Link
            to="/forgot-password"
            className="auth-link"
          >
            Forgot password?
          </Link>
        </span>
        <div className="auth-password-field">
          <input
            className={cn('auth-input', form.formState.errors.password && 'is-error')}
            type={showPassword ? 'text' : 'password'}
            placeholder="Password"
            autoComplete="current-password"
            disabled={isLocked}
            {...form.register('password')}
          />
          <button
            type="button"
            className="auth-password-toggle"
            onClick={() => setShowPassword((value) => !value)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            disabled={isLocked}
          >
            {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          </button>
        </div>
        {form.formState.errors.password ? (
          <small className="auth-error">{form.formState.errors.password.message}</small>
        ) : null}
      </label>

      {isLocked ? (
        <p className="auth-error-box">
          Too many failed attempts. Try again in{' '}
          <span>{lockoutRemaining}s</span>.
        </p>
      ) : null}

      {errorPresentation ? (
        <div className="auth-error-box">
          <p>{errorPresentation.message}</p>
          {errorPresentation.retryable && lastSubmittedValues ? (
            <button
              type="button"
              className="auth-retry"
              onClick={() => mutation.mutate(lastSubmittedValues)}
            >
              Retry
            </button>
          ) : null}
        </div>
      ) : null}

      <button type="submit" className="auth-submit" disabled={mutation.isPending || isLocked}>
        {mutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <LogIn data-icon="inline-start" />}
        {mutation.isPending ? 'Signing in' : 'Sign in'}
      </button>

      <p className="auth-alt-link">
        New to GIT it!?{' '}
        <Link to="/register">
          Create an account
        </Link>
      </p>
    </form>
  )
}
