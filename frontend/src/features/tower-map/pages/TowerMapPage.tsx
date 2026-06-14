import {
  memo,
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
} from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, useScroll, useSpring, useTransform } from 'motion/react'
import { useSearchParams } from 'react-router-dom'

import { towerMapApi } from '@/features/tower-map/api/towerMapApi'
import { TowerCharacter } from '@/features/tower-map/character/TowerCharacter'
import { DoorOverview } from '@/features/tower-map/components/DoorOverview'
import { StoreyOverview, TowerStoreySection } from '@/features/tower-map/components/TowerStoreySection'
import { SkyClock } from '@/features/tower-map/components/SkyClock'
import { TowerActionButton } from '@/features/tower-map/components/TowerActionButton'
import { TowerControls, type TowerView } from '@/features/tower-map/components/TowerControls'
import { InTowerEditor } from '@/features/tower-map/editor/InTowerEditor'
import { PrivateTowerStack } from '@/features/tower-designs/components/PrivateTowerStack'
import { useTowerDesignEditor } from '@/features/tower-designs/hooks/useTowerDesignEditor'
import { useTowerSelection } from '@/features/tower-map/hooks/useTowerSelection'
import { computeSky } from '@/features/tower-map/sky/useTowerSky'
import { clamp, lerp, mulberry32 } from '@/features/tower-map/towerLayoutRandom'
import type { LearningStorey } from '@/features/tower-map/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { assetsApi } from '@/shared/assets/assetsApi'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { readPreference, writePreference } from '@/shared/utils/persistentState'
import { characterFromDescriptor } from '@/shared/sprites/characters'

// One in-app day takes this long in real time when the cycle is auto-advancing.
const DAY_LENGTH_MS = 18 * 60 * 1000
const wrap24 = (hour: number) => ((hour % 24) + 24) % 24

// Remembered day-night clock state. `timeOfDay` is only restored when the cycle
// was paused; while running we resume from the real wall-clock time of day.
const CLOCK_PREFERENCE_KEY = 'tower:clock'
type ClockPreference = { running: boolean; timeOfDay: number }

function isFoundationsStorey(storey: LearningStorey) {
  return storey.number === 1 || storey.slug === 'creating-inspecting-repositories'
}

function storeyTitle(storey: LearningStorey) {
  return isFoundationsStorey(storey) ? 'Foundations' : storey.title
}

// Crisp-edged puffy clouds. Three silhouettes for variety; transparency, size and
// position come from CSS per instance. Every coordinate (including bezier
// control points) stays inside the viewBox - points outside it render as
// straight clipped edges on the cloud.
const CLOUD_SHAPES = {
  a: {
    viewBox: '0 0 120 58',
    d: 'M18 50 C9 50 4 44 7 38 C3 31 9 24 17 26 C18 15 30 9 39 15 C44 5 58 4 64 12 C71 5 83 7 87 15 C96 12 105 18 104 26 C112 27 116 34 113 41 C111 47 104 50 97 50 Z',
  },
  b: {
    viewBox: '0 0 134 46',
    d: 'M14 39 C6 39 2 33 5 28 C8 24 14 23 18 25 C19 16 30 12 37 17 C42 9 56 8 61 16 C67 10 79 11 83 18 C90 13 102 15 105 22 C114 20 125 24 126 31 C127 36 120 39 112 39 Z',
  },
  c: {
    viewBox: '0 0 112 62',
    d: 'M20 54 C11 54 5 47 9 40 C4 33 11 25 19 28 C19 16 32 10 42 16 C46 6 62 6 67 15 C74 8 87 11 88 21 C97 19 105 26 101 34 C108 38 105 50 95 52 C91 54 85 54 80 54 Z',
  },
} as const

type CloudVariant = keyof typeof CLOUD_SHAPES

function CloudShape({
  className,
  variant = 'a',
  style,
  'data-layer': dataLayer,
}: {
  className?: string
  variant?: CloudVariant
  style?: CSSProperties
  'data-layer'?: string
}) {
  const shape = CLOUD_SHAPES[variant]
  return (
    <svg className={className} style={style} data-layer={dataLayer} viewBox={shape.viewBox} aria-hidden="true">
      <path d={shape.d} />
    </svg>
  )
}

type CloudLayer = 'far' | 'mid' | 'near'

const CLOUD_VARIANTS: CloudVariant[] = ['a', 'b', 'c']
const LAYER_STYLE: Record<CloudLayer, { width: [number, number]; opacity: [number, number] }> = {
  far: { width: [18, 25], opacity: [0.22, 0.3] },
  mid: { width: [13, 20], opacity: [0.34, 0.46] },
  near: { width: [10, 16], opacity: [0.5, 0.66] },
}

type SeededCloud = {
  id: number
  variant: CloudVariant
  layer: CloudLayer
  top: number
  left: number
  width: number
  opacity: number
}

function buildCloudField(floors: number): SeededCloud[] {
  const count = Math.max(4, Math.round(floors * 0.9))
  const rand = mulberry32(0x7a9c13)
  return Array.from({ length: count }, (_, i): SeededCloud => {
    const layer = i % 5 === 0 ? 'far' : i % 5 === 3 ? 'mid' : 'near'
    const range = LAYER_STYLE[layer]
    const band = (i + 0.5) / count
    const top = clamp(band + (rand() - 0.5) * (1.05 / count), 0.04, 0.96) * 100
    const leftSide = rand() < 0.5
    const gutterStart = layer === 'near' ? 4 : -8
    const gutterSpan = layer === 'near' ? 24 : 32
    const left = leftSide ? gutterStart + rand() * gutterSpan : 100 - gutterStart - rand() * gutterSpan
    return {
      id: i,
      variant: CLOUD_VARIANTS[Math.floor(rand() * CLOUD_VARIANTS.length)],
      layer,
      top,
      left,
      width: lerp(range.width[0], range.width[1], rand()),
      opacity: lerp(range.opacity[0], range.opacity[1], rand()),
    }
  })
}

// The storey stack is the heavy part of the tree; memo it so the once-a-second
// clock-label re-render (from the sky cycle) never re-renders every storey.
//
// Storeys mount progressively: only the slice the user has scrolled to exists in
// the DOM, so the page height grows with the climb instead of pre-rendering the
// whole tower. The build zone at the bottom is the growth sentinel.
const TowerStoreys = memo(function TowerStoreys({
  storeys,
  mountedCount,
  onGrow,
}: {
  storeys: LearningStorey[]
  mountedCount: number
  onGrow: () => void
}) {
  const growRef = useRef<HTMLDivElement | null>(null)
  const allMounted = mountedCount >= storeys.length

  // Recreated after every growth step: the fresh observer fires its initial
  // callback immediately, so storeys keep mounting one by one while the build
  // zone sits inside the scroll margin and stop as soon as it drops below it.
  useEffect(() => {
    if (allMounted) return
    const el = growRef.current
    if (!el) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) onGrow()
      },
      { rootMargin: '0px 0px 480px 0px' },
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [allMounted, mountedCount, onGrow])

  return (
    <div className="tower-stack-column">
      {storeys.slice(0, mountedCount).map((storey, index) => (
        <TowerStoreySection
          displayTitle={storeyTitle(storey)}
          isFirst={index === 0}
          isLast={index === storeys.length - 1}
          key={storey.id}
          sequenceIndex={index}
          storey={storey}
        />
      ))}
      {!allMounted ? (
        <div className="tower-build-zone" ref={growRef} aria-hidden="true">
          <div className="tower-build-ghost">
            <span className="tower-build-ghost-window" />
            <span className="tower-build-ghost-window" />
            <span className="tower-build-ghost-window" />
          </div>
          <span className="tower-build-beam" />
        </div>
      ) : null}
    </div>
  )
})

export function TowerMapPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const storeyParam = searchParams.get('storey')
  const focusedStoreyId = storeyParam ? Number(storeyParam) : null
  const view: TowerView = searchParams.get('view') === 'mine' ? 'mine' : 'official'
  const editMode = searchParams.get('mode') === 'edit'
  const setView = useCallback(
    (next: TowerView) => {
      setSearchParams(
        (params) => {
          if (next === 'mine') params.set('view', 'mine')
          else params.delete('view')
          return params
        },
        { replace: true },
      )
    },
    [setSearchParams],
  )
  // Editing happens IN this page (no route change): `?mode=edit` swaps the
  // stage for the editor; `?design=<id>` targets a specific design (the personal
  // tower by default, or the official fork when editing the official tower).
  const { design: personalDesign } = useTowerDesignEditor()
  const editDesignParam = searchParams.get('design')
  const editDesignId = editDesignParam ? Number(editDesignParam) : personalDesign?.id ?? null
  const exitEdit = useCallback(() => {
    setSearchParams(
      (params) => {
        params.delete('mode')
        params.delete('design')
        return params
      },
      { replace: true },
    )
  }, [setSearchParams])
  const storeysQuery = useQuery({
    queryKey: queryKeys.storeys,
    queryFn: towerMapApi.listStoreys,
    staleTime: 5 * 60 * 1000,
  })
  const characterQuery = useQuery({
    queryKey: queryKeys.assetDescriptors('character'),
    queryFn: () => assetsApi.getDescriptors('character'),
    staleTime: 10 * 60 * 1000,
    retry: 1,
  })

  const storeys = useMemo(() => storeysQuery.data ?? [], [storeysQuery.data])
  // Blue is rendered from his seeded descriptor; null until it loads (no local
  // sprite fallback now that sprites live only in the backend seed).
  const activeCharacter = useMemo(() => {
    const descriptor = characterQuery.data?.results.blue
    if (descriptor?.kind !== 'character') return null
    return characterFromDescriptor(descriptor)
  }, [characterQuery.data])
  const cloudField = useMemo(() => buildCloudField(storeys.length), [storeys.length])
  // How many storeys exist in the DOM. Starts at one; the build-zone observer
  // raises it as the user scrolls down. A ?storey= deep link raises the floor
  // so the target storey is already mounted on first render.
  const focusIndex = useMemo(
    () => (focusedStoreyId ? storeys.findIndex((storey) => storey.id === focusedStoreyId) : -1),
    [focusedStoreyId, storeys],
  )
  const mountedFloor = focusIndex >= 0 ? focusIndex + 1 : 1
  const [mountedRaw, setMountedRaw] = useState(1)
  const mountedCount = Math.max(mountedRaw, mountedFloor)
  const growTower = useCallback(
    () => setMountedRaw((count) => Math.max(count, mountedFloor) + 1),
    [mountedFloor],
  )
  const clearSelection = useTowerSelection((state) => state.clear)
  const selectedStoreyId = useTowerSelection((state) => state.selected?.storeyId ?? null)
  const [activeStoreyId, setActiveStoreyId] = useState<number | null>(null)
  const activeStorey = useMemo(
    () => storeys.find((storey) => storey.id === activeStoreyId) ?? storeys[0] ?? null,
    [activeStoreyId, storeys],
  )
  const doorOverviewStoreyId = selectedStoreyId ?? activeStorey?.id ?? null
  const activeStoreyIdRef = useRef<number | null>(null)
  useEffect(() => {
    activeStoreyIdRef.current = activeStoreyId
  }, [activeStoreyId])

  // -- Living sky ----------------------------------------------------------
  const pageRef = useRef<HTMLDivElement | null>(null)
  const prefersReduced = useMemo(
    () => typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    [],
  )
  const initialClockPref = useMemo(() => readPreference<ClockPreference | null>(CLOCK_PREFERENCE_KEY, null), [])
  const initialRunning = initialClockPref?.running ?? !prefersReduced
  const initialTime = useMemo(() => {
    if (initialClockPref && !initialClockPref.running && Number.isFinite(initialClockPref.timeOfDay)) {
      return wrap24(initialClockPref.timeOfDay)
    }
    const now = new Date()
    return now.getHours() + now.getMinutes() / 60
  }, [initialClockPref])
  const timeRef = useRef(initialTime)
  const runningRef = useRef(initialRunning)
  const [timeOfDay, setTimeOfDay] = useState(initialTime)
  const [running, setRunning] = useState(initialRunning)
  const [phaseLabel, setPhaseLabel] = useState(() => computeSky(initialTime).phaseLabel)

  const applySky = useCallback((hour: number) => {
    const el = pageRef.current
    if (!el) return
    const sky = computeSky(hour)
    for (const key in sky.vars) el.style.setProperty(key, sky.vars[key])
  }, [])

  // Paint the correct sky before first frame (no flash of the fallback palette).
  useLayoutEffect(() => {
    applySky(timeRef.current)
  }, [applySky])

  // Auto-advance loop: write CSS vars imperatively each frame; surface a throttled
  // time/label to React (~1/sec) only so the clock hand + readout track along.
  useEffect(() => {
    let raf = 0
    let last = performance.now()
    let lastLabel = 0
    let applied = NaN

    const tick = (now: number) => {
      const dt = now - last
      last = now
      if (runningRef.current && !document.hidden) {
        timeRef.current = wrap24(timeRef.current + (dt / DAY_LENGTH_MS) * 24)
      }
      if (timeRef.current !== applied) {
        applied = timeRef.current
        applySky(timeRef.current)
      }
      if (now - lastLabel > 1000) {
        lastLabel = now
        setTimeOfDay(timeRef.current)
        setPhaseLabel(computeSky(timeRef.current).phaseLabel)
      }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [applySky])

  // Reset the selection when leaving the tower.
  useEffect(() => () => clearSelection(), [clearSelection])

  const handleScrub = useCallback(
    (hour: number) => {
      runningRef.current = false
      setRunning(false)
      timeRef.current = hour
      setTimeOfDay(hour)
      setPhaseLabel(computeSky(hour).phaseLabel)
      applySky(hour)
      // Scrubbing pauses the cycle and freezes the chosen time; remember both.
      writePreference<ClockPreference>(CLOCK_PREFERENCE_KEY, { running: false, timeOfDay: hour })
    },
    [applySky],
  )

  const toggleRunning = useCallback(() => {
    runningRef.current = !runningRef.current
    setRunning(runningRef.current)
    writePreference<ClockPreference>(CLOCK_PREFERENCE_KEY, {
      running: runningRef.current,
      timeOfDay: timeRef.current,
    })
  }, [])

  // -- Scroll-linked parallax (composed on top of the time-driven positions) --
  const { scrollY, scrollYProgress } = useScroll()
  const skyProgress = useSpring(scrollYProgress, { stiffness: 70, damping: 24, mass: 0.5 })
  const moonY = useTransform(skyProgress, [0, 1], ['0px', '-90px'])
  const sunY = useTransform(skyProgress, [0, 1], ['0px', '-60px'])
  const starsFarY = useTransform(skyProgress, [0, 1], ['0px', '-45px'])

  const cloudSpring = useMemo(() => ({ stiffness: 60, damping: 22, mass: 0.4 }), [])
  const cloudFarY = useSpring(useTransform(scrollY, (v) => v * 0.12), cloudSpring)
  const cloudMidY = useSpring(useTransform(scrollY, (v) => v * -0.02), cloudSpring)
  const cloudNearY = useSpring(useTransform(scrollY, (v) => v * -0.12), cloudSpring)
  const cloudLayerY = useMemo(
    () => ({ far: cloudFarY, mid: cloudMidY, near: cloudNearY }),
    [cloudFarY, cloudMidY, cloudNearY],
  )
  const cloudsByLayer = useMemo(
    () => ({
      far: cloudField.filter((cloud) => cloud.layer === 'far'),
      mid: cloudField.filter((cloud) => cloud.layer === 'mid'),
      near: cloudField.filter((cloud) => cloud.layer === 'near'),
    }),
    [cloudField],
  )

  const renderCloudLayer = useCallback((layer: CloudLayer) => (
    <motion.div className="tower-cloud-layer" key={layer} style={{ y: cloudLayerY[layer] }}>
      {cloudsByLayer[layer].map((cloud) => (
        <CloudShape
          className="tower-cloud"
          data-layer={layer}
          key={cloud.id}
          style={{
            top: `${cloud.top}%`,
            left: `${cloud.left}%`,
            width: `${cloud.width}rem`,
            opacity: cloud.opacity,
          }}
          variant={cloud.variant}
        />
      ))}
    </motion.div>
  ), [cloudLayerY, cloudsByLayer])

  // The mount floor guarantees the deep-linked storey is in the DOM by the time
  // this effect runs, so it only has to scroll there (once per focus target).
  const focusHandledRef = useRef<number | null>(null)
  useEffect(() => {
    if (!focusedStoreyId || focusIndex === -1) return
    if (focusHandledRef.current === focusedStoreyId) return
    focusHandledRef.current = focusedStoreyId
    window.requestAnimationFrame(() => {
      document.querySelector(`[data-storey-id="${focusedStoreyId}"]`)?.scrollIntoView({
        block: 'start',
        behavior: 'smooth',
      })
    })
  }, [focusedStoreyId, focusIndex])

  // No reset effect needed when storeys change: the activeStorey memo above
  // already falls back to storeys[0] whenever the stored id is stale or null.

  useEffect(() => {
    if (!storeys.length) return

    let frame = 0
    const updateActiveStorey = () => {
      frame = 0
      const page = pageRef.current
      if (!page) return

      const sections = Array.from(page.querySelectorAll<HTMLElement>('[data-storey-id]'))
      if (!sections.length) return

      const threshold = Math.min(window.innerHeight * 0.38, 340)
      let nextId = Number(sections[0].dataset.storeyId)

      for (const section of sections) {
        const rect = section.getBoundingClientRect()
        const storeyId = Number(section.dataset.storeyId)
        if (!Number.isFinite(storeyId)) continue
        if (rect.top <= threshold) nextId = storeyId
        if (rect.top <= threshold && rect.bottom >= threshold) {
          nextId = storeyId
          break
        }
      }

      if (Number.isFinite(nextId) && activeStoreyIdRef.current !== nextId) {
        activeStoreyIdRef.current = nextId
        setActiveStoreyId(nextId)
      }
    }

    const scheduleActiveStoreyUpdate = () => {
      if (frame) return
      frame = window.requestAnimationFrame(updateActiveStorey)
    }

    scheduleActiveStoreyUpdate()
    window.addEventListener('scroll', scheduleActiveStoreyUpdate, { passive: true })
    window.addEventListener('resize', scheduleActiveStoreyUpdate)
    return () => {
      if (frame) window.cancelAnimationFrame(frame)
      window.removeEventListener('scroll', scheduleActiveStoreyUpdate)
      window.removeEventListener('resize', scheduleActiveStoreyUpdate)
    }
  }, [storeys.length])

  if (view === 'official' && !editMode) {
    if (storeysQuery.isLoading) {
      return (
        <LoadingState
          description="Preparing the tower."
          label="Loading tower"
          variant="page"
        />
      )
    }
    if (storeysQuery.isError) {
      return <ErrorState title="Could not load tower" description={storeysQuery.error.message} />
    }
    if (!storeys.length) {
      return <EmptyState title="No tower available" description="Publish storeys to start the climb." />
    }
  }

  return (
    <div className="tower-page-shell" ref={pageRef}>
      <div className="tower-sky" aria-hidden="true">
        <motion.span className="tower-sun" style={{ y: sunY }}>
          <span className="tower-sun-core" />
          <span className="tower-sun-flare" />
        </motion.span>
        <motion.span className="tower-moon" style={{ y: moonY }}>
          <span className="tower-moon-crater tower-moon-crater--a" />
          <span className="tower-moon-crater tower-moon-crater--b" />
          <span className="tower-moon-crater tower-moon-crater--c" />
        </motion.span>
        <motion.div className="tower-starfield tower-starfield--far" style={{ y: starsFarY }} />
        <div className="tower-starfield tower-starfield--near" />
      </div>

      <SkyClock
        timeOfDay={timeOfDay}
        onScrub={handleScrub}
        running={running}
        onToggleRunning={toggleRunning}
        phaseLabel={phaseLabel}
      />

      {editMode ? (
        // Edit mode keeps only the living sky + clock; the editor takes the rest.
        editDesignId !== null ? (
          <InTowerEditor designId={editDesignId} onExit={exitEdit} />
        ) : (
          <EmptyState
            title="No tower to edit"
            description="Raise your tower first, then come back to design it."
          />
        )
      ) : (
        <>
          <TowerControls view={view} onViewChange={setView} />

          {view === 'official' && activeStorey ? (
            <aside className="tower-storey-dock" aria-label="Current storey overview">
              <StoreyOverview
                key={activeStorey.id}
                storey={activeStorey}
                title={storeyTitle(activeStorey)}
                progress={activeStorey.level_completion?.value ?? 0}
              />
            </aside>
          ) : null}

          {view === 'official' && activeStorey ? (
            <aside className="tower-door-dock" aria-label="Selected door controls">
              {doorOverviewStoreyId ? <DoorOverview storeyId={doorOverviewStoreyId} /> : null}
              <TowerActionButton />
            </aside>
          ) : null}

          {/* Far + mid clouds sit BEHIND the tower as depth. */}
          <div className="tower-cloudfield tower-cloudfield--back" aria-hidden="true">
            {(['far', 'mid'] as const).map(renderCloudLayer)}
          </div>

          <h1 className="sr-only">{view === 'mine' ? 'Your Tower' : 'The Arcane Spire'}</h1>
          <section
            className="tower-stage-grid"
            aria-label={view === 'mine' ? 'Your Tower' : 'The Arcane Spire storeys'}
          >
            {view === 'mine' ? (
              <PrivateTowerStack />
            ) : (
              <TowerStoreys storeys={storeys} mountedCount={mountedCount} onGrow={growTower} />
            )}
          </section>

          {/* Near clouds drift in FRONT of the tower so the sky isn't all hidden behind it. */}
          <div className="tower-cloudfield tower-cloudfield--front" aria-hidden="true">
            {(['near'] as const).map(renderCloudLayer)}
          </div>

          {/* Companion sprite - must stay a direct child of the page shell. */}
          {activeCharacter ? <TowerCharacter character={activeCharacter} /> : null}
        </>
      )}
    </div>
  )
}
