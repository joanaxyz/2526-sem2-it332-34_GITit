import { Info } from 'lucide-react'
import { useMemo, useState } from 'react'

import {
  getMissingPasswordRequirements,
  getPasswordStrength,
} from '@/features/auth/utils/passwordStrength'
type PasswordStrengthIndicatorProps = {
  password: string
}

export function PasswordStrengthIndicator({ password }: PasswordStrengthIndicatorProps) {
  const [showMissing, setShowMissing] = useState(false)
  const strength = useMemo(() => getPasswordStrength(password), [password])
  const missing = useMemo(() => getMissingPasswordRequirements(password), [password])
  const showIndicator = password.length > 0

  if (!showIndicator) return null

  return (
    <div className="auth-strength">
      <div className="auth-strength-bars">
        {Array.from({ length: 4 }).map((_, index) => (
          <span
            key={index}
            data-filled={index < strength.filledSegments}
            data-strength={strength.label.toLowerCase()}
          />
        ))}
      </div>
      <div className="auth-strength-label">
        <span>{strength.label}</span>
        {missing.length > 0 ? (
          <div className="auth-strength-help">
            <button
              type="button"
              aria-label="Show missing password requirements"
              aria-expanded={showMissing}
              onClick={() => setShowMissing((value) => !value)}
              onBlur={() => setShowMissing(false)}
            >
              <Info aria-hidden="true" />
            </button>
            {showMissing ? (
              <div
                role="tooltip"
                className="auth-strength-tooltip"
              >
                <p>Still needed</p>
                <ul>
                  {missing.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  )
}
