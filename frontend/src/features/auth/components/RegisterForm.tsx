import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { Eye, EyeOff, Loader2, UserPlus } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { authApi } from '@/features/auth/api/authApi'
import { presentAuthError } from '@/features/auth/api/authError'
import { PasswordStrengthIndicator } from '@/features/auth/components/PasswordStrengthIndicator'
import { Button } from '@/shared/components/Button'
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
    password_confirm: z.string().min(8),
  })
  .refine((data) => data.password === data.password_confirm, {
    path: ['password_confirm'],
    message: 'Passwords do not match.',
  })

type FormValues = z.infer<typeof schema>

const inputClasses =
  'h-10 rounded-md border border-input bg-secondary px-3 text-sm outline-none transition-all duration-200 focus:border-primary/40 focus:ring-2 focus:ring-ring/25'

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
  const passwordValue = form.watch('password') ?? ''
  const mutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      navigate('/login')
    },
  })
  const errorPresentation = useMemo(
    () => (mutation.error ? presentAuthError(mutation.error) : null),
    [mutation.error],
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
      className="flex flex-col gap-2.5"
      onSubmit={form.handleSubmit((values) => {
        setLastSubmittedValues(values)
        submitRegistration(values)
      })}
    >
      <div>
        <h2 className="text-2xl font-extrabold tracking-tight">Create account</h2>
      </div>
      <label className="flex flex-col gap-1.5 text-sm font-semibold">
        Username
        <input className={cn(inputClasses, form.formState.errors.username && 'border-destructive focus:border-destructive/80 focus:ring-destructive/30')} autoComplete="username" {...form.register('username')} />
        {form.formState.errors.username ? <span className="text-xs font-normal text-destructive">{form.formState.errors.username.message}</span> : null}
      </label>
      <label className="flex flex-col gap-1.5 text-sm font-semibold">
        Email
        <input className={cn(inputClasses, form.formState.errors.email && 'border-destructive focus:border-destructive/80 focus:ring-destructive/30')} autoComplete="email" {...form.register('email')} />
        {form.formState.errors.email ? <span className="text-xs font-normal text-destructive">{form.formState.errors.email.message}</span> : null}
      </label>
      <label className="flex flex-col gap-1.5 text-sm font-semibold">
        Password
        <div className="relative">
          <input
            className={cn(
              `${inputClasses} w-full pr-10`,
              form.formState.errors.password && 'border-destructive focus:border-destructive/80 focus:ring-destructive/30',
            )}
            type={showPassword ? 'text' : 'password'}
            {...form.register('password')}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 grid w-10 place-items-center text-muted-foreground"
            onClick={() => setShowPassword((value) => !value)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          </button>
        </div>
        {form.formState.errors.password ? <span className="text-xs font-normal text-destructive">{form.formState.errors.password.message}</span> : null}
        <PasswordStrengthIndicator password={passwordValue} />
      </label>
      <label className="flex flex-col gap-1.5 text-sm font-semibold">
        Confirm password
        <div className="relative">
          <input
            className={cn(
              `${inputClasses} w-full pr-10`,
              form.formState.errors.password_confirm && 'border-destructive focus:border-destructive/80 focus:ring-destructive/30',
            )}
            type={showPasswordConfirm ? 'text' : 'password'}
            {...form.register('password_confirm')}
          />
          <button
            type="button"
            className="absolute inset-y-0 right-0 grid w-10 place-items-center text-muted-foreground"
            onClick={() => setShowPasswordConfirm((value) => !value)}
            aria-label={showPasswordConfirm ? 'Hide password confirmation' : 'Show password confirmation'}
          >
            {showPasswordConfirm ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          </button>
        </div>
        {form.formState.errors.password_confirm ? <span className="text-xs font-normal text-destructive">{form.formState.errors.password_confirm.message}</span> : null}
      </label>
      {errorPresentation ? (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive">
          <p>{errorPresentation.message}</p>
          {errorPresentation.retryable && lastSubmittedValues ? (
            <button
              type="button"
              className="mt-2 text-xs font-semibold underline underline-offset-2"
              onClick={() => submitRegistration(lastSubmittedValues)}
            >
              Retry
            </button>
          ) : null}
        </div>
      ) : null}
      <Button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <UserPlus data-icon="inline-start" />}
        {mutation.isPending ? 'Creating account' : 'Create account'}
      </Button>
      <p className="text-sm text-muted-foreground">
        Already registered?{' '}
        <Link className="link-underline-anim font-semibold text-primary" to="/login">
          Sign in
        </Link>
      </p>
    </form>
  )
}
