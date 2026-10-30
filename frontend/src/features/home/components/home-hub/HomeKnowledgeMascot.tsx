import { useSearchParams } from 'react-router-dom'
import type { LearnedSkill } from '@/features/skills/types'
import { knowledgeForMascot } from '@/features/skills/utils/mascotKnowledge'
import { WorldMascot } from '@/shared/mascot/WorldMascot'
import { homeViewFromParam } from './homeViews'

/** Shares Profile's earned spellbook while remaining present on every Home view. */
export function HomeKnowledgeMascot({ skills }: { skills: readonly LearnedSkill[] | undefined }) {
  const [params] = useSearchParams()
  const view = homeViewFromParam(params.get('view'))
  return <WorldMascot surface="home" knowledge={knowledgeForMascot(skills ?? [])} contextKey={`home:${view}`} />
}
