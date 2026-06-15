import { useEffect, useRef, type RefObject } from 'react'

import { clamp } from '@/features/tower-map/towerLayoutRandom'
import type {
  CharacterDefinition,
  MoveName,
  SpriteAnimation,
  SpriteAnimatorHandle,
} from '@/shared/sprites/types'

/**
 * Click-driven character movement on the tower page.
 *
 * The character lives in stage-grid coordinates (document space inside
 * `.tower-stage-grid`, the layer's parent), so a grounded character scrolls
 * glued to its landing ledge with zero per-scroll work. All position writes are
 * imperative transforms - no React re-renders while moving.
 *
 * Movement rules:
 * - Click on the current ledge -> walk along it.
 * - Click anywhere else -> take_off -> fly straight there; dive (fly sheet
 *   tilted nose-down) when the target is well below.
 * - Arrive on a ledge -> land -> idle; arrive in open air -> float.
 * - Click farther than the teleport distance -> fade out, reappear there.
 * - While idle, one-shot "random" fidget sheets play on a randomized timer.
 */

const LEDGE_INSET_PX = 14 // fallback inset for CSS-painted landing ends
const WALK_BAND_PX = 48 // click this close (vertically) to a ledge targets it
const RUN_DISTANCE_PX = 220 // ground moves longer than this sprint instead of walking
const ARRIVE_PX = 6
const FLIP_DEADZONE_PX = 4 // no facing flips on sub-pixel jitter near arrival
const DIVE_DROP_PX = 120 // remaining drop that swaps fly -> dive
const DIVE_TILT_DEG = 38
const TILT_EASE_DEG_PER_S = 220
const TAKEOFF_LIFT_SPEED = 150 // px/s straight up while the lift-off frames play
const LAND_HOVER_PX = 60 // braking height above the ledge before the vertical drop
const LAND_FALL_SPEED = 150 // px/s straight down while the drop frames play
const TELEPORT_PHASE_MS = 200 // must cover the CSS fade duration
const RANDOM_DELAY_MIN_MS = 6000
const RANDOM_DELAY_MAX_MS = 14000

const INTERACTIVE_SELECTOR =
  'button, a, input, select, textarea, [role="button"], [role="slider"], .sky-clock, .tower-artifact-dock, .tower-zoom-control'

type Ledge = { el: HTMLElement; left: number; right: number; y: number }
type Target = { x: number; y: number; ledge: Ledge | null }
type Mode = 'hidden' | 'idle' | 'walk' | 'take_off' | 'air' | 'land' | 'float' | 'teleport'
/** Resting state kept across effect re-inits (e.g. the active character swaps
 *  from the bundled fallback to the loaded descriptor) so the companion stays
 *  put instead of teleporting back to the base ledge. */
type Persisted = { pos: { x: number; y: number }; anchor: { el: HTMLElement; xFraction: number } | null }

/** Looping moves substitute a simpler sheet when theirs is missing;
 *  transitions (take_off/land) just skip instead. */
const LOOP_FALLBACKS: Partial<Record<MoveName, MoveName>> = {
  run: 'walk',
  float: 'fly',
  dive: 'fly',
}

function resolveSprite(def: CharacterDefinition, moveName: MoveName): SpriteAnimation | null {
  let current: MoveName | undefined = moveName
  while (current) {
    const sprite = def.sprites[current]
    if (sprite) return sprite
    current = LOOP_FALLBACKS[current]
  }
  return null
}

export function useCharacterController({
  character,
  layerRef,
  bodyRef,
  spriteRef,
}: {
  character: CharacterDefinition
  layerRef: RefObject<HTMLDivElement | null>
  bodyRef: RefObject<HTMLDivElement | null>
  spriteRef: RefObject<SpriteAnimatorHandle | null>
}) {
  // Survives effect re-runs (refs persist for the component's lifetime), so a
  // character-identity change re-mounts the controller without losing position.
  const persistedRef = useRef<Persisted | null>(null)

  useEffect(() => {
    const layer = layerRef.current
    const bodyEl = bodyRef.current
    const shellEl = layer?.parentElement
    if (!layer || !bodyEl || !shellEl) return
    // Non-null aliases: hoisted inner functions don't inherit the narrowing.
    const body: HTMLDivElement = bodyEl
    const shell: HTMLElement = shellEl

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const metrics = character.metrics
    const boxW = character.sprites.idle.frameWidth * metrics.scale
    const boxH = character.sprites.idle.frameHeight * metrics.scale
    const footPx = metrics.footOffset * metrics.scale
    // Two-phase landing (brake above the ledge, then drop straight down)
    // needs both the sheet and the frame split; otherwise land standing.
    const landApproach = character.sprites.land !== undefined && metrics.landFallFrame !== undefined

    let disposed = false
    let pos = { x: 0, y: 0 }
    let target: Target | null = null
    let mode: Mode = 'hidden'
    let currentSheet: SpriteAnimation | null = character.sprites.idle
    let anchor: { el: HTMLElement; xFraction: number } | null = null
    let facingLeft = false
    let tilt = 0
    let tiltGoal = 0
    let randomTimer = 0
    let teleportTimer = 0
    let pointerDown: { x: number; y: number } | null = null
    let running = false // gait for the current ground move, decided at click time

    function setMove(next: MoveName, opts?: { onComplete?: () => void }) {
      const sheet = resolveSprite(character, next)
      if (!sheet) {
        // Missing transition sheet (take_off/land on other characters) = skip.
        opts?.onComplete?.()
        return
      }
      // fly ->" dive resolve to the same sheet - don't restart its frames.
      if (sheet === currentSheet && sheet.loop && !opts?.onComplete) return
      currentSheet = sheet
      spriteRef.current?.setAnimation(sheet, opts)
    }

    function setFacing(dx: number) {
      if (Math.abs(dx) <= FLIP_DEADZONE_PX) return
      const next = dx < 0
      if (next !== facingLeft) {
        facingLeft = next
        spriteRef.current?.setFlipX(next)
      }
    }

    function paint() {
      body.style.transform = `translate3d(${pos.x - boxW / 2}px, ${pos.y - boxH + footPx}px, 0) rotate(${
        facingLeft ? -tilt : tilt
      }deg)`
    }

    function numberData(el: HTMLElement, name: string): number | null {
      const value = el.dataset[name]
      if (value === undefined) return null
      const parsed = Number(value)
      return Number.isFinite(parsed) ? parsed : null
    }

    function measureAnchorLedge(el: HTMLElement, shellRect: DOMRect): Ledge | null {
      const rect = el.getBoundingClientRect()
      if (rect.width === 0) return null

      const viewBoxWidth = numberData(el, 'viewboxWidth')
      const viewBoxHeight = numberData(el, 'viewboxHeight')
      const viewBoxX = numberData(el, 'viewboxX') ?? 0
      const viewBoxY = numberData(el, 'viewboxY') ?? 0
      const x1 = numberData(el, 'walkRailX1')
      const y1 = numberData(el, 'walkRailY1')
      const x2 = numberData(el, 'walkRailX2')
      const y2 = numberData(el, 'walkRailY2')
      if (!viewBoxWidth || !viewBoxHeight || x1 === null || y1 === null || x2 === null || y2 === null) {
        return null
      }

      return {
        el,
        left: rect.left - shellRect.left + ((Math.min(x1, x2) - viewBoxX) / viewBoxWidth) * rect.width,
        right: rect.left - shellRect.left + ((Math.max(x1, x2) - viewBoxX) / viewBoxWidth) * rect.width,
        y: rect.top - shellRect.top + ((((y1 + y2) / 2) - viewBoxY) / viewBoxHeight) * rect.height,
      }
    }

    // Prefer authored landing anchors from tower-piece descriptors. The CSS
    // separator scan below is an explicit migration shim until every rendered
    // landing carries a walk_rail anchor.
    function measureLedge(el: HTMLElement, shellRect: DOMRect): Ledge | null {
      const anchored = measureAnchorLedge(el, shellRect)
      if (anchored) return anchored

      // Fallback: use the CSS separator's top edge when authored anchor data is absent.
      const rect = el.getBoundingClientRect()
      if (rect.width === 0) return null
      const railTop = Number.parseFloat(window.getComputedStyle(el, '::before').top)
      return {
        el,
        left: rect.left - shellRect.left + LEDGE_INSET_PX,
        right: rect.right - shellRect.left - LEDGE_INSET_PX,
        y: rect.top - shellRect.top + (Number.isFinite(railTop) ? railTop : 0),
      }
    }

    function scanLedges(): Ledge[] {
      const shellRect = shell.getBoundingClientRect()
      const anchoredNodes = shell.querySelectorAll<HTMLElement>('.tower-landing[data-walk-rail-x1]')
      const nodes = anchoredNodes.length
        ? anchoredNodes
        : shell.querySelectorAll<HTMLElement>('.tower-section-separator')
      const ledges: Ledge[] = []
      for (const el of Array.from(nodes)) {
        const ledge = measureLedge(el, shellRect)
        if (ledge) ledges.push(ledge)
      }
      return ledges
    }

    function ledgeAt(point: { x: number; y: number }): Ledge | null {
      let best: Ledge | null = null
      let bestDist = WALK_BAND_PX
      for (const ledge of scanLedges()) {
        if (point.x < ledge.left - LEDGE_INSET_PX || point.x > ledge.right + LEDGE_INSET_PX) continue
        const dist = Math.abs(point.y - ledge.y)
        if (dist <= bestDist) {
          best = ledge
          bestDist = dist
        }
      }
      return best
    }

    // -- Idle fidgets: one-shot random sheets on a randomized timer ---------
    function cancelRandom() {
      if (randomTimer) {
        window.clearTimeout(randomTimer)
        randomTimer = 0
      }
    }

    function scheduleRandom() {
      cancelRandom()
      if (reducedMotion || !character.randoms.length) return
      const delay = RANDOM_DELAY_MIN_MS + Math.random() * (RANDOM_DELAY_MAX_MS - RANDOM_DELAY_MIN_MS)
      randomTimer = window.setTimeout(() => {
        randomTimer = 0
        if (disposed || mode !== 'idle') return
        const fidget = character.randoms[Math.floor(Math.random() * character.randoms.length)]
        currentSheet = fidget
        spriteRef.current?.setAnimation(fidget, {
          onComplete: () => {
            if (disposed || mode !== 'idle') return
            setMove('idle')
            scheduleRandom()
          },
        })
      }, delay)
    }

    // Snapshot the current resting state so a controller re-init can restore it.
    function remember() {
      persistedRef.current = {
        pos: { x: pos.x, y: pos.y },
        anchor: anchor ? { el: anchor.el, xFraction: anchor.xFraction } : null,
      }
    }

    function settle(ledge: Ledge) {
      anchor = {
        el: ledge.el,
        xFraction: clamp((pos.x - ledge.left) / Math.max(1, ledge.right - ledge.left), 0, 1),
      }
      mode = 'idle'
      tiltGoal = 0
      setMove('idle')
      scheduleRandom()
      remember()
    }

    function arriveAirborne() {
      const dest = target
      const ledge = dest?.ledge ?? null
      tiltGoal = 0
      if (!dest || !ledge) {
        target = null
        mode = 'float'
        setMove('float')
        remember()
        return
      }
      mode = 'land'
      // Two-phase landing keeps the target so the tick can brake above the
      // ledge and drop onto it; otherwise the sheet plays standing in place.
      if (!landApproach) target = null
      setMove('land', {
        onComplete: () => {
          if (disposed || mode !== 'land') return
          // The drop is tuned to touch down before the sheet ends, but never
          // trust the timing - snap the last few px on completion.
          pos = { x: dest.x, y: dest.y }
          target = null
          paint()
          settle(ledge)
        },
      })
    }

    function startTeleport(destination: Target) {
      cancelRandom()
      mode = 'teleport'
      target = null
      anchor = null
      body.classList.add('is-teleporting')
      window.clearTimeout(teleportTimer)
      teleportTimer = window.setTimeout(() => {
        if (disposed) return
        setFacing(destination.x - pos.x)
        pos = { x: destination.x, y: destination.y }
        tilt = 0
        tiltGoal = 0
        paint()
        if (destination.ledge) {
          settle(destination.ledge)
        } else {
          mode = 'float'
          setMove('float')
          remember()
        }
        body.classList.remove('is-teleporting')
      }, TELEPORT_PHASE_MS)
    }

    // -- Spawn + re-anchor ---------------------------------------------------
    function trySpawn() {
      const ledges = scanLedges()
      if (!ledges.length) return
      const base = ledges.find((ledge) => ledge.el.classList.contains('is-base')) ?? ledges[0]
      pos = { x: (base.left + base.right) / 2, y: base.y }
      anchor = { el: base.el, xFraction: 0.5 }
      mode = 'idle'
      setMove('idle')
      paint()
      body.classList.remove('is-unspawned')
      scheduleRandom()
      remember()
    }

    // Re-init after a character swap: drop the companion back where he was
    // (re-measured against the live ledge) instead of spawning at the base.
    // Returns false when there's nothing to restore (first mount).
    function restoreSpawn(): boolean {
      const saved = persistedRef.current
      if (!saved) return false
      const grounded = saved.anchor && saved.anchor.el.isConnected ? saved.anchor : null
      anchor = grounded
      pos = { x: saved.pos.x, y: saved.pos.y }
      // Mid-move states don't survive a re-init; settle to a resting pose.
      mode = grounded ? 'idle' : 'float'
      if (grounded) {
        const ledge = measureLedge(grounded.el, shell.getBoundingClientRect())
        if (ledge) {
          pos = { x: ledge.left + grounded.xFraction * (ledge.right - ledge.left), y: ledge.y }
        }
      }
      setMove(mode === 'float' ? 'float' : 'idle')
      paint()
      body.classList.remove('is-unspawned')
      if (mode === 'idle') scheduleRandom()
      remember()
      return true
    }

    // Layout shifts (lazy storey mounts, viewport resize) move the landings;
    // a grounded character re-derives its position from the stored anchor.
    function reanchor() {
      if (disposed) return
      if (mode === 'hidden') {
        trySpawn()
        return
      }
      if (mode !== 'idle' || !anchor) return
      if (!anchor.el.isConnected) {
        const ledges = scanLedges()
        if (!ledges.length) return
        let best = ledges[0]
        for (const ledge of ledges) {
          if (Math.abs(ledge.y - pos.y) < Math.abs(best.y - pos.y)) best = ledge
        }
        anchor = { el: best.el, xFraction: 0.5 }
      }
      const ledge = measureLedge(anchor.el, shell.getBoundingClientRect())
      if (!ledge) return
      pos = {
        x: ledge.left + anchor.xFraction * (ledge.right - ledge.left),
        y: ledge.y,
      }
      paint()
    }

    // -- Click handling ------------------------------------------------------
    function onPointerDown(e: PointerEvent) {
      pointerDown = { x: e.clientX, y: e.clientY }
    }

    function onClick(e: MouseEvent) {
      if (disposed || mode === 'hidden' || mode === 'teleport') return
      const origin = e.target as Element | null
      if (origin?.closest(INTERACTIVE_SELECTOR)) return
      if (window.getSelection()?.toString()) return
      if (pointerDown && (Math.abs(e.clientX - pointerDown.x) > 5 || Math.abs(e.clientY - pointerDown.y) > 5)) {
        return // drag, not a click
      }

      const shellRect = shell.getBoundingClientRect()
      const point = { x: e.clientX - shellRect.left, y: e.clientY - shellRect.top }
      const ledge = ledgeAt(point)
      const next: Target = ledge
        ? { x: clamp(point.x, ledge.left, ledge.right), y: ledge.y, ledge }
        : { x: point.x, y: point.y, ledge: null }

      cancelRandom()

      if (reducedMotion) {
        setFacing(next.x - pos.x)
        pos = { x: next.x, y: next.y }
        tilt = 0
        tiltGoal = 0
        paint()
        if (ledge) {
          settle(ledge)
        } else {
          mode = 'float'
          setMove('float')
        }
        return
      }

      const distance = Math.hypot(next.x - pos.x, next.y - pos.y)
      const teleportDistance = metrics.teleportDistance ?? Math.max(2400, window.innerHeight * 2)
      if (distance > teleportDistance) {
        startTeleport(next)
        return
      }

      target = next
      const grounded = mode === 'idle' || mode === 'walk'
      if (grounded) {
        if (ledge && anchor && ledge.el === anchor.el) {
          // Gait is chosen once, from a standstill; retargets mid-stride keep
          // the current gait so he never flips between run and walk.
          if (mode !== 'walk') running = Math.abs(next.x - pos.x) > RUN_DISTANCE_PX
          mode = 'walk'
        } else {
          anchor = null
          mode = 'take_off'
          setMove('take_off', {
            onComplete: () => {
              if (!disposed && mode === 'take_off') mode = 'air'
            },
          })
        }
      } else if (mode !== 'take_off') {
        mode = 'air' // airborne retarget - tick picks fly/dive
      }
    }

    // -- Frame loop ----------------------------------------------------------
    let raf = 0
    let last = performance.now()
    function tick(now: number) {
      raf = requestAnimationFrame(tick)
      const dt = Math.min(0.1, (now - last) / 1000)
      last = now
      if (disposed) return

      if (tilt !== tiltGoal) {
        const step = TILT_EASE_DEG_PER_S * dt
        tilt = tilt < tiltGoal ? Math.min(tiltGoal, tilt + step) : Math.max(tiltGoal, tilt - step)
        paint()
      }

      if (!target) return

      if (mode === 'land') {
        // Braking flare frames hold at the hover point; from the fall frame
        // the descent is straight down onto the ledge (touchdown mid-sheet,
        // the settle frames play grounded until onComplete).
        const falling =
          currentSheet !== character.sprites.land ||
          (spriteRef.current?.getFrame() ?? Infinity) >= (metrics.landFallFrame ?? 0)
        const step = (falling ? LAND_FALL_SPEED : metrics.flySpeed) * dt
        pos.x += clamp(target.x - pos.x, -step, step)
        if (falling) pos.y = Math.min(target.y, pos.y + step)
        paint()
        return
      }

      if (mode === 'walk') {
        const dx = target.x - pos.x
        setFacing(dx)
        setMove(running ? 'run' : 'walk')
        const step = (running ? (metrics.runSpeed ?? metrics.walkSpeed * 2) : metrics.walkSpeed) * dt
        if (Math.abs(dx) <= Math.max(step, ARRIVE_PX)) {
          pos.x = target.x
          const ledge = target.ledge
          target = null
          paint()
          if (ledge) settle(ledge)
        } else {
          pos.x += Math.sign(dx) * step
          paint()
        }
        return
      }

      if (mode === 'take_off' || mode === 'air') {
        const dx = target.x - pos.x
        setFacing(dx)
        // Lift phase: while the take_off sheet still shows the grounded
        // crouch/wing-unfurl frames, rise straight up instead of seeking.
        if (
          mode === 'take_off' &&
          metrics.takeOffAirborneFrame !== undefined &&
          currentSheet === character.sprites.take_off &&
          (spriteRef.current?.getFrame() ?? Infinity) < metrics.takeOffAirborneFrame
        ) {
          pos.y -= (metrics.takeOffLiftSpeed ?? TAKEOFF_LIFT_SPEED) * dt
          paint()
          return
        }
        // Ledge approaches aim at the hover point above the target; the
        // landing branch covers the final drop.
        const aimY = target.ledge && landApproach ? target.y - LAND_HOVER_PX : target.y
        const dy = aimY - pos.y
        const distance = Math.hypot(dx, dy)
        const step = metrics.flySpeed * dt
        if (mode === 'air') {
          if (dy > DIVE_DROP_PX) {
            setMove('dive')
            // No dive sheet -> reuse fly tilted nose-down toward the travel side.
            tiltGoal = character.sprites.dive ? 0 : DIVE_TILT_DEG
          } else {
            setMove('fly')
            tiltGoal = 0
          }
        }
        if (distance <= Math.max(step, ARRIVE_PX)) {
          pos = { x: target.x, y: aimY }
          paint()
          arriveAirborne()
        } else {
          pos = { x: pos.x + (dx / distance) * step, y: pos.y + (dy / distance) * step }
          paint()
        }
      }
    }

    const resizeObserver = new ResizeObserver(reanchor)
    resizeObserver.observe(shell)
    shell.addEventListener('pointerdown', onPointerDown)
    shell.addEventListener('click', onClick)
    if (!restoreSpawn()) trySpawn()
    raf = requestAnimationFrame(tick)

    return () => {
      disposed = true
      cancelAnimationFrame(raf)
      resizeObserver.disconnect()
      shell.removeEventListener('pointerdown', onPointerDown)
      shell.removeEventListener('click', onClick)
      cancelRandom()
      window.clearTimeout(teleportTimer)
    }
  }, [character, layerRef, bodyRef, spriteRef])
}
