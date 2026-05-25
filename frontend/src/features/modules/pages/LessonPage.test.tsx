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
  },
}))

vi.mock('@/features/modules/components/LessonContentRenderer', () => ({
  LessonContentRenderer: ({ lesson }: { lesson: { title: string } }) => <h1>{lesson.title}</h1>,
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

  it('renders orientation lesson content without requiring a lesson kind', async () => {
    vi.mocked(modulesApi.getLesson).mockResolvedValue({
      id: 7,
      slug: 'orientation-basics',
      title: 'Orientation Basics',
      subtitle: 'Start here.',
      sort_order: 1,
      is_complete: false,
      scenario_count: 0,
      content_html: '<h1>Orientation Basics</h1>',
      scoped_css: '',
      interaction_steps: [],
      module: {
        id: 1,
        slug: 'orientation',
        number: 0,
        title: 'Orientation',
        is_orientation: true,
      },
    })

    renderPage()

    expect(await screen.findByRole('heading', { name: 'Orientation Basics' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /mark lesson read/i })).toBeInTheDocument()
    expect(screen.getByText('Saved to your foundation progress.')).toBeInTheDocument()
    expect(screen.queryByText(/overview/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/scenario practice starts/i)).not.toBeInTheDocument()
  })
})
