import blueCast from '@/assets/sprites/character/blue/cast.png'
import blueFloat from '@/assets/sprites/character/blue/float.png'
import blueFly from '@/assets/sprites/character/blue/fly.png'
import blueHurt from '@/assets/sprites/character/blue/hurt.png'
import blueIdle from '@/assets/sprites/character/blue/idle.png'
import blueLand from '@/assets/sprites/character/blue/land.png'
import blueRandom1 from '@/assets/sprites/character/blue/random1.png'
import blueRun from '@/assets/sprites/character/blue/run.png'
import blueTakeOff from '@/assets/sprites/character/blue/take_off.png'
import blueWalk from '@/assets/sprites/character/blue/walk.png'
import type { CharacterDefinition, SpriteAnimation } from '@/shared/sprites/types'

/**
 * Named character definitions. Sheets live in src/assets/sprites/character/.
 * Frames are always 256×256; sheets come in two layouts — the original 5×5
 * (25 frames) and the newer 8×8 (64 frames).
 *
 * To add a move or a whole character, add config here — no component changes.
 */
function sheet(name: string, src: string, grid: 5 | 8, fps: number, loop: boolean): SpriteAnimation {
  return {
    name,
    src,
    frameWidth: 256,
    frameHeight: 256,
    columns: grid,
    rows: grid,
    frameCount: grid * grid,
    fps,
    loop,
  }
}

export const BLUE: CharacterDefinition = {
  id: 'blue',
  sprites: {
    idle: sheet('blue.idle', blueIdle, 5, 10, true),
    walk: sheet('blue.walk', blueWalk, 5, 12, true),
    run: sheet('blue.run', blueRun, 5, 14, true),
    fly: sheet('blue.fly', blueFly, 8, 24, true),
    float: sheet('blue.float', blueFloat, 5, 8, true),
    take_off: sheet('blue.take_off', blueTakeOff, 8, 40, false),
    land: sheet('blue.land', blueLand, 8, 40, false),
    // dive: none yet — the controller tilts the fly sheet nose-down instead.
  },
  randoms: [sheet('blue.random1', blueRandom1, 8, 20, false)],
  metrics: {
    scale: 0.65,
    walkSpeed: 140,
    runSpeed: 280,
    flySpeed: 380,
    // Measured from the idle sheet: lowest opaque pixel sits at y=204 of the
    // 256px frame in every cell, so the foot line is 51 source px up.
    footOffset: 51,
    // take_off frames 0–44 are the upright crouch/wing-unfurl (rise straight
    // up); from cell 45 the sheet is in horizontal flight poses.
    takeOffAirborneFrame: 45,
    takeOffLiftSpeed: 55,
    // land frames 0–31 are flight/braking flare; from cell 32 the pose is an
    // upright wings-flared drop, touching down around cell 40.
    landFallFrame: 32,
  },
}

/**
 * Battle-only sheets for Blue, kept out of `CharacterDefinition` so the tower
 * controller's MoveName contract is untouched. Blue rests on the shared `idle`
 * sheet (BLUE.sprites.idle) and plays one `cast` action for every spell — the
 * spell's projectile/effect is drawn by the battle effect layer, not the sprite.
 *
 * `miss` has no dedicated sheet yet, so it deliberately reuses the idle frames
 * (played once) as a placeholder beat when a spell fizzles; swap in a real
 * sheet later without touching the director. `hurt` is retained for legacy
 * callers but the tower-defense loop has monsters strike the crystal, not Blue.
 */
export const BLUE_BATTLE: Record<'cast' | 'hurt' | 'miss', SpriteAnimation> = {
  cast: sheet('blue.cast', blueCast, 8, 32, false),
  hurt: sheet('blue.hurt', blueHurt, 5, 20, false),
  miss: sheet('blue.miss', blueIdle, 5, 10, false),
}
