/**
 * Shared gameplay-workspace sizing.
 *
 * Adventure and challenge intentionally use the same open battle-stage row so
 * switching modes does not change the visual weight of combat. The terminal is
 * allowed to remain compact; repository feedback and context keep the rest of
 * the workspace.
 */
export const WORKSPACE_BATTLE_STAGE_ROW = 'clamp(16rem, 38vh, 24rem)'
export const WORKSPACE_BATTLE_COLLAPSED_ROW = '2.25rem'
