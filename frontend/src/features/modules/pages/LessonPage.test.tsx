import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { modulesApi } from '@/features/modules/api/modulesApi'
import { LessonPage } from './LessonPage'

vi.mock('@/features/modules/api/modulesApi', () => ({
  modulesApi: {
    getLesson: vi.fn(),
    completeOrientationLesson: vi.fn(),
    startOrientationSession: vi.fn(),
    submitOrientationCommand: vi.fn(),
  },
}))

vi.mock('@/features/scenarios/utils/scenarioCache', () => ({
  invalidateScenarioProgressQueries: vi.fn(),
}))

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/lessons/7']}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('LessonPage', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('renders orientation workspace with Mark as complete', async () => {
    vi.mocked(modulesApi.getLesson).mockResolvedValue({
      id: 7,
      slug: 'what-is-git-and-why-it-matters',
      title: 'Lesson 0.1 — What Is Git and Why Does It Matter?',
      subtitle: 'Version control basics.',
      sort_order: 1,
      is_complete: false,
      scenario_count: 0,
      content_html: '<p>Git intro</p>',
      scoped_css: '',
      interaction_steps: [
        {
          id: 'vc-discipline',
          kind: 'continue',
          title: 'Version control discipline',
          prompt: 'Read and continue.',
          body: 'Version control tracks changes.',
        },
      ],
      module: {
        id: 1,
        slug: 'orientation',
        number: 0,
        title: 'Orientation',
        is_orientation: true,
      },
    })

    renderPage()

    expect(await screen.findByRole('heading', { name: /What Is Git/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Complete steps|Mark as complete/i })).toBeInTheDocument()
  })
})
