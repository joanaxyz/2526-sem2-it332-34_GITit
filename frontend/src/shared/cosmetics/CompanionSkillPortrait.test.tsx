import { existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { CompanionSkillPortrait } from './CompanionSkillPortrait'

afterEach(cleanup)

describe('CompanionSkillPortrait', () => {
  it.each([
    ['blue', 'git init', 'skill-flames-25/init.png', 0, -768],
    ['black', 'git init', 'skill-lightning-25/init.png', -1024, -512],
    ['white', 'git add', 'skill-ice-25/add.png', 0, -768],
    ['white', 'git unsupported', 'skill-ice-25/default.png', 0, -768],
    ['unknown', 'git init', 'skill-flames-25/init.png', 0, -768],
  ] as const)('crops one indexed impact frame from shipped %s art for %s', (companion, command, suffix, x, y) => {
    render(<CompanionSkillPortrait companionSlug={companion} command={command} title="Learned spell" />)
    const portrait = screen.getByRole('img', { name: 'Learned spell' })
    const image = portrait.querySelector('image')!
    const source = image.getAttribute('href')!
    expect(source).toContain(suffix)
    expect(existsSync(resolve(process.cwd(), 'public', source.slice(1)))).toBe(true)
    expect(portrait).toHaveAttribute('viewBox', '0 0 256 256')
    expect(image).toHaveAttribute('x', String(x))
    expect(image).toHaveAttribute('y', String(y))
    expect(image).toHaveAttribute('width', '1280')
    expect(image).toHaveAttribute('height', '1280')
    expect(portrait.querySelector('clipPath rect')).toHaveAttribute('width', '256')
    expect(portrait.querySelector('clipPath rect')).toHaveAttribute('height', '256')
    expect(portrait.querySelector('g')).toHaveAttribute('clip-path', `url(#${portrait.querySelector('clipPath')!.id})`)
  })
})
