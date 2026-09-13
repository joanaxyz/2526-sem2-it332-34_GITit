import { useEffect, useRef } from 'react'
import type { FieldValues, Path, UseFormReturn } from 'react-hook-form'

import { apiFieldErrors, type ApiFieldErrors } from './apiError'

/**
 * Pins backend field errors (Django's password rules, a taken username) onto the
 * inputs that caused them.
 *
 * Returns the fields it attached so a form can keep its summary box from
 * repeating what an input already says.
 */
export function useServerFieldErrors<TValues extends FieldValues>(
  form: UseFormReturn<TValues>,
  error: unknown,
  fields: Path<TValues>[],
  /** Field errors to use instead of the thrown error's own, when a caller maps them. */
  overrides?: ApiFieldErrors,
): Path<TValues>[] {
  const { setError } = form
  const submitCount = form.formState.submitCount
  const fieldErrors = overrides ?? apiFieldErrors(error)
  const attached = fields.filter((field) => (fieldErrors[field]?.length ?? 0) > 0)
  const pending = useRef<[Path<TValues>, string[]][]>([])
  pending.current = attached.map((field) => [field, fieldErrors[field]])

  // Keyed by value and by submit, never by the error's identity: resubmitting the
  // same bad password produces the same message, and handleSubmit clears the
  // form's errors on its way out, so the message has to be applied again.
  const signature = JSON.stringify(pending.current)

  useEffect(() => {
    for (const [field, messages] of pending.current) {
      setError(field, { type: 'server', message: messages.join(' ') })
    }
  }, [signature, submitCount, setError])

  return attached
}
