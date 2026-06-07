import { useEffect, useMemo, type CSSProperties } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, useScroll, useSpring, useTransform } from 'motion/react'
import { useSearchParams } from 'react-router-dom'

import { storeysApi } from '@/features/storeys/api/storeysApi'
import { StoreyPracticeHub } from '@/features/storeys/components/StoreyPracticeHub'
import type { LearningStorey } from '@/features/storeys/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { EmptyState } from '@/shared/components/EmptyState'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

function isFoundationsStorey(storey: LearningStorey) {
  return storey.number === 1 || storey.slug === 'creating-inspecting-repositories'
}

function storeyTitle(storey: LearningStorey) {
  return isFoundationsStorey(storey) ? 'Foundations' : storey.title
}

// Crisp-edged puffy clouds. Three silhouettes for variety; transparency, size and
// position come from CSS per instance.
const CLOUD_SHAPES = {
  // wide, balanced cumulus
  a: {
    viewBox: '0 0 120 54',
    d: 'M14 47 C5 47 1 40 4 33 C6 27 13 26 17 28 C16 17 27 10 36 14 C40 5 52 3 59 9 C65 2 77 4 80 13 C90 9 100 14 100 23 C110 22 117 29 114 37 C112 43 105 47 97 47 Z',
  },
  // long, low and flat
  b: {
    viewBox: '0 0 130 44',
    d: 'M9 38 C2 38 0 32 3 28 C5 24 12 24 15 26 C16 18 26 16 32 20 C36 12 49 12 53 19 C60 13 73 14 76 21 C84 16 97 18 99 24 C109 22 122 25 123 31 C124 36 117 38 110 38 Z',
  },
  // tall, puffy multi-lobe
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

// Depth bands, far → near. Each gets its own size/opacity range and its own scroll
// speed, so the field reads as 3D atmosphere rather than a flat sticker.
type CloudLayer = 'far' | 'mid' | 'near'

const CLOUD_VARIANTS: CloudVariant[] = ['a', 'b', 'c']
const LAYER_STYLE: Record<CloudLayer, { width: [number, number]; opacity: [number, number] }> = {
  far: { width: [18, 25], opacity: [0.08, 0.14] },
  mid: { width: [13, 20], opacity: [0.13, 0.23] },
  // `near` renders in FRONT of the tower, so keep it light enough to read through.
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

const clamp = (value: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, value))
const lerp = (a: number, b: number, t: number) => a + (b - a) * t

// Tiny deterministic PRNG so the layout is generated once and stays put across
// renders (no reshuffle / flicker) while still looking hand-scattered.
function mulberry32(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

// Build a cloud field that scales with the tower: ~1.6 clouds per storey, stratified
// down the full height so they never clump and never leave gaps. Add storeys and they
// get their own clouds for free — nothing here is hand-placed to a fixed viewport.
function buildCloudField(floors: number): SeededCloud[] {
  const count = Math.max(4, Math.round(floors * 0.9))
  const rand = mulberry32(0x7a9c13)
  return Array.from({ length: count }, (_, i): SeededCloud => {
    const layer = i % 5 === 0 ? 'far' : i % 5 === 3 ? 'mid' : 'near'
    const range = LAYER_STYLE[layer]
    // One cloud per evenly spaced band + sub-band jitter → scattered but gap-free.
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

  // Moon + stars sit on the fixed backdrop and ease with normalised progress.
  const { scrollY, scrollYProgress } = useScroll()
  const skyProgress = useSpring(scrollYProgress, { stiffness: 70, damping: 24, mass: 0.5 })
  const moonY = useTransform(skyProgress, [0, 1], ['0px', '-130px'])
  const starsFarY = useTransform(skyProgress, [0, 1], ['0px', '-45px'])

  // Clouds live in the scrolling tower, so they already travel with the content.
  // These per-layer offsets are driven by raw scroll *pixels* (not progress) to add
  // depth on top — far clouds lag, near clouds lead — at a drift speed that stays
  // the same however tall the tower grows. Scroll up and it all reverses.
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

  useEffect(() => {
    if (!focusedStoreyId || !Number.isFinite(focusedStoreyId) || !storeys.length) return
    window.requestAnimationFrame(() => {
      document.querySelector(`[data-storey-id="${focusedStoreyId}"]`)?.scrollIntoView({
        block: 'start',
        behavior: 'smooth',
      })
    })
  }, [focusedStoreyId, storeys])

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
    <div className="tower-page-shell">
      <div className="tower-sky" aria-hidden="true">
        <motion.span className="tower-moon" style={{ y: moonY }}>
          <span className="tower-moon-crater tower-moon-crater--a" />
          <span className="tower-moon-crater tower-moon-crater--b" />
          <span className="tower-moon-crater tower-moon-crater--c" />
        </motion.span>
        <motion.div className="tower-starfield tower-starfield--far" style={{ y: starsFarY }} />
        <div className="tower-starfield tower-starfield--near" />
      </div>
      {/* Far + mid clouds sit BEHIND the tower as depth. */}
      <div className="tower-cloudfield tower-cloudfield--back" aria-hidden="true">
        {(['far', 'mid'] as const).map(renderCloudLayer)}
      </div>
      <h1 className="sr-only">Git Tower</h1>
      <section className="tower-stage-grid" aria-label="Git Tower storeys">
        <div className="tower-stack-column">
          {storeys.map((storey, index) => (
            <StoreyPracticeHub
              displayTitle={storeyTitle(storey)}
              isFirst={index === 0}
              isLast={index === storeys.length - 1}
              key={storey.id}
              sequenceIndex={index}
              storey={storey}
            />
          ))}
        </div>
      </section>
      {/* Near clouds drift in FRONT of the tower so the sky isn't all hidden behind it. */}
      <div className="tower-cloudfield tower-cloudfield--front" aria-hidden="true">
        {(['near'] as const).map(renderCloudLayer)}
      </div>
    </div>
  )
}
