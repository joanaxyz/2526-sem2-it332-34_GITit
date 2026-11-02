import { useSearchParams } from 'react-router-dom'
import type { LearnedSkill } from '@/features/skills/types'
import { knowledgeForMascot } from '@/features/skills/utils/mascotKnowledge'
import { INTRODUCTORY_TIPS } from '@/shared/mascot/mascotKnowledge'
import { WorldMascot } from '@/shared/mascot/WorldMascot'
import { homeViewFromParam } from './homeViews'

/** Shares Profile's earned spellbook while remaining present on every Home view. */
export function HomeKnowledgeMascot({ skills }: { skills: readonly LearnedSkill[] | undefined }) {
  const [params] = useSearchParams()
  const view = homeViewFromParam(params.get('view'))
  const earned = knowledgeForMascot(skills ?? [])
  // A small spellbook alone would leave Home cycling between one or two tips.
  const knowledge = [...earned, ...INTRODUCTORY_TIPS.filter((tip) => !earned.some((entry) => entry.id === tip.id))]
  return <WorldMascot surface="home" knowledge={knowledge} contextKey={`home:${view}`} />
}
