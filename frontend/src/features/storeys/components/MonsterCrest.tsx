export type MonsterVariant = 'easy' | 'medium' | 'hard'

// Stylised neon "beast mask" crest that frames the top of a challenge door.
// Horns + brow get fiercer with difficulty; hard is a horned devil.
const HORNS: Record<MonsterVariant, string> = {
  // small curled nubs
  easy: 'M44 24 C40 16 33 14 30 18 C35 19 39 22 43 28 Z M76 24 C80 16 87 14 90 18 C85 19 81 22 77 28 Z',
  // swept-back ram horns
  medium: 'M45 24 C36 14 24 12 18 18 C28 17 35 21 44 30 Z M75 24 C84 14 96 12 102 18 C92 17 85 21 76 30 Z',
  // tall curved devil horns
  hard: 'M46 23 C36 8 20 2 10 8 C16 12 18 18 20 24 C30 18 38 19 45 30 Z M74 23 C84 8 100 2 110 8 C104 12 102 18 100 24 C90 18 82 19 75 30 Z',
}

export function MonsterCrest({ variant }: { variant: MonsterVariant }) {
  return (
    <svg className="monster-crest" data-variant={variant} viewBox="0 0 120 80" aria-hidden="true">
      <path className="monster-horn" d={HORNS[variant]} />
      {/* head mask with a pointed chin */}
      <path
        className="monster-head"
        d="M32 30 L46 22 L74 22 L88 30 L82 54 L60 74 L38 54 Z"
      />
      {/* brow ridge */}
      <path className="monster-brow" d="M40 36 L54 41 M80 36 L66 41" />
      {/* glowing eyes */}
      <path className="monster-eye" d="M45 40 L55 43 L50 49 L43 46 Z" />
      <path className="monster-eye" d="M75 40 L65 43 L70 49 L77 46 Z" />
      {/* snarl + fangs */}
      <path className="monster-snarl" d="M48 58 L60 62 L72 58" />
      <path className="monster-fang" d="M53 59 L57 59 L55 65 Z" />
      <path className="monster-fang" d="M63 59 L67 59 L65 65 Z" />
      {variant === 'hard' ? <path className="monster-thirdeye" d="M60 30 L64 35 L60 40 L56 35 Z" /> : null}
    </svg>
  )
}
