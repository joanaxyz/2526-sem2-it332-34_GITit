import { ArrowLeft, KeyRound } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/shared/components/Button'

/**
 * There is no self-serve reset endpoint yet, so this screen is honest about
 * that and routes the user forward instead of dead-ending at the password
 * field on the login form.
 */
export function ForgotPasswordPage() {
  return (
    <div className="flex flex-col gap-4">
      <span className="grid size-11 place-items-center rounded-md border border-primary/25 bg-primary/10 text-primary">
        <KeyRound className="size-5" />
      </span>

      <div>
        <h2 className="text-2xl font-extrabold tracking-tight">Reset your password</h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          Self-serve password reset isn&apos;t available yet. If you&apos;re locked out, the quickest way
          back onto the tower is a fresh account — your climb is tracked per account.
        </p>
      </div>

      <Button asChild>
        <Link to="/register">Create a new account</Link>
      </Button>

      <Link
        to="/login"
        className="link-underline-anim inline-flex items-center gap-1.5 self-start text-sm font-semibold text-primary"
      >
        <ArrowLeft className="size-4" />
        Back to sign in
      </Link>
    </div>
  )
}
