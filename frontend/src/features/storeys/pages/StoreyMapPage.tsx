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

import { storeysApi } from '@/features/storeys/api/storeysApi'
import { DoorOverview } from '@/features/storeys/components/DoorOverview'
import { StoreyOverview, StoreyPracticeHub } from '@/features/storeys/components/StoreyPracticeHub'
import { SkyClock } from '@/features/storeys/components/SkyClock'
import { TowerActionButton } from '@/features/storeys/components/TowerActionButton'
import { useTowerSelection } from '@/features/storeys/hooks/useTowerSelection'
import { computeSky } from '@/features/storeys/sky/useTowerSky'
import { clamp, lerp, mulberry32 } from '@/features/storeys/towerRandom'
import type { LearningStorey } from '@/features/storeys/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { readPreference, writePreference } from '@/shared/utils/persistentState'

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
// position come from CSS per instance.
const CLOUD_SHAPES = {
  a: {
    viewBox: '0 0 120 54',
    d: 'M14 47 C5 47 1 40 4 33 C6 27 13 26 17 28 C16 17 27 10 36 14 C40 5 52 3 59 9 C65 2 77 4 80 13 C90 9 100 14 100 23 C110 22 117 29 114 37 C112 43 105 47 97 47 Z',
  },
  b: {
    viewBox: '0 0 130 44',
    d: 'M9 38 C2 38 0 32 3 28 C5 24 12 24 15 26 C16 18 26 16 32 20 C36 12 49 12 53 19 C60 13 73 14 76 21 C84 16 97 18 99 24 C109 22 122 25 123 31 C124 36 117 38 110 38 Z',
  },
  c: {
    viewBox: '0 0 116 64',
    d: 'M16 56 C6 56 1 47 6 39 C2 31 10 23 19 27 C20 14 35 8 45 16 C49 4 66 4 72 15 C79 6 94 9 95 21 C107 18 116 27 110 36 C120 38 119 51 109 53 C110 57 101 56 95 56 Z',
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
  far: { width: [18, 25], opacity: [0.08, 0.14] },
  mid: { width: [13, 20], opacity: [0.13, 0.23] },
  near: { width: [10, 16], opacity: [0.18, 0.32] },
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
        <StoreyPracticeHub
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

export function StoreyMapPage() {
  const [searchParams] = useSearchParams()
  const storeyParam = searchParams.get('storey')
  const focusedStoreyId = storeyParam ? Number(storeyParam) : null
  const storeysQuery = useQuery({
    queryKey: queryKeys.storeys,
    queryFn: storeysApi.listStoreys,
    staleTime: 5 * 60 * 1000,
  })

  const storeys = useMemo(() => storeysQuery.data ?? [], [storeysQuery.data])
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

  // ── Living sky ──────────────────────────────────────────────────────────
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

  // ── Scroll-linked parallax (composed on top of the time-driven positions) ──
  const { scrollY, scrollYProgress } = useScroll()
  const skyProgress = useSpring(scrollYProgress, { stiffness: 70, damping: 24, mass: 0.5 })
  const moonY = useTransform(skyProgress, [0, 1], ['0px', '-90px'])
  const sunY = useTransform(skyProgress, [0, 1], ['0px', '-60px'])
  const starsFarY = useTransform(skyProgress, [0, 1], ['0px', '-45px'])

  const cloudSpring = { stiffness: 60, damping: 22, mass: 0.4 }
  const cloudFarY = useSpring(useTransform(scrollY, (v) => v * 0.12), cloudSpring)
  const cloudMidY = useSpring(useTransform(scrollY, (v) => v * -0.02), cloudSpring)
  const cloudNearY = useSpring(useTransform(scrollY, (v) => v * -0.12), cloudSpring)
  const cloudLayerY = { far: cloudFarY, mid: cloudMidY, near: cloudNearY }

  const renderCloudLayer = (layer: CloudLayer) => (
    <motion.div className="tower-cloud-layer" key={layer} style={{ y: cloudLayerY[layer] }}>
      {cloudField
        .filter((cloud) => cloud.layer === layer)
        .map((cloud) => (
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
  )

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

  useEffect(() => {
    if (!storeys.length) return
    setActiveStoreyId((current) => {
      if (current && storeys.some((storey) => storey.id === current)) return current
      return storeys[0]?.id ?? null
    })
  }, [storeys])

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

      if (Number.isFinite(nextId)) setActiveStoreyId(nextId)
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

      {activeStorey ? (
        <aside className="tower-storey-dock" aria-label="Current storey overview">
          <StoreyOverview
            key={activeStorey.id}
            storey={activeStorey}
            title={storeyTitle(activeStorey)}
            progress={activeStorey.practice_completion?.value ?? 0}
          />
        </aside>
      ) : null}

      {activeStorey ? (
        <aside className="tower-door-dock" aria-label="Selected door controls">
          {doorOverviewStoreyId ? <DoorOverview storeyId={doorOverviewStoreyId} /> : null}
          <TowerActionButton />
        </aside>
      ) : null}

      {/* Far + mid clouds sit BEHIND the tower as depth. */}
      <div className="tower-cloudfield tower-cloudfield--back" aria-hidden="true">
        {(['far', 'mid'] as const).map(renderCloudLayer)}
      </div>

      <h1 className="sr-only">Git Tower</h1>
      <section className="tower-stage-grid" aria-label="Git Tower storeys">
        <TowerStoreys storeys={storeys} mountedCount={mountedCount} onGrow={growTower} />
      </section>

      {/* Near clouds drift in FRONT of the tower so the sky isn't all hidden behind it. */}
      <div className="tower-cloudfield tower-cloudfield--front" aria-hidden="true">
        {(['near'] as const).map(renderCloudLayer)}
      </div>
    </div>
  )
}
