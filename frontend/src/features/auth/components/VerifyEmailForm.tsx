import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Loader2, MailCheck, ShieldCheck } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { RESEND_COOLDOWN_SECONDS, VERIFICATION_CODE_LENGTH } from '@/features/auth/api/emailVerification'
import { presentAuthError } from '@/features/auth/api/authError'
import { authApi } from '@/shared/auth/authApi'
import { useAuthStore } from '@/shared/auth/useAuth'
import { storyPath } from '@/shared/navigation/routes'
import { cn } from '@/shared/utils/cn'

export function VerifyEmailForm() {
  const [params] = useSearchParams()
  const email = params.get('email')?.trim() ?? ''
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setSession = useAuthStore((state) => state.setSession)
  const [code, setCode] = useState('')
  const [cooldown, setCooldown] = useState(RESEND_COOLDOWN_SECONDS)
  const confirm = useMutation({
    mutationFn: (value: string) => authApi.confirmEmailVerification({ email, code: value }),
    onSuccess: (session) => {
      queryClient.clear()
      setSession(session.access, session.user)
      navigate(storyPath(), { replace: true })
    },
  })
  const resend = useMutation({
    mutationFn: () => authApi.resendEmailVerification({ email }),
    onSuccess: () => setCooldown(RESEND_COOLDOWN_SECONDS),
  })
  const confirmError = useMemo(
    () => (confirm.error ? presentAuthError(confirm.error) : null),
    [confirm.error],
  )
  const isCoolingDown = cooldown > 0

  useEffect(() => {
    if (!isCoolingDown) return
    const intervalId = window.setInterval(() => {
      setCooldown((value) => Math.max(0, value - 1))
    }, 1000)
    return () => window.clearInterval(intervalId)
  }, [isCoolingDown])

  function updateCode(raw: string) {
    const digits = raw.replace(/\D/g, '').slice(0, VERIFICATION_CODE_LENGTH)
    setCode(digits)
    // A pasted or fully typed code submits itself; the button stays for retries.
    if (digits.length === VERIFICATION_CODE_LENGTH && digits !== code && !confirm.isPending) {
      confirm.mutate(digits)
    }
  }

  if (!email) {
    return (
      <div className="auth-form auth-forgot">
        <span className="auth-reset-icon"><MailCheck aria-hidden="true" /></span>
        <div className="auth-form-heading">
          <h2>Confirm your email</h2>
          <p>Sign in with your username and password, and we'll take you back to the code screen.</p>
        </div>
        <Link to="/login" className="auth-back-link"><ArrowLeft aria-hidden="true" />Back to sign in</Link>
      </div>
    )
  }

  return (
    <form
      className="auth-form"
      onSubmit={(event) => {
        event.preventDefault()
        if (code.length === VERIFICATION_CODE_LENGTH) confirm.mutate(code)
      }}
    >
      <span className="auth-reset-icon"><MailCheck aria-hidden="true" /></span>
      <div className="auth-form-heading">
        <h2>Check your inbox</h2>
        <p>
          We sent a 6-digit code to <strong>{email}</strong>. Enter it to open the Spire.
        </p>
      </div>
      <label className="auth-field">
        <span>Verification code</span>
        <input
          className={cn('auth-input auth-code-input', confirmError && 'is-error')}
          value={code}
          onChange={(event) => updateCode(event.target.value)}
          inputMode="numeric"
          autoComplete="one-time-code"
          placeholder="000000"
          maxLength={VERIFICATION_CODE_LENGTH + 1}
          autoFocus
        />
      </label>
      {confirmError ? <p className="auth-error-box">{confirmError.message}</p> : null}
      <button
        type="submit"
        className="auth-submit ui-drawn-plate"
        disabled={confirm.isPending || code.length !== VERIFICATION_CODE_LENGTH}
      >
        {confirm.isPending ? <Loader2 className="size-4 animate-spin" /> : <ShieldCheck aria-hidden="true" />}
        {confirm.isPending ? 'Verifying' : 'Verify email'}
      </button>
      <p className="auth-muted-copy">Can't find it? Check your spam or promotions folder.</p>
      <p className="auth-alt-link">
        Didn't get a code?{' '}
        <button
          type="button"
          className="auth-text-button"
          disabled={isCoolingDown || resend.isPending}
          onClick={() => resend.mutate()}
        >
          {isCoolingDown ? `Send a new code in ${cooldown}s` : 'Send a new code'}
        </button>
      </p>
      {resend.isSuccess ? <p className="auth-muted-copy" role="status">{resend.data.detail}</p> : null}
      {resend.isError ? <p className="auth-error-box">{presentAuthError(resend.error).message}</p> : null}
      <Link to="/login" className="auth-back-link"><ArrowLeft aria-hidden="true" />Back to sign in</Link>
    </form>
  )
}
