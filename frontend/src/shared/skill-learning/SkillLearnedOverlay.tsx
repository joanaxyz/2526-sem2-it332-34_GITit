import { Modal } from '@/shared/components/Modal'
import { CompanionSkillPortrait } from '@/shared/cosmetics/CompanionSkillPortrait'
import type { LearnedSkill } from './useSkillLearnedQueue'
import './skill-learned.css'

export function SkillLearnedOverlay({ skill, companionSlug, onClose }: {
  skill: LearnedSkill | null
  companionSlug: string
  onClose: () => void
}) {
  return (
    <Modal
      open={Boolean(skill)}
      title="You've learned a new skill"
      onClose={onClose}
      className="skill-learned-shell"
      contentClassName="skill-learned-content"
      overlayClassName="skill-learned-backdrop"
      hideHeader
      dismissOnClick
    >
      {skill ? (
        <section className="skill-learned-reveal" key={skill.base_command}>
          <div className="skill-learned-announcement">
            <img className="skill-learned-mascot" src="/mascot/portrait.png" alt="Git it guide" draggable={false} />
            <p>You've learned a new skill</p>
          </div>
          <CompanionSkillPortrait
            className="skill-learned-portrait"
            companionSlug={companionSlug}
            command={skill.base_command}
            title={`${skill.title} skill`}
          />
          <h3 className="skill-learned-title">{skill.title}</h3>
          {skill.title.trim().toLowerCase() !== skill.base_command.trim().toLowerCase() ? (
            <p className="skill-learned-command">{skill.base_command}</p>
          ) : null}
          <p className="skill-learned-hint">Click anywhere to continue<span className="sr-only">, or press Enter, Space, or Escape.</span></p>
        </section>
      ) : null}
    </Modal>
  )
}
