import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Eye, EyeOff, GitMerge, Loader2, LogIn, ShieldCheck, Zap } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { authApi } from '@/features/auth/api/authApi'
import { presentAuthError } from '@/features/auth/api/authError'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { Button } from '@/shared/components/Button'
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

const inputClasses =
  'h-10 rounded-md border border-input bg-secondary px-3 text-sm outline-none transition-all duration-200 focus:border-primary/40 focus:ring-2 focus:ring-ring/25'

const highlights = [
  { Icon: ShieldCheck, text: 'Live DAG visualizations per command' },
  { Icon: Zap, text: 'Consequence-safe practice sessions' },
  { Icon: GitMerge, text: 'Progress tracking across all towers' },
]

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
      className="flex h-full flex-col gap-3"
      onSubmit={form.handleSubmit((values) => {
        setLastSubmittedValues(values)
        mutation.mutate(values)
      })}
    >
      <div>
        <h2 className="text-2xl font-extrabold tracking-tight">Sign in</h2>
        <p className="mt-1 text-sm leading-5 text-muted-foreground">Continue your Git practice journey.</p>
      </div>

      <label className="flex flex-col gap-1.5 text-sm font-semibold">
        Username or email
        <input
          className={cn(inputClasses, form.formState.errors.identifier && 'border-destructive focus:border-destructive/80 focus:ring-destructive/30')}
          autoComplete="username"
          disabled={isLocked}
          {...form.register('identifier')}
        />
        {form.formState.errors.identifier ? (
          <span className="text-xs font-normal text-destructive">{form.formState.errors.identifier.message}</span>
        ) : null}
      </label>

      <label className="flex flex-col gap-1.5 text-sm font-semibold">
        Password
        <div className="relative">
          <input
            className={cn(`${inputClasses} w-full pr-10`, form.formState.errors.password && 'border-destructive focus:border-destructive/80 focus:ring-destructive/30')}
            type={showPassword ? 'text' : 'password'}
            disabled={isLocked}
            {...form.register('password')}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 grid w-10 place-items-center text-muted-foreground transition-colors hover:text-foreground"
            onClick={() => setShowPassword((value) => !value)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            disabled={isLocked}
          >
            {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          </button>
        </div>
        {form.formState.errors.password ? (
          <span className="text-xs font-normal text-destructive">{form.formState.errors.password.message}</span>
        ) : null}
      </label>

      {isLocked ? (
        <p className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
          Too many failed attempts. Try again in {lockoutRemaining}s.
        </p>
      ) : null}

      {errorPresentation ? (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
          <p>{errorPresentation.message}</p>
          {errorPresentation.retryable && lastSubmittedValues ? (
            <button
              type="button"
              className="mt-2 text-xs font-semibold underline underline-offset-2"
              onClick={() => mutation.mutate(lastSubmittedValues)}
            >
              Retry
            </button>
          ) : null}
        </div>
      ) : null}

      <Button type="submit" disabled={mutation.isPending || isLocked}>
        {mutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <LogIn data-icon="inline-start" />}
        {mutation.isPending ? 'Signing in…' : 'Sign in'}
      </Button>

      <div className="mt-auto flex flex-col gap-3">
        <div
          className="rounded-md p-3"
          style={{
            background: 'rgba(0,245,212,0.04)',
            border: '1px solid rgba(0,245,212,0.12)',
          }}
        >
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.1em] text-primary/50">
            Platform features
          </p>
          <ul className="space-y-1.5">
            {highlights.map(({ Icon, text }) => (
              <li key={text} className="flex items-center gap-2 text-xs text-muted-foreground">
                <Icon className="size-3 shrink-0 text-primary/60" />
                {text}
              </li>
            ))}
          </ul>
        </div>

        <p className="text-sm text-muted-foreground">
          New to GIT it!?{' '}
          <Link className="link-underline-anim font-semibold text-primary" to="/register">
            Create an account
          </Link>
        </p>
      </div>
    </form>
  )
}
