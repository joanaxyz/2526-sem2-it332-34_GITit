import { describe, expect, it } from 'vitest'

import { companionBattleFromDef, companionFromDef } from '@/shared/cosmetics/companionRuntime'
import { getCompanion } from '@/shared/cosmetics/companions/registry'

describe('companionBattleFromDef', () => {
  it('treats Blue death as a frame animation', () => {
    const battle = companionBattleFromDef(getCompanion('blue'))

    expect(battle?.attackEnd.src).toBe('/cosmetics/companion/blue/attack-end.lossless.webp')
    expect(battle?.miss.src).toBe('/cosmetics/companion/blue/miss.lossless.webp')
    expect(battle?.death).toMatchObject({
      frameWidth: 253,
      frameHeight: 244,
      columns: 5,
      rows: 5,
      frameCount: 25,
      loop: false,
    })
  })

  it('registers White as 25-frame animated battle sheets', () => {
    const def = getCompanion('white')
    const world = companionFromDef(def)
    const battle = companionBattleFromDef(def)

    expect(world?.id).toBe('white')
    expect(world?.sprites.idle).toMatchObject({
      name: 'white.idle',
      src: '/cosmetics/companion/white/idle.lossless.webp',
      frameWidth: 250,
      frameHeight: 239,
      columns: 5,
      rows: 5,
      frameCount: 25,
    })
    expect(world?.sprites.run.name).toBe('white.run')
    expect(battle?.attack).toMatchObject({
      name: 'white.attack',
      src: '/cosmetics/companion/white/attack.lossless.webp',
      frameCount: 25,
      loop: false,
    })
    expect(battle?.attackEnd).toMatchObject({
      name: 'white.attack-end',
      src: '/cosmetics/companion/white/attack-end.lossless.webp',
      frameCount: 25,
      loop: false,
    })
    expect(battle?.miss).toMatchObject({
      name: 'white.miss',
      src: '/cosmetics/companion/white/miss.lossless.webp',
      frameCount: 25,
      loop: false,
    })
    expect(battle?.hurt.name).toBe('white.hurt')
    expect(battle?.death.name).toBe('white.death')
  })

  it('registers Black as 25-frame animated battle sheets', () => {
    const def = getCompanion('black')
    const world = companionFromDef(def)
    const battle = companionBattleFromDef(def)

    expect(world?.id).toBe('black')
    expect(world?.sprites.idle).toMatchObject({
      name: 'black.idle',
      src: '/cosmetics/companion/black/idle.lossless.webp',
      frameWidth: 251,
      frameHeight: 251,
      columns: 5,
      rows: 5,
      frameCount: 25,
    })
    expect(world?.sprites.run.name).toBe('black.run')
    expect(battle?.attack).toMatchObject({
      name: 'black.attack',
      src: '/cosmetics/companion/black/attack.lossless.webp',
      frameCount: 25,
      loop: false,
    })
    expect(battle?.attackEnd).toMatchObject({
      name: 'black.attack-end',
      src: '/cosmetics/companion/black/attack-end.lossless.webp',
      frameCount: 25,
      loop: false,
    })
    expect(battle?.miss).toMatchObject({
      name: 'black.miss',
      src: '/cosmetics/companion/black/miss.lossless.webp',
      frameCount: 25,
      loop: false,
    })
    expect(battle?.hurt.name).toBe('black.hurt')
    expect(battle?.death.name).toBe('black.death')
  })

  it('uses attack as the companion combat sprite key', () => {
    const def = getCompanion('blue')

    expect(def.sprites.attack).toBeTruthy()
    expect(def.sprites.cast).toBeUndefined()
  })

})
