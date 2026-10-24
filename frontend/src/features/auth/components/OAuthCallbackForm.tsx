import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Loader2, ShieldAlert } from 'lucide-react'
import { useEffect, useRef } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { presentAuthError } from '@/features/auth/api/authError'
import { authApi } from '@/shared/auth/authApi'
import { useAuthStore } from '@/shared/auth/useAuth'
import { storyPath } from '@/shared/navigation/routes'

/** Messages for the `error` codes the API's OAuth callback redirects with. */
const oauthErrorMessages: Record<string, string> = {
  denied: 'Sign-in was cancelled before it finished.',
  state: 'That sign-in took too long or was started in another tab. Try again.',
  email: "That account didn't give us a verified email. Verify your email with the provider, or sign up with email instead.",
  staff: 'Staff accounts sign in with their username and password.',
  inactive: 'This account has been disabled.',
  unavailable: "That sign-in option isn't set up yet. Use your email and password for now.",
  provider: "We couldn't finish signing in with the provider. Try again in a moment.",
  retry: 'Something changed while we were signing you in. Try again.',
  username: "We couldn't create a username for you. Sign up with email instead.",
}
const fallbackMessage = 'Sign-in did not finish. Try again.'

export function OAuthCallbackForm() {
  const [params] = useSearchParams()
  const ticket = params.get('ticket') ?? ''
  const errorCode = params.get('error')
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setSession = useAuthStore((state) => state.setSession)
  const { mutate, error: exchangeError } = useMutation({
    mutationFn: (value: string) => authApi.exchangeOAuthTicket({ ticket: value }),
    onSuccess: (session) => {
      queryClient.clear()
      setSession(session.access, session.user)
      navigate(session.user.is_staff ? '/admin' : storyPath(), { replace: true })
    },
  })
  // The ticket works once; StrictMode's second effect run must not spend it again.
  const exchanged = useRef(false)

  useEffect(() => {
    if (!ticket || errorCode || exchanged.current) return
    exchanged.current = true
    mutate(ticket)
  }, [ticket, errorCode, mutate])

  const failure = errorCode
    ? oauthErrorMessages[errorCode] ?? fallbackMessage
    : exchangeError
      ? presentAuthError(exchangeError).message
      : !ticket
        ? fallbackMessage
        : null

  if (failure) {
    return (
      <div className="auth-form auth-forgot">
        <span className="auth-reset-icon"><ShieldAlert aria-hidden="true" /></span>
        <div className="auth-form-heading">
          <h2>Sign-in didn't finish</h2>
          <p>{failure}</p>
        </div>
        <Link to="/login" className="auth-back-link"><ArrowLeft aria-hidden="true" />Back to sign in</Link>
      </div>
    )
  }

  return (
    <div className="auth-form auth-forgot" role="status">
      <span className="auth-reset-icon"><Loader2 className="animate-spin" aria-hidden="true" /></span>
      <div className="auth-form-heading">
        <h2>Signing you in</h2>
        <p>Opening the Spire gates…</p>
      </div>
    </div>
  )
}
