// Shared field vocabulary for every auth form (login, register, recovery) so
// the inputs can never drift apart across screens. One source of truth for the
// resting + focus + error states.

export const inputClasses =
  'h-10 w-full rounded-md border border-input bg-secondary px-3 text-sm text-foreground outline-none transition-all duration-200 placeholder:text-muted-foreground/60 focus:border-primary/60 focus:ring-2 focus:ring-ring/45'

// Applied on top of `inputClasses` when the field is in error. Stronger focus
// ring than the old /30 so keyboard focus stays visible on the dark plaque.
export const inputErrorClasses =
  'border-destructive focus:border-destructive/80 focus:ring-destructive/40'

// The reveal/hide affordance baked into password fields. Identical hover
// treatment everywhere (Login used to have it, Register didn't).
export const passwordToggleClasses =
  'absolute inset-y-0 right-0 grid w-10 place-items-center text-muted-foreground transition-colors hover:text-foreground'
