import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { DrillSummary } from './DrillSummary'
import { DRILL_PLAN_FIXTURE } from '@/features/dev/utils/drillPlan'
import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import type { ChapterBook } from '@/features/story-map/components/book/bookTypes'
import type { DrillMistake } from '@/features/drills/types'

const plan = { ...DRILL_PLAN_FIXTURE, cards: DRILL_PLAN_FIXTURE.cards.slice(0, 2) }
const book: ChapterBook = {
  chapter_id: plan.level.chapter_id!, slug: 'basics', number: 1, title: 'Basics', description: '',
  lesson_count: 1, lessons: [{ item_type: 'lesson', id: 1, slug: 'how-git-thinks', title: 'How Git thinks', summary: '', pages: [] }],
  command_count: 2, commands: [
    { id: 1, slug: 'git-init', base_command: 'git init', title: 'Initialize', summary: 'Create a repository.', tags: [], forms: [], pages: [] },
    { id: 2, slug: 'git-add', base_command: 'git add', title: 'Stage', summary: 'Prepare changes for a commit.', tags: [], forms: [], pages: [] },
  ],
}
const mistake: DrillMistake = {
  cardKey: plan.cards[0].key, round: 0, subject: plan.cards[0].intent,
  picked: 'git status', pickedGloss: 'Inspect files', expected: plan.cards[0].command,
  expectedGloss: plan.cards[0].intent, voice: 'machine',
}
let client: QueryClient
function mount(customPlan = plan, { mistakes = [], shaky = [plan.cards[0].key] }: { mistakes?: DrillMistake[]; shaky?: string[] } = {}) {
  client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={client}><MemoryRouter>
    <DrillSummary plan={customPlan} rail={[]} accuracy={80} answered={5} shaky={shaky} mistakes={mistakes}
      saveFailed={false} onRestart={vi.fn()} />
  </MemoryRouter></QueryClientProvider>)
}
afterEach(() => { cleanup(); client?.clear(); vi.restoreAllMocks() })

describe('drill result views', () => {
  it('opens on corrections and switches to command references without stacking both lists', () => {
    mount(plan, { mistakes: [mistake] })
    expect(screen.getByRole('tab', { name: 'Review mistakes' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByRole('tabpanel', { name: 'Review mistakes' })).toBeVisible()
    expect(screen.queryByRole('region', { name: 'Commands used in this drill' })).not.toBeInTheDocument()
    expect(screen.getByText('git status')).toBeVisible()
    fireEvent.click(screen.getByRole('tab', { name: 'Commands used' }))
    expect(screen.getByRole('tab', { name: 'Commands used' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByRole('region', { name: 'Commands used in this drill' })).toBeVisible()
    expect(screen.queryByRole('region', { name: 'Your flight review' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', { name: 'Review mistakes' }))
    expect(screen.getByText('git status')).toBeVisible()
    expect(screen.getByText('80%')).toBeInTheDocument()
  })

  it('supports arrow keys and Home/End with focus following the selected tab', () => {
    mount()
    const review = screen.getByRole('tab', { name: 'Review mistakes' })
    const commands = screen.getByRole('tab', { name: 'Commands used' })
    review.focus()
    fireEvent.keyDown(review, { key: 'ArrowRight' })
    expect(commands).toHaveFocus()
    expect(commands).toHaveAttribute('aria-selected', 'true')
    fireEvent.keyDown(commands, { key: 'Home' })
    expect(review).toHaveFocus()
    expect(review).toHaveAttribute('aria-selected', 'true')
    fireEvent.keyDown(review, { key: 'End' })
    expect(commands).toHaveFocus()
  })

  it('opens the selected command in the Field Guide from a quiet reference control', async () => {
    const getBook = vi.spyOn(storyMapApi, 'getChapterBook').mockResolvedValue(book)
    mount()
    expect(getBook).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('tab', { name: 'Commands used' }))
    const commands = screen.getByRole('region', { name: 'Commands used in this drill' })
    expect(within(commands).getAllByRole('button')).toHaveLength(2)
    expect(within(commands).queryByText('Field Guide')).not.toBeInTheDocument()
    expect(within(commands).queryByText('Review')).not.toBeInTheDocument()
    fireEvent.click(within(commands).getByRole('button', { name: `Open ${plan.cards[1].command} in the Field Guide` }))
    expect(getBook).toHaveBeenCalledWith(plan.level.chapter_id)
    expect(await screen.findByRole('heading', { name: 'git add' })).toBeInTheDocument()
    const dialog = screen.getByRole('dialog')
    expect(within(dialog).getByRole('button', { name: 'git add' })).toHaveAttribute('aria-current', 'page')
    fireEvent.keyDown(dialog, { key: 'Escape' })
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Commands used' })).toHaveAttribute('aria-selected', 'true')
  })

  it('links detailed mistakes to the real level that teaches their command', () => {
    mount(plan, { mistakes: [mistake] })
    const review = screen.getByRole('region', { name: 'Your flight review' })
    const practice = within(review).getByRole('link', { name: `Practice ${plan.cards[0].command} in ${plan.level.title}` })
    expect(practice).toHaveAttribute('href', `/stories/${plan.level.story_slug}?chapter=${plan.level.chapter_id}&level=${plan.level.id}`)
  })

  it('still provides a practice destination for weak commands restored without detailed history', () => {
    mount()
    const weak = screen.getByRole('list', { name: 'Worth another look' })
    expect(within(weak).getByText(plan.cards[0].command)).toBeVisible()
    expect(within(weak).getByRole('link', { name: `Practice ${plan.cards[0].command} in ${plan.level.title}` }))
      .toHaveAttribute('href', `/stories/${plan.level.story_slug}?chapter=${plan.level.chapter_id}&level=${plan.level.id}`)
  })

  it('starts on command references after a clean flight and offers an honest empty review', () => {
    mount(plan, { shaky: [] })
    expect(screen.getByRole('tab', { name: 'Commands used' })).toHaveAttribute('aria-selected', 'true')
    fireEvent.click(screen.getByRole('tab', { name: 'Review mistakes' }))
    expect(screen.getByText('No mistakes to review.')).toBeVisible()
  })

  it('does not offer broken Field Guide controls when the drill has no chapter', () => {
    mount({ ...plan, level: { ...plan.level, chapter_id: null } })
    fireEvent.click(screen.getByRole('tab', { name: 'Commands used' }))
    const commands = screen.getByRole('region', { name: 'Commands used in this drill' })
    expect(within(commands).getByText(plan.cards[0].command)).toBeVisible()
    expect(within(commands).queryByRole('button')).not.toBeInTheDocument()
  })
})
