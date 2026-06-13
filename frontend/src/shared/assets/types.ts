export type AssetKind = 'monster' | 'character' | 'projectile' | 'tower_piece' | 'tower_artifact'

export type AssetSpriteDescriptor = {
  url: string
  frame_count: number
  columns: number
  rows: number
  frame_width: number
  frame_height: number
  fps: number
  loops?: boolean
}

export type BaseAssetDescriptor<K extends AssetKind = AssetKind> = {
  slug: string
  label: string
  kind: K
  scale?: number
  config?: Record<string, unknown>
  sprites: Record<string, AssetSpriteDescriptor>
}

export type MonsterAssetDescriptor = BaseAssetDescriptor<'monster'> & {
  tier?: 'mob' | 'elite' | 'boss' | (string & {})
  attack?: {
    kind?: 'melee' | 'projectile' | (string & {})
    hit_frame?: number
    lunge_px?: number
    projectile?: string
  }
  metrics?: {
    foot_offset?: number
    hp_bar_fraction?: number
  }
}

export type CharacterAssetDescriptor = BaseAssetDescriptor<'character'> & {
  metrics?: {
    walk_speed?: number
    run_speed?: number
    fly_speed?: number
    foot_offset?: number
    teleport_distance?: number
    take_off_airborne_frame?: number
    take_off_lift_speed?: number
    land_fall_frame?: number
  }
  random_actions?: string[]
}

export type TowerPieceType =
  | 'spire'
  | 'landing'
  | 'door'
  | 'adventure_section'
  | 'challenge_section'
  | 'tome'

export type TowerPieceAssetDetail = {
  piece_type: TowerPieceType
  view_box: string
  anchors: Record<string, unknown>
  bounds: Record<string, unknown>
  interaction_zones: Record<string, unknown>
  state_variants: Record<string, unknown>
  svg_sanitized: boolean
}

export type TowerPieceAssetDescriptor = BaseAssetDescriptor<'tower_piece'> & {
  piece_type?: TowerPieceType
  tower_piece?: TowerPieceAssetDetail
}

export type TowerArtifactAssetDescriptor = BaseAssetDescriptor<'tower_artifact'>
export type ProjectileAssetDescriptor = BaseAssetDescriptor<'projectile'>

export type AssetDescriptor =
  | MonsterAssetDescriptor
  | CharacterAssetDescriptor
  | TowerPieceAssetDescriptor
  | TowerArtifactAssetDescriptor
  | ProjectileAssetDescriptor

export type TowerContentBinding = {
  kind: 'adventure' | 'challenge' | 'tome'
  id: number | string
}

export type TowerLayoutPieceDescriptor = {
  instanceId: string
  assetSlug: string
  pieceType: TowerPieceType
  contentBinding?: TowerContentBinding
}

export type TowerLayoutDescriptor = {
  storeyId: number
  pieces: TowerLayoutPieceDescriptor[]
}

export type AssetDescriptorResponse = {
  kind: AssetKind
  results: Record<string, AssetDescriptor>
}

