export type PasswordStrengthLevel = 'very-weak' | 'weak' | 'so-so' | 'good' | 'strong'

export type PasswordRequirement = {
  id: string
  label: string
  test: (password: string) => boolean
}

export const PASSWORD_REQUIREMENTS: PasswordRequirement[] = [
  { id: 'length', label: 'At least 8 characters', test: (password) => password.length >= 8 },
  { id: 'uppercase', label: 'An uppercase letter', test: (password) => /[A-Z]/.test(password) },
  { id: 'lowercase', label: 'A lowercase letter', test: (password) => /[a-z]/.test(password) },
  { id: 'number', label: 'A number', test: (password) => /\d/.test(password) },
  { id: 'special', label: 'A special character', test: (password) => /[^A-Za-z0-9]/.test(password) },
]

const STRENGTH_META: Record<
  PasswordStrengthLevel,
  { label: string; filledSegments: number; labelClass: string; segmentClass: string }
> = {
  'very-weak': {
    label: 'Very weak',
    filledSegments: 0,
    labelClass: 'text-muted-foreground',
    segmentClass: 'bg-muted-foreground/35',
  },
  weak: {
    label: 'Weak',
    filledSegments: 1,
    labelClass: 'text-destructive',
    segmentClass: 'bg-destructive',
  },
  'so-so': {
    label: 'So-so',
    filledSegments: 2,
    labelClass: 'text-orange-500',
    segmentClass: 'bg-orange-500',
  },
  good: {
    label: 'Good',
    filledSegments: 3,
    labelClass: 'text-emerald-400',
    segmentClass: 'bg-emerald-400',
  },
  strong: {
    label: 'Strong',
    filledSegments: 4,
    labelClass: 'text-emerald-600',
    segmentClass: 'bg-emerald-600',
  },
}

export function getMissingPasswordRequirements(password: string): string[] {
  return PASSWORD_REQUIREMENTS.filter((requirement) => !requirement.test(password)).map(
    (requirement) => requirement.label,
  )
}

export function getPasswordStrength(password: string) {
  if (!password) {
    return { level: 'very-weak' as const, ...STRENGTH_META['very-weak'] }
  }

  const metCount = PASSWORD_REQUIREMENTS.filter((requirement) => requirement.test(password)).length
  const length = password.length

  let level: PasswordStrengthLevel = 'very-weak'
  if (length >= 12 && metCount >= 5) {
    level = 'strong'
  } else if (length >= 10 && metCount >= 3) {
    level = 'good'
  } else if (length >= 8 && metCount >= 2) {
    level = 'so-so'
  } else if (length >= 6) {
    level = 'weak'
  } else if (length > 0) {
    level = 'very-weak'
  }

  return { level, ...STRENGTH_META[level] }
}
