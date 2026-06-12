# Plan: Character Animation System — Blue on the Tower

Click-driven character movement on /tower: Blue walks the separator ledges, takes off and flies on outside clicks, flaps upward / dives downward, teleports when the target is too far. Built generically so every future character reuses the same controller.

## Current state (verified)

- Sprite engine exists: `frontend/src/shared/sprites/SpriteAnimator.tsx` (rAF stepper, background-position frames, imperative handle `play/pause/goToFrame/setAnimation/setFlipX`, honors reduced motion). **No completion callback for non-looping sheets — needed for transitions.**
- Blue sheets on disk (`frontend/src/assets/sprites/character/blue/`): `idle, walk, run, fly, float, flap` — all 1280×1280, 5×5 grid, 256×256, 25 frames. **`take_off`, `land` don't exist yet** (planned). **`dive` will not get a sheet: it's `fly` rotated downward** (user decision).
- `characters.ts` still imports `@/assets/sprites/character1/*.png` which were **deleted from the worktree → build is broken**; `CharacterShowcase.tsx` (home hub) consumes it. Migration to blue is required regardless.
- Tower page: `frontend/src/features/storeys/pages/StoreyMapPage.tsx`, content in `.tower-stage-grid` (z-1), parallax clouds z-0/z-2, fixed docks z-34. Separators are plain document-flow elements: `.tower-section-separator` (ledge backplate at **1.22rem** from top, globals.css ~2973) and `.tower-tome-separator` (ledge at **1.93rem**, ~3170). Storeys lazy-mount via IntersectionObserver; page scrolls normally. Clicks today only on door/tome buttons.

## Architecture decisions

1. **Placement — document-space layer.** `.tower-character-layer` (`position:absolute; inset:0; pointer-events:none; z-index:3`) as a direct child of `.tower-page-shell`, after the front cloudfield. Grounded character scrolls glued to its separator for free (no per-scroll JS); airborne it floats at a world position above the stage, behind the docks. Click → shell coords: `clientX/Y - shell.getBoundingClientRect().left/top`. Character div moved imperatively via `transform: translate3d(x − w/2, y − h + footOffset, 0)` — no React re-renders per frame.

2. **State machine.** Walking is only along the *current* separator; clicking a different separator (or open air) = take_off → fly. Click-while-moving always retargets (no queue).

   | Current | Event | Next |
   |---|---|---|
   | idle / walk | click in current separator's walk band (rect ±3rem vertically, X clamped to extent) | walk (retarget, face target) |
   | idle / walk | click elsewhere, dist ≤ teleport threshold | take_off → fly |
   | any | click, dist > teleport threshold | teleport_out → reposition → teleport_in → idle/float |
   | take_off | sheet completes (missing → instant skip) | fly |
   | airborne (fly/flap/dive) | per tick: target ≥120px above → flap; ≥120px below → dive (= fly rotated); else fly | sprite/presentation swap only |
   | airborne | arrive at separator target | land → idle (land missing → instant idle) |
   | airborne | arrive at open-air target | float (loop) |
   | float | new click | flap/dive/fly toward it |
   | any | prefers-reduced-motion | instant reposition, idle/float |

3. **Movement engine — hand-rolled rAF tween** in the controller hook (not `motion`'s `animate()`): the tick makes per-frame decisions (sprite swap, facing, arrival transitions, retarget), and this matches codebase style (SpriteAnimator, sky clock). Constants: walk 140 px/s, fly 380 px/s, arrival 6px, `flipX = dx < 0` only when `|dx| > 4px` (no flip jitter). Straight-line constant-velocity flight.

4. **Dive = rotated fly (and generic move presentation).** Each move resolves to `{ animation, rotateDeg }`. `dive` defaults to `{ sheet: fly, rotateDeg: ~40 }` tilted toward travel direction; rotation sign flips with facing. Transform order on the character wrapper: `translate3d(...) scaleX(±1) rotate(deg)` (rotation on wrapper, not inside SpriteAnimator's flip). Tilt eased in/out over ~150ms so fly↔dive doesn't snap. Dropping a real `dive.png` later = one config entry.

5. **Teleport.** Threshold `max(2400, 2 × innerHeight)` px euclidean (per-character overridable). No sheet yet → CSS effect: `.is-teleporting-out` (opacity→0, scale→0.6, 180ms), instant reposition, `.is-teleporting-in` reverse; `transitionend` + timeout fallback. Real teleport sheet later is config-only.

6. **Click capture.** One `click` listener on the shell. Bail when `e.target.closest('button, a, input, select, textarea, [role="button"], [role="slider"], .tower-storey-dock, .tower-door-dock')` matches, when text selection is non-empty, or when pointer travelled >5px between pointerdown and click (drag). Buttons keep native priority; no `preventDefault`.

7. **Genericity — `CharacterDefinition`,** consumed by the controller (never `BLUE` directly):

   ```ts
   type MoveName = 'idle'|'walk'|'run'|'fly'|'float'|'flap'|'dive'
                 | 'take_off'|'land'|'teleport_out'|'teleport_in'

   type CharacterDefinition = {
     id: string
     sprites: Partial<Record<MoveName, SpriteAnimation>> &
       Record<'idle'|'walk'|'fly', SpriteAnimation>   // required core
     metrics: { scale: number; walkSpeed: number; flySpeed: number
                footOffset: number; teleportDistance?: number }
   }
   // Loop fallbacks: run→walk, float→fly, flap→fly, dive→fly+rotate.
   // Transition fallbacks (take_off/land/teleport_*): missing sheet ⇒ zero-duration skip.
   ```

8. **Separator anchoring.** `findSeparators(shell)`: `querySelectorAll('.tower-section-separator, .tower-tome-separator')` → `{ el, walkY, minX, maxX }` with `walkY = rect.top − shellRect.top + ledgeOffset` (1.22rem / 1.93rem × root font-size), X inset ±0.75rem. Grounded anchor memory: `{ separatorEl, xFraction }` (fraction of width, resilient to resize). Re-anchor on: `ResizeObserver` on `.tower-stack-column` (covers lazy storey mounts shifting layout) + window `resize`. If `separatorEl.isConnected` is false, snap to nearest separator by Y.

9. **Reduced motion.** `matchMedia` once; when true every click = instant reposition + idle/float, transitions skipped, teleport CSS neutralized under the same media query.

10. **Spawn.** `xFraction 0.5` on the first mounted storey's base separator, idle, facing right; the ResizeObserver's first callback doubles as the spawn trigger. No idle wandering in v1.

## Controller pseudocode

```ts
function onShellClick(e) {
  if (isInteractive(e.target) || hasSelection() || wasDrag(e)) return
  const p = toShellCoords(e)
  const sep = hitSeparatorBand(p)
  const target = sep ? { x: clamp(p.x, sep.minX, sep.maxX), y: sep.walkY, sep }
                     : { x: p.x, y: p.y, sep: null }
  if (reducedMotion) return snapTo(target)
  if (dist(pos, target) > teleportDistance) return startTeleport(target)
  if (grounded) {
    if (sep?.el === anchor.el) enter('walk', target)
    else enter('take_off', target)        // → fly on complete/skip
  } else retarget(target)
}

function tick(now) {
  const dt = (now - last) / 1000; last = now
  if (state === 'walk') {
    pos.x = approach(pos.x, target.x, walkSpeed * dt); face(target.x - pos.x)
    if (atTarget()) { enter('idle'); anchor = { el: target.sep.el, xFraction: fracOf(pos.x) } }
  } else if (airborne(state)) {
    const d = sub(target, pos), step = flySpeed * dt
    pos = mag(d) <= step ? { ...target } : add(pos, scale(norm(d), step))
    face(d.x)
    setMove(d.y < -120 ? 'flap' : d.y > 120 ? 'dive' : 'fly')  // dive = fly + rotate
    if (atTarget()) target.sep ? enter('land') : enter('float')
  }
  applyTransform(pos, rotateDeg)           // imperative translate3d + rotate
  raf = requestAnimationFrame(tick)
}
```

## Implementation steps

1. **Sprite engine: completion callbacks + presentation.**
   - `frontend/src/shared/sprites/types.ts`: add `MoveName`, `CharacterDefinition`, fallback map; handle becomes `setAnimation(anim, opts?: { onComplete?: () => void })`.
   - `frontend/src/shared/sprites/SpriteAnimator.tsx`: hold callback in a ref; fire+clear it in the non-loop terminal branch (currently lines 111-112). Optional declarative `onAnimationEnd` prop.
2. **Migrate config to BLUE** (also fixes the broken build).
   - `frontend/src/shared/sprites/characters.ts`: drop dead `character1` imports; export `BLUE: CharacterDefinition` with the six blue sheets (fps: idle 10, walk 12, run 14, fly 12, flap 14, float 8; all loop).
   - `frontend/src/features/home/components/CharacterShowcase.tsx`: `CHARACTER1.idle` → `BLUE.sprites.idle`.
3. **Controller:** `frontend/src/features/storeys/character/useCharacterController.ts` (new) — state machine, rAF tween, separator scan/anchor (ResizeObserver + resize), dive rotation, teleport, reduced motion. All position writes imperative.
4. **Mount component:** `frontend/src/features/storeys/character/TowerCharacter.tsx` (new) — layer + character div + `SpriteAnimator`, takes `character: CharacterDefinition` prop, attaches shell click/pointerdown listeners, spawn-on-first-separator.
5. **Page:** `StoreyMapPage.tsx` — render `<TowerCharacter character={BLUE} />` inside `.tower-page-shell` after the front cloudfield.
6. **Styles:** `globals.css` — `.tower-character-layer` (abs, inset-0, z-3, pointer-events:none), `.tower-character` (will-change: transform; rotation transition ~150ms), teleport in/out classes, reduced-motion overrides.

## Verification

- `npm run build` / dev server passes (step 2 alone fixes the current dead-import failure).
- /tower: blue spawns idle centered on the first separator; stays glued while scrolling.
- Same-separator click → walks, faces correctly, clamps at edges, idles on arrival.
- Other-storey separator click → fly (take_off skipped until sheet exists) → lands → idle → re-anchors and scroll-sticks there.
- Open-sky clicks: flap when ≥120px above; **below → fly sheet visibly tilted nose-down (dive)**, tilt eases out on arrival; arrival in air → float loop.
- Far click (> threshold) → fade-scale teleport out/in, ends idle (separator) or float (air).
- Doors, tome, docks, sky-clock scrubber unaffected; text-selection drags ignored.
- Resize + lazy storey growth don't displace a grounded blue.
- Reduced motion: instant repositions, frame-0 sprite.
- Home CharacterShowcase shows blue idle.
- Extensibility proof: add a fake `take_off` entry pointing at fly.png → plays once before flight, no code changes.
