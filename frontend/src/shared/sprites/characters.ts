import blueFloat from '@/assets/sprites/character/blue/float.png'
import blueFly from '@/assets/sprites/character/blue/fly.png'
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
    // land frames 0–31 are flight/braking flare; from cell 32 the pose is an
    // upright wings-flared drop, touching down around cell 40.
    landFallFrame: 32,
  },
}
