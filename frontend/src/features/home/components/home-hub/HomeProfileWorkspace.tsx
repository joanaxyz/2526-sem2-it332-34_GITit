import { HomeCombatShowcase } from '@/features/home/components/home-hub/HomeCombatShowcase'
import { HomeCompanionRoster } from '@/features/home/components/home-hub/HomeCompanionRoster'
import { HomeCompanionAnnouncement } from '@/features/home/components/home-hub/HomeCompanionStatus'
import { HomeProfilePanel } from '@/features/home/components/home-hub/HomeProfilePanel'
import { HomeKnowledgeMascot } from '@/features/home/components/home-hub/HomeKnowledgeMascot'
import type { CompanionPresentation } from '@/features/home/components/home-hub/companionPresentation'
import { useCompanionPreview } from '@/features/home/components/home-hub/useCompanionPreview'
import type { HomeSummary } from '@/features/home/types'
import { useLearnedSkills } from '@/features/skills/hooks/useLearnedSkills'
import type { StatsSummary } from '@/features/stats/types'

type HomeProfileWorkspaceProps = {
  home: HomeSummary
  stats: StatsSummary
  playerName: string
  hidden: boolean
  companion: CompanionPresentation
}

export function HomeProfileWorkspace({
  home,
  stats,
  playerName,
  hidden,
  companion,
}: HomeProfileWorkspaceProps) {
  const { data: skills, isLoading: skillsLoading } = useLearnedSkills()
  const { shownCompanion, previewCompanion } = useCompanionPreview(companion)

  return (
    <>
      <HomeKnowledgeMascot skills={skills} />
      <section className="home-ref-grid" aria-label="Player profile overview" hidden={hidden}>
        {companion.status !== 'ready' ? (
          <HomeCompanionAnnouncement companion={companion} />
        ) : null}
        <HomeProfilePanel
          home={home}
          stats={stats}
          playerName={playerName}
          companion={shownCompanion}
        />
        <HomeCompanionRoster onSelect={previewCompanion} />
        <HomeCombatShowcase
          key={shownCompanion.status === 'ready' ? shownCompanion.slug : shownCompanion.status}
          companion={shownCompanion}
          skills={skills}
          skillsLoading={skillsLoading}
        />
      </section>
    </>
  )
}
