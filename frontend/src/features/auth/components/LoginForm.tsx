import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { LogIn } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { authApi } from '@/features/auth/api/authApi'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { Button } from '@/shared/components/Button'

const schema = z.object({
  identifier: z
    .string()
    .trim()
    .min(1, 'Student ID or email is required.')
    .refine(
      (value) =>
        value.includes('@')
          ? z.string().email().safeParse(value).success && value.toLowerCase().endsWith('@cit.edu')
          : /^\d{2}-\d{4}-\d{3}$/.test(value),
      'Use your student ID or @cit.edu email.',
    ),
  password: z.string().min(1, 'Password is required.'),
})

type FormValues = z.infer<typeof schema>

export function LoginForm() {
  const navigate = useNavigate()
  const setSession = useAuthStore((state) => state.setSession)
  const form = useForm<FormValues>({ resolver: zodResolver(schema) })
  const mutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      setSession(data.access, data.user)
      navigate('/dashboard')
    },
  })

  return (
    <form className="flex flex-col gap-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <div>
        <h2 className="text-3xl font-extrabold tracking-tight">Sign in</h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">Continue your Git practice dashboard.</p>
      </div>
      <label className="flex flex-col gap-2 text-sm font-semibold">
        Student ID or email
        <input className="h-11 rounded-md border border-input bg-secondary px-3 outline-none focus:ring-2 focus:ring-ring" autoComplete="username" {...form.register('identifier')} />
        {form.formState.errors.identifier ? <span className="text-xs text-destructive">{form.formState.errors.identifier.message}</span> : null}
      </label>
      <label className="flex flex-col gap-2 text-sm font-semibold">
        Password
        <input className="h-11 rounded-md border border-input bg-secondary px-3 outline-none focus:ring-2 focus:ring-ring" type="password" {...form.register('password')} />
        {form.formState.errors.password ? <span className="text-xs text-destructive">{form.formState.errors.password.message}</span> : null}
      </label>
      {mutation.error ? <p className="text-sm text-destructive">{mutation.error.message}</p> : null}
      <Button type="submit" disabled={mutation.isPending}>
        <LogIn data-icon="inline-start" />
        {mutation.isPending ? 'Signing in' : 'Sign in'}
      </Button>
      <p className="text-sm text-muted-foreground">
        New to GIT it!? <Link className="font-semibold text-primary" to="/register">Create an account</Link>
      </p>
    </form>
  )
}
