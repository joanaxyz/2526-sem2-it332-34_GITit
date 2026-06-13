import { motion } from 'motion/react'
import { Sparkles } from 'lucide-react'

import { useLearnedSkills } from '@/features/skills/hooks/useLearnedSkills'
import type { LearnedSkill } from '@/features/skills/types'

const EASE = [0.16, 1, 0.3, 1] as const
const CYAN = '#00F5D4'
const VIOLET = '#A78BFA'

// The command's verb (word after "git "), used as the rune glyph + initial.
function verbOf(baseCommand: string): string {
  const parts = baseCommand.trim().split(/\s+/)
  return parts[parts.length - 1] || baseCommand
}

// HTML-animated stand-in for a future spell sprite: a glowing rune chip that
// rises in, then breathes on a slow per-rune offset loop so the row feels alive.
function SpellRune({ skill, index }: { skill: LearnedSkill; index: number }) {
  const verb = verbOf(skill.base_command)
  return (
    <motion.div
      className="spell-rune group relative flex items-center gap-2.5"
      initial={{ opacity: 0, y: 14, scale: 0.92 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true, amount: 0.4 }}
      transition={{ duration: 0.5, ease: EASE, delay: Math.min(index * 0.05, 0.4) }}
      whileHover={{ y: -3 }}
      title={skill.title}
      style={{
        borderRadius: 9999,
        padding: '0.4rem 0.85rem 0.4rem 0.45rem',
        border: '1px solid rgba(0,245,212,0.28)',
        background: 'linear-gradient(135deg, rgba(12,30,56,0.66), rgba(9,20,40,0.66))',
        backdropFilter: 'blur(6px)',
      }}
    >
      {/* Rune glyph — a diamond crystal bearing the verb's initial, breathing. */}
      <motion.span
        aria-hidden="true"
        className="grid size-7 shrink-0 place-items-center font-mono text-[0.62rem] font-black uppercase"
        animate={{
          boxShadow: [
            `0 0 6px ${CYAN}33, inset 0 0 6px ${CYAN}22`,
            `0 0 14px ${CYAN}66, inset 0 0 9px ${VIOLET}33`,
            `0 0 6px ${CYAN}33, inset 0 0 6px ${CYAN}22`,
          ],
        }}
        transition={{ duration: 3.2, repeat: Infinity, ease: 'easeInOut', delay: (index % 6) * 0.4 }}
        style={{
          color: CYAN,
          background: 'radial-gradient(circle at 50% 35%, rgba(0,245,212,0.18), rgba(9,20,40,0.6))',
          border: '1px solid rgba(0,245,212,0.45)',
          // 45°-rotated square reads as a crystal/rune; counter-rotate the text.
          clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)',
        }}
      >
        <span style={{ transform: 'translateZ(0)' }}>{verb.charAt(0)}</span>
      </motion.span>

      <span className="min-w-0">
        <span className="block truncate font-mono text-[0.78rem] font-bold leading-tight text-foreground">
          {skill.base_command}
        </span>
        <span className="block font-mono text-[0.55rem] uppercase tracking-[0.14em] text-muted-foreground/75">
          Storey {skill.storey_number}
        </span>
      </span>
    </motion.div>
  )
}

function RuneSkeleton({ index }: { index: number }) {
  return (
    <span
      aria-hidden="true"
      className="animate-pulse"
      style={{
        height: '2.4rem',
        width: `${6 + (index % 3)}rem`,
        borderRadius: 9999,
        border: '1px solid rgba(0,245,212,0.12)',
        background: 'rgba(12,30,56,0.5)',
      }}
    />
  )
}

/**
 * The player's spellbook: the commands they've learned, rendered as animated
 * HTML runes (no sprites yet). Open, container-light section — a hairline rule
 * and a row of runes, not a boxed panel.
 */
export function SpellbookPanel() {
  const { data: skills, isLoading } = useLearnedSkills()
  const count = skills?.length ?? 0

  return (
    <section className="relative z-[1] mt-2 px-6 pb-7 max-md:px-2" aria-label="Spellbook">
      <div className="mb-4 flex items-center gap-2 border-t border-[rgba(125,211,252,0.1)] pt-5">
        <Sparkles
          aria-hidden="true"
          className="size-4"
          style={{ color: VIOLET, filter: `drop-shadow(0 0 6px ${VIOLET}66)` }}
        />
        <h3 className="font-mono text-[0.62rem] font-semibold uppercase tracking-[0.26em] text-aurora-blue/80">
          Spellbook
        </h3>
        {!isLoading && count > 0 ? (
          <span className="font-mono text-[0.62rem] uppercase tracking-[0.14em] text-muted-foreground/60">
            {count} command{count === 1 ? '' : 's'} learned
          </span>
        ) : null}
      </div>

      {isLoading ? (
        <div className="flex flex-wrap gap-2.5">
          {Array.from({ length: 5 }, (_, index) => (
            <RuneSkeleton index={index} key={index} />
          ))}
        </div>
      ) : count === 0 ? (
        <p className="font-mono text-xs leading-6 text-muted-foreground/70">
          Clear a Command Adventure to inscribe your first spell.
        </p>
      ) : (
        <div className="flex flex-wrap gap-2.5">
          {skills!.map((skill, index) => (
            <SpellRune index={index} key={skill.id} skill={skill} />
          ))}
        </div>
      )}
    </section>
  )
}
