import type { BattleBackdropHandle } from '@/shared/battle/components/BattleBackdrop'
import type { MonsterActorHandle } from '@/shared/battle/components/MonsterActor'
import type { PlayerActorHandle } from '@/shared/battle/components/PlayerActor'
import type { BattleBlock, BattleMonster } from '@/shared/battle/types'

export type BattleTransitionCueConfig = {
  wave: number
  total: number
}

export type BattleTransitionCue = BattleTransitionCueConfig & {
  id: number
}

export type EncounterOptions = {
  /** Blue runs while the parallax scrolls before the new encounter stages in. */
  travel?: boolean
  /** Every entrance runs in on foot ('run'); 'none' skips the choreography. */
  entry?: 'run' | 'none'
  /** Optional cue shown by the consumer when the queued transition actually begins. */
  transitionCue?: BattleTransitionCueConfig | null
  playerHp?: number | null
  playerMaxHp?: number | null
}

export type BattleDirector = {
  /** Current roster - render one MonsterActor per entry. */
  roster: BattleMonster[]
  playerHp: number | null
  playerMaxHp: number | null
  defeated: boolean
  /** True while the battle choreography queue still has visible work to finish. */
  animating: boolean
  /** Emits when a queued wave/encounter transition animation starts. */
  transitionCue: BattleTransitionCue | null
  /** Monsters mounting for an entrance should stay hidden until choreography reveals them. */
  stagedMonsterIds: ReadonlySet<number>
  /** Monster currently executing its counterattack, if any. */
  activeMonsterId: number | null
  /** Increments on every roster replacement (new encounter/wave). Fold it into
   *  each MonsterActor's React key so waves never reuse an actor instance. */
  rosterEpoch: number
  /** Callback refs the BattleStage wires up (functions, not ref objects, so
   *  they are safe to pass during render). */
  bindPlayer: (handle: PlayerActorHandle | null) => void
  bindBackdrop: (handle: BattleBackdropHandle | null) => void
  /** The pannable actor-camera layer (real camera follow while Blue runs). */
  bindCamera: (node: HTMLDivElement | null) => void
  bindEffectLayer: (node: HTMLDivElement | null) => void
  bindBackEffectLayer: (node: HTMLDivElement | null) => void
  bindMonster: (id: number, handle: MonsterActorHandle | null) => void
  /** Latest roster snapshot (for deriveBattleEvents inputs). */
  currentMonsters: () => BattleMonster[]
  /** Command lifecycle. */
  onAttackStart: () => void
  onResolve: (block: BattleBlock) => void
  onError: () => void
  /** Select which story world supplies monster skins/effects for this run. */
  setStoryWorldSlug: (slug: string | null | undefined) => void
  /** Swap to a new encounter (level advance / initial mount / retry). */
  setEncounter: (roster: BattleMonster[], opts?: EncounterOptions) => void
}
