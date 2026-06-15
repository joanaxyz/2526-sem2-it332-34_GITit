import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ArtifactOverview } from './ArtifactOverview'
import { TowerStoreySection } from './TowerStoreySection'
import { TowerActionButton } from './TowerActionButton'
import { useTowerSelection } from '@/features/tower-map/hooks/useTowerSelection'

const mocks = vi.hoisted(() => ({
  getStoreyOverview: vi.fn(),
  getAssetDescriptors: vi.fn(),
  startChallengeRun: vi.fn(),
  retryChallengeRun: vi.fn(),
}))

vi.mock('motion/react', async () => {
  const React = await import('react')
  const createMotion = (tag: keyof HTMLElementTagNameMap) => {
    const Component = ({ children, ...props }: Record<string, unknown> & { children?: React.ReactNode }) => {
      const domProps = { ...props }
      delete domProps.initial
      delete domProps.whileInView
      delete domProps.viewport
      delete domProps.transition
      delete domProps.variants
      return React.createElement(tag, domProps, children)
    }
    return Component
  }
  return {
    motion: {
      article: createMotion('article'),
      aside: createMotion('aside'),
      button: createMotion('button'),
      div: createMotion('div'),
      header: createMotion('header'),
      section: createMotion('section'),
      span: createMotion('span'),
    },
    useInView: () => true,
  }
})

vi.mock('@/features/tower-map/api/towerMapApi', () => ({
  towerMapApi: {
    getStoreyOverview: mocks.getStoreyOverview,
  },
}))

vi.mock('@/shared/assets/assetsApi', () => ({
  assetsApi: {
    getDescriptors: mocks.getAssetDescriptors,
  },
}))

vi.mock('@/features/challenges/api/challengesApi', () => ({
  challengesApi: {
    startChallengeRun: mocks.startChallengeRun,
    retryChallengeRun: mocks.retryChallengeRun,
  },
}))

class ImmediateIntersectionObserver {
  private callback: IntersectionObserverCallback

  constructor(callback: IntersectionObserverCallback) {
    this.callback = callback
  }

  observe(target: Element) {
    this.callback([{ isIntersecting: true, target } as IntersectionObserverEntry], this as unknown as IntersectionObserver)
  }

  disconnect() {}
  unobserve() {}
  takeRecords() {
    return []
  }
}

vi.stubGlobal('IntersectionObserver', ImmediateIntersectionObserver)

const CANONICAL_ADVENTURE = {
  item_type: 'command_adventure',
  id: 2,
  slug: 'tracking-command-adventure',
  title: 'Preparing File Changes',
  description: 'Learn how to inspect, stage, and save file changes.',
  status: 'not_started',
  is_passed: false,
  active_run_id: null,
  latest_run_id: null,
  level_count: 5,
  progress: { value: 0, numerator: 0, denominator: 5 },
}

const CANONICAL_TOME = {
  item_type: 'tome',
  id: 7,
  slug: 'how-git-thinks',
  title: 'How Git Thinks',
  summary: 'The four places your work lives.',
  placement: 'above_adventure',
  pages: [
    {
      id: 'overview',
      title: 'The four places',
      heading: 'The four places',
      section_type: 'overview',
      blocks: [{ type: 'paragraph', body: 'Every Git command moves work between four places.' }],
    },
  ],
}

const CANONICAL_CHALLENGE = {
  item_type: 'challenge',
  id: 30,
  slug: 'compose-clean-history',
  title: 'Compose Clean History',
  summary: 'Turn workspace changes into focused commits.',
  narrative: '',
  levels: ['easy', 'medium', 'hard'].map((difficulty, index) => ({
    id: 300 + index,
    difficulty,
    status: difficulty === 'easy' ? 'not_started' : 'locked',
    required_successful_attempts: 2,
    successful_attempts: { count: 0, required: 2 },
    active_run_id: null,
    latest_attempt: null,
    completion: null,
    review_available: false,
    command_budget: { min_counted_commands: 3, max_counted_commands: 6 },
  })),
}

function canonicalTowerLayout(storeyId: number) {
  return {
    storeyId,
    pieces: [
      { instanceId: `storey-${storeyId}-crown`, assetSlug: 'official-crown', pieceType: 'crown' },
      {
        instanceId: `storey-${storeyId}-tome-section-${CANONICAL_TOME.id}`,
        assetSlug: 'official-hall-section',
        pieceType: 'section',
      },
      {
        instanceId: `storey-${storeyId}-landing-after-tomes`,
        assetSlug: 'official-tome-landing',
        pieceType: 'landing',
      },
      {
        instanceId: `storey-${storeyId}-adventure-section`,
        assetSlug: 'official-hall-section',
        pieceType: 'section',
      },
      {
        instanceId: `storey-${storeyId}-landing-after-adventure`,
        assetSlug: 'official-landing',
        pieceType: 'landing',
      },
      {
        instanceId: `storey-${storeyId}-challenge-section-${CANONICAL_CHALLENGE.id}`,
        assetSlug: 'official-trial-section',
        pieceType: 'section',
      },
      {
        instanceId: `storey-${storeyId}-landing-after-challenges`,
        assetSlug: 'official-challenge-landing',
        pieceType: 'landing',
      },
    ],
  } as const
}

function canonicalArtifacts(storeyId: number, includeTome = true) {
  return [
    ...(includeTome
      ? [
          {
            id: `storey-${storeyId}-artifact-tome-${CANONICAL_TOME.id}`,
            targetInstanceId: `storey-${storeyId}-tome-section-${CANONICAL_TOME.id}`,
            assetSlug: 'official-tome-artifact',
            role: 'tome',
            contentBinding: { kind: 'tome', id: CANONICAL_TOME.id },
            x: 184,
            y: 112,
            scale: 1,
            width: 96,
            height: 88,
            rotation: 0,
            anchor: '',
            zIndex: 12,
          },
        ]
      : []),
    {
      id: `storey-${storeyId}-artifact-adventure`,
      targetInstanceId: `storey-${storeyId}-adventure-section`,
      assetSlug: 'official-gate-artifact',
      role: 'adventure',
      contentBinding: { kind: 'adventure', id: CANONICAL_ADVENTURE.id },
      x: 184,
      y: 122,
      scale: 1,
      width: 116,
      height: 134,
      rotation: 0,
      anchor: '',
      zIndex: 12,
    },
    {
      id: `storey-${storeyId}-artifact-challenge-${CANONICAL_CHALLENGE.id}`,
      targetInstanceId: `storey-${storeyId}-challenge-section-${CANONICAL_CHALLENGE.id}`,
      assetSlug: 'official-portcullis-artifact',
      role: 'challenge',
      contentBinding: { kind: 'challenge', id: CANONICAL_CHALLENGE.id },
      x: 184,
      y: 124,
      scale: 1,
      width: 90,
      height: 132,
      rotation: 0,
      anchor: '',
      zIndex: 12,
    },
  ] as const
}

const TOWER_SPRITE = {
  url: '/media/assets/sprites/official-piece.svg',
  frame_count: 1,
  columns: 1,
  rows: 1,
  frame_width: 1,
  frame_height: 1,
  fps: 1,
  loops: true,
}

function towerPieceDescriptor(slug: string, pieceType: string, anchors = {}) {
  return {
    slug,
    label: slug,
    kind: 'tower_piece',
    scale: 1,
    config: {},
    sprites: { default: TOWER_SPRITE },
    piece_type: pieceType,
    tower_piece: {
      piece_type: pieceType,
      view_box: '0 0 220 48',
      anchors,
      bounds: {},
      interaction_zones: {},
      state_variants: {},
      svg_sanitized: true,
      svg: '<svg data-piece-art="arcane-spire-test" viewBox="0 0 220 48" xmlns="http://www.w3.org/2000/svg"></svg>',
    },
  }
}

function towerArtifactDescriptor(slug: string) {
  return {
    slug,
    label: slug,
    kind: 'tower_artifact',
    scale: 1,
    config: {},
    sprites: { default: TOWER_SPRITE },
  }
}

function mockTowerPieceDescriptors() {
  mocks.getAssetDescriptors.mockImplementation((kind: string) =>
    Promise.resolve(
      kind === 'tower_artifact'
        ? {
            kind: 'tower_artifact',
            results: {
              'official-gate-artifact': towerArtifactDescriptor('official-gate-artifact'),
              'official-portcullis-artifact': towerArtifactDescriptor('official-portcullis-artifact'),
              'official-tome-artifact': towerArtifactDescriptor('official-tome-artifact'),
            },
          }
        : {
            kind: 'tower_piece',
            results: {
              'official-crown': towerPieceDescriptor('official-crown', 'crown'),
              'official-hall-section': towerPieceDescriptor('official-hall-section', 'section'),
              'official-trial-section': towerPieceDescriptor('official-trial-section', 'section'),
              'official-landing': towerPieceDescriptor('official-landing', 'landing', {
                walk_rail: { x1: 18, y1: 18, x2: 202, y2: 18 },
              }),
              'official-challenge-landing': towerPieceDescriptor('official-challenge-landing', 'landing', {
                walk_rail: { x1: 16, y1: 16, x2: 204, y2: 16 },
              }),
              'official-tome-landing': towerPieceDescriptor('official-tome-landing', 'landing', {
                walk_rail: { x1: 20, y1: 14, x2: 200, y2: 14 },
              }),
            },
          },
    ),
  )
}

function mockCanonicalStoreyContent() {
  mocks.getStoreyOverview.mockImplementation((storeyId: number) =>
    Promise.resolve({
      storey_id: storeyId,
      command_adventure: CANONICAL_ADVENTURE,
      tomes: [CANONICAL_TOME],
      challenges: [CANONICAL_CHALLENGE],
      tower_layout: canonicalTowerLayout(storeyId),
      artifacts: canonicalArtifacts(storeyId),
    }),
  )
}

function renderHub() {
  mockTowerPieceDescriptors()
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <TowerStoreySection
          storey={{
            id: 2,
            slug: 'tracking-changes-snapshots',
            number: 2,
            title: 'Tracking Changes and Creating Snapshots',
            description: 'Stage changes and create commits.',
            sort_order: 2,
            command_skill_count: 2,
            challenge_count: 1,
            level_completion: { value: 0, numerator: 0, denominator: 5 },
          }}
        />
        <ArtifactOverview storeyId={2} />
        <TowerActionButton />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('TowerStoreySection', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
    useTowerSelection.setState({ selected: null })
  })

  it('renders adventure, tome, and challenge artifacts on generic sections', async () => {
    mockCanonicalStoreyContent()
    renderHub()

    await waitFor(() =>
      expect(
        screen.getByRole('button', { name: /select command adventure: preparing file changes/i }),
      ).toBeInTheDocument(),
    )
    expect(
      screen.getByRole('button', { name: /select compose clean history: easy/i }),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /select command adventure/i })).toHaveAttribute(
      'data-piece-id',
      'storey-2-adventure-section',
    )
    await waitFor(() =>
      expect(document.querySelector('[data-piece-id="storey-2-landing-after-adventure"]')).toHaveAttribute(
        'data-walk-rail-x1',
        '18',
      ),
    )
    expect(document.querySelector('.tower-roof-art')).toBeInTheDocument()
    expect(document.querySelector('.tower-hall-art')).toBeInTheDocument()
  })

  it('shows the adventure overview + Play action when its artifact is selected', async () => {
    mockCanonicalStoreyContent()
    renderHub()

    const artifact = await screen.findByRole('button', { name: /select command adventure: preparing file changes/i })
    fireEvent.click(artifact)

    const overview = screen.getByLabelText('Selected artifact')
    expect(within(overview).getByText('Preparing File Changes')).toBeInTheDocument()
    expect(within(overview).getByText('0/5 solved')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^play$/i })).toBeInTheDocument()
  })

  it('renders the tome lectern above the adventure and opens the reader via Read', async () => {
    mockCanonicalStoreyContent()
    renderHub()

    const lectern = await screen.findByRole('button', { name: /select tome: how git thinks/i })
    const adventureDoor = await screen.findByRole('button', {
      name: /select command adventure: preparing file changes/i,
    })
    // The tome section is authored above the adventure gate.
    expect(lectern.compareDocumentPosition(adventureDoor) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()

    fireEvent.click(lectern)

    const overview = screen.getByLabelText('Selected artifact')
    expect(within(overview).getByText('Tome')).toBeInTheDocument()
    expect(within(overview).getByText('How Git Thinks')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /^read$/i }))
    await waitFor(() => expect(screen.getByText('The four places')).toBeInTheDocument())
  })

  it('does not render a tome section when the storey has no authored tome', async () => {
    mocks.getStoreyOverview.mockImplementation((storeyId: number) =>
      Promise.resolve({
        storey_id: storeyId,
        command_adventure: CANONICAL_ADVENTURE,
        tomes: [],
        challenges: [CANONICAL_CHALLENGE],
        tower_layout: {
          storeyId,
          pieces: canonicalTowerLayout(storeyId).pieces.filter(
            (piece) =>
              !piece.instanceId.includes('tome-section') &&
              !piece.instanceId.includes('landing-after-tomes'),
          ),
        },
        artifacts: canonicalArtifacts(storeyId, false),
      }),
    )
    renderHub()

    await waitFor(() => expect(mocks.getStoreyOverview).toHaveBeenCalled())
    expect(screen.queryByRole('button', { name: /select tome/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: /^tome$/i })).not.toBeInTheDocument()
  })

  it('shows the chosen level overview with accuracy + attempts when a challenge artifact is selected', async () => {
    mockCanonicalStoreyContent()
    renderHub()

    const easyDoor = await screen.findByRole('button', {
      name: /select compose clean history: easy/i,
    })
    fireEvent.click(easyDoor)

    const overview = screen.getByLabelText('Selected artifact')
    expect(within(overview).getByText('Compose Clean History')).toBeInTheDocument()
    expect(within(overview).getByText('Easy')).toBeInTheDocument()
    // Accuracy with no attempts yet renders as a placeholder.
    expect(within(overview).getByText('--%')).toBeInTheDocument()
  })
})
