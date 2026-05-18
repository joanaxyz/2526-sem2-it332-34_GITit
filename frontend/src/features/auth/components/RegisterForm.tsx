import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { UserPlus } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { authApi } from '@/features/auth/api/authApi'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { Button } from '@/shared/components/Button'

const schema = z
  .object({
    display_name: z.string().min(2, 'Use at least two characters.'),
    email: z.string().email(),
    password: z.string().min(8, 'Use at least eight characters.'),
    password_confirm: z.string().min(8),
  })
  .refine((data) => data.password === data.password_confirm, {
    path: ['password_confirm'],
    message: 'Passwords do not match.',
  })

type FormValues = z.infer<typeof schema>

export function RegisterForm() {
  const navigate = useNavigate()
  const setSession = useAuthStore((state) => state.setSession)
  const form = useForm<FormValues>({ resolver: zodResolver(schema) })
  const mutation = useMutation({
    mutationFn: authApi.register,
    onSuccess: (data) => {
      setSession(data.access, data.user)
      navigate('/dashboard')
    },
  })

  return (
    <form className="flex flex-col gap-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>
      <div>
        <h2 className="text-3xl font-extrabold tracking-tight">Create account</h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">Register as a student and complete Unit 1 before scenario practice.</p>
      </div>
      <label className="flex flex-col gap-2 text-sm font-semibold">
        Display name
        <input className="h-11 rounded-md border border-input bg-secondary px-3 outline-none focus:ring-2 focus:ring-ring" {...form.register('display_name')} />
      </label>
      <label className="flex flex-col gap-2 text-sm font-semibold">
        Email
        <input className="h-11 rounded-md border border-input bg-secondary px-3 outline-none focus:ring-2 focus:ring-ring" {...form.register('email')} />
      </label>
      <label className="flex flex-col gap-2 text-sm font-semibold">
        Password
        <input className="h-11 rounded-md border border-input bg-secondary px-3 outline-none focus:ring-2 focus:ring-ring" type="password" {...form.register('password')} />
      </label>
      <label className="flex flex-col gap-2 text-sm font-semibold">
        Confirm password
        <input className="h-11 rounded-md border border-input bg-secondary px-3 outline-none focus:ring-2 focus:ring-ring" type="password" {...form.register('password_confirm')} />
      </label>
      {Object.values(form.formState.errors)[0]?.message ? <p className="text-sm text-destructive">{String(Object.values(form.formState.errors)[0]?.message)}</p> : null}
      {mutation.error ? <p className="text-sm text-destructive">{mutation.error.message}</p> : null}
      <Button type="submit" disabled={mutation.isPending}>
        <UserPlus data-icon="inline-start" />
        {mutation.isPending ? 'Creating account' : 'Create account'}
      </Button>
      <p className="text-sm text-muted-foreground">
        Already registered? <Link className="font-semibold text-primary" to="/login">Sign in</Link>
      </p>
    </form>
  )
}
