import { HomeCombatShowcase } from '@/features/home/components/home-hub/HomeCombatShowcase'
import { HomeCompanionAnnouncement } from '@/features/home/components/home-hub/HomeCompanionStatus'
import { HomeProfilePanel } from '@/features/home/components/home-hub/HomeProfilePanel'
import type { CompanionPresentation } from '@/features/home/components/home-hub/companionPresentation'
import type { HomeSummary } from '@/features/home/types'
import { useLearnedSkills } from '@/features/skills/hooks/useLearnedSkills'
import type { StatsSummary } from '@/features/stats/types'

type HomeProfileWorkspaceProps = {
  home: HomeSummary
  stats: StatsSummary
  playerName: string
  gitcoins: number | null
  hidden: boolean
  companion: CompanionPresentation
}

export function HomeProfileWorkspace({
  home,
  stats,
  playerName,
  gitcoins,
  hidden,
  companion,
}: HomeProfileWorkspaceProps) {
  const { data: skills, isLoading: skillsLoading } = useLearnedSkills()

  return (
    <section className="home-ref-grid" aria-label="Player profile overview" hidden={hidden}>
      {companion.status !== 'ready' ? (
        <HomeCompanionAnnouncement companion={companion} />
      ) : null}
      <HomeProfilePanel
        home={home}
        stats={stats}
        playerName={playerName}
        gitcoins={gitcoins}
        companion={companion}
      />
      <HomeCombatShowcase
        key={companion.status === 'ready' ? companion.slug : companion.status}
        companion={companion}
        skills={skills}
        skillsLoading={skillsLoading}
      />
    </section>
  )
}
