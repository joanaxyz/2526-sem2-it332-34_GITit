import type { PiecePreset } from '@/shared/assets/types'

/**
 * The closed set of safe animation presets a piece can use. There is no
 * user-authored code: a preset is a name + a couple of params, and the CSS that
 * implements it (in globals.css, `.piece-anim--*`) moves the SVG's `data-role`
 * parts when an interactive ancestor is hovered/selected.
 */
export const PIECE_PRESETS: PiecePreset[] = [
  'none',
  'swing-open',
  'swing-single',
  'slide-up',
  'fade',
  'pulse',
]

/** preset → the CSS class that drives it. */
export const PIECE_PRESET_CLASS: Record<PiecePreset, string> = {
  none: '',
  'swing-open': 'piece-anim--swing',
  'swing-single': 'piece-anim--swing-single',
  'slide-up': 'piece-anim--slide',
  fade: 'piece-anim--fade',
  pulse: 'piece-anim--pulse',
}

/** Human label for the editor's preset picker. */
export const PIECE_PRESET_LABEL: Record<PiecePreset, string> = {
  none: 'None (static)',
  'swing-open': 'Double doors (swing open)',
  'swing-single': 'Single door (swing open)',
  'slide-up': 'Portcullis (slide up)',
  fade: 'Glow on focus',
  pulse: 'Pulse',
}

/** The `data-role` parts each preset moves — surfaced in the editor so authors
 *  know which tags their SVG needs for the preset to do anything. A two-panel
 *  door tags `leaf-left`/`leaf-right`; a one-panel door tags a single `leaf`. */
export const PIECE_PRESET_PARTS: Record<PiecePreset, string[]> = {
  none: [],
  'swing-open': ['leaf-left', 'leaf-right', 'interior', 'accent'],
  'swing-single': ['leaf', 'interior', 'accent'],
  'slide-up': ['gate', 'interior'],
  fade: [],
  pulse: [],
}

export const DEFAULT_PRESET_DURATION_MS = 520
export const DEFAULT_PRESET_EASING = 'cubic-bezier(0.22, 1, 0.32, 1)'
