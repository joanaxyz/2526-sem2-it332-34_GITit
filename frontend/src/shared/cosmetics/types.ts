/** A single spritesheet, grid pre-computed for the sprite runtime. */
export type SpriteDef = {
  src: string
  frameWidth: number
  frameHeight: number
  columns: number
  rows: number
  frameCount: number
  fps: number
  loops: boolean
  displayScale?: number
}

/** Flavor-only kit entry shown in the shop preview - not a gameplay system. */
export type CompanionKitEntry = {
  name: string
  description: string
}

/** The player companion, sold on its own in the shop. */
export type CompanionDef = {
  id: string
  label: string
  scale: number
  metrics: Record<string, number>
  randomActions: string[]
  sprites: Record<string, SpriteDef>
  kit?: CompanionKitEntry[]
}
