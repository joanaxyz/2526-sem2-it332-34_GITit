export type AssetKind =
  | 'monster'
  | 'character'
  | 'projectile'
  | 'tower_piece'
  | 'tower_artifact'
  | 'battle_artifact'

export type AssetSpriteDescriptor = {
  url: string
  frame_count: number
  columns: number
  rows: number
  frame_width: number
  frame_height: number
  natural_width?: number
  natural_height?: number
  content_type?: string
  is_raster?: boolean
  fps: number
  loops?: boolean
}

/** Where an owned-map descriptor came from, relative to the requesting user. */
export type AssetSource = 'official' | 'owned' | 'purchased'

export type BaseAssetDescriptor<K extends AssetKind = AssetKind> = {
  id: number
  slug: string
  label: string
  kind: K
  scale?: number
  owner_id?: number | null
  visibility?: 'private' | 'public' | 'store'
  price?: number
  tags?: string[]
  /** Present only on owned-map responses (getOwnedDescriptors). */
  source?: AssetSource
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
    walk_speed?: number
    run_speed?: number
    fly_speed?: number
    foot_offset?: number
    hp_bar_fraction?: number
    teleport_distance?: number
    take_off_airborne_frame?: number
    take_off_lift_speed?: number
    land_fall_frame?: number
  }
  random_actions?: string[]
}

export type CharacterAssetDescriptor = BaseAssetDescriptor<'character'> & {
  metrics?: {
    walk_speed?: number
    run_speed?: number
    fly_speed?: number
    foot_offset?: number
    hp_bar_fraction?: number
    teleport_distance?: number
    take_off_airborne_frame?: number
    take_off_lift_speed?: number
    land_fall_frame?: number
  }
  random_actions?: string[]
}

export type TowerPieceType = 'crown' | 'base' | 'section' | 'landing'

export type TowerArtifactRole = 'normal' | 'adventure' | 'challenge' | 'tome'

export type TowerPieceAssetDetail = {
  piece_type: TowerPieceType
  view_box: string
  anchors: Record<string, unknown>
  bounds: Record<string, unknown>
  interaction_zones: Record<string, unknown>
  state_variants: Record<string, unknown>
  svg_sanitized: boolean
  natural_width?: number
  natural_height?: number
  content_type?: string
  is_raster?: boolean
  /** Inline sanitized SVG markup for structural pieces. Asset states come from
   *  uploaded sprite actions or authored SVG data, not frontend presets. */
  svg?: string
}

export type TowerPieceAssetDescriptor = BaseAssetDescriptor<'tower_piece'> & {
  piece_type?: TowerPieceType
  tower_piece?: TowerPieceAssetDetail
}

export type TowerArtifactAssetDescriptor = BaseAssetDescriptor<'tower_artifact'>
export type ProjectileAssetDescriptor = BaseAssetDescriptor<'projectile'>

/** A battle-stage set piece (e.g. the crystal Blue defends). `config.foot_offset`
 *  is the source-pixel padding below its base, used to stand it on the ledge. */
export type BattleArtifactAssetDescriptor = BaseAssetDescriptor<'battle_artifact'>

export type AssetDescriptor =
  | MonsterAssetDescriptor
  | CharacterAssetDescriptor
  | TowerPieceAssetDescriptor
  | TowerArtifactAssetDescriptor
  | ProjectileAssetDescriptor
  | BattleArtifactAssetDescriptor

export type TowerContentBinding = {
  kind: 'adventure' | 'challenge' | 'tome'
  id: number | string
  levelId?: number | string
  difficulty?: string
}

export type TowerLayoutPieceDescriptor = {
  instanceId: string
  assetSlug: string
  pieceType: TowerPieceType
  storeyIndex?: number
  sortOrder?: number
  parentInstanceId?: string | null
  transform?: Record<string, unknown>
  config?: Record<string, unknown>
}

export type TowerLayoutDescriptor = {
  storeyId: number | null
  pieces: TowerLayoutPieceDescriptor[]
}

export type AssetDescriptorResponse = {
  kind: AssetKind
  results: Record<string, AssetDescriptor>
}
