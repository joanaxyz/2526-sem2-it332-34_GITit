import { useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ImageOff, Trash2 } from 'lucide-react'

import type { BattleStageArtifactConfig, BattleStageConfig } from '@/features/authoring/types'
import { backendUrl } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'
import { assetsApi } from '@/shared/assets/assetsApi'
import type { AssetDescriptor } from '@/shared/assets/types'
import { cn } from '@/shared/utils/cn'

type ArtifactOption = { slug: string; label: string; url: string | null }

const EMPTY: BattleStageConfig = { background: null, artifacts: [] }

function thumbUrl(descriptor: AssetDescriptor): string | null {
  const sprite = descriptor.sprites.default ?? Object.values(descriptor.sprites)[0]
  return sprite?.url ? backendUrl(sprite.url) : null
}

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value))
}

/**
 * Author a storey's battle stage: pick a backdrop and drag decorative artifacts
 * onto a preview of the stage. Positions are stored normalized (0..1) so they
 * render at any battle-stage size. Reuses the same artifact pool as the tower
 * editor (the author's owned + purchased tower/battle artifacts).
 */
export function BattleStageEditor({
  value,
  onChange,
}: {
  value: BattleStageConfig | undefined
  onChange: (config: BattleStageConfig) => void
}) {
  const config = value ?? EMPTY
  const stageRef = useRef<HTMLDivElement | null>(null)
  const [selected, setSelected] = useState<number | null>(null)

  const towerArtifacts = useQuery({
    queryKey: queryKeys.assetDescriptorsOwned('tower_artifact'),
    queryFn: () => assetsApi.getOwnedDescriptors('tower_artifact'),
    staleTime: 5 * 60 * 1000,
  })
  const battleArtifacts = useQuery({
    queryKey: queryKeys.assetDescriptorsOwned('battle_artifact'),
    queryFn: () => assetsApi.getOwnedDescriptors('battle_artifact'),
    staleTime: 5 * 60 * 1000,
  })

  const options = useMemo<ArtifactOption[]>(() => {
    const all = [
      ...Object.values(towerArtifacts.data?.results ?? {}),
      ...Object.values(battleArtifacts.data?.results ?? {}),
    ]
    return all.map((d) => ({ slug: d.slug, label: d.label, url: thumbUrl(d) }))
  }, [towerArtifacts.data, battleArtifacts.data])

  const urlBySlug = useMemo(() => {
    const map: Record<string, string | null> = {}
    for (const option of options) map[option.slug] = option.url
    return map
  }, [options])

  function update(next: Partial<BattleStageConfig>) {
    onChange({ ...config, ...next })
  }

  function addArtifact(slug: string) {
    const artifact: BattleStageArtifactConfig = { slug, x: 0.5, y: 0.55, scale: 1, rotation: 0, z: 0 }
    update({ artifacts: [...config.artifacts, artifact] })
    setSelected(config.artifacts.length)
  }

  function patchArtifact(index: number, patch: Partial<BattleStageArtifactConfig>) {
    update({ artifacts: config.artifacts.map((a, i) => (i === index ? { ...a, ...patch } : a)) })
  }

  function removeArtifact(index: number) {
    update({ artifacts: config.artifacts.filter((_, i) => i !== index) })
    setSelected(null)
  }

  function startDrag(index: number, event: React.PointerEvent) {
    event.stopPropagation()
    event.preventDefault()
    setSelected(index)
    const rect = stageRef.current?.getBoundingClientRect()
    if (!rect) return
    const { left, top, width, height } = rect
    function move(ev: PointerEvent) {
      patchArtifact(index, {
        x: clamp01((ev.clientX - left) / width),
        y: clamp01((ev.clientY - top) / height),
      })
    }
    function up() {
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', up)
    }
    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', up)
  }

  const backgroundUrl = config.background ? urlBySlug[config.background] : null
  const selectedArtifact = selected !== null ? config.artifacts[selected] : null

  return (
    <section className="author-card">
      <header className="author-card-head">
        <h2 className="author-card-title">Battle stage</h2>
        <p className="author-card-sub">
          Dress the floor Blue defends — pick a backdrop and drag artifacts onto the stage. Shown behind the fighters in
          every battle on this storey.
        </p>
      </header>

      <div
        ref={stageRef}
        className="stage-ed-canvas"
        onClick={() => setSelected(null)}
        role="application"
        aria-label="Battle stage preview"
      >
        {backgroundUrl ? (
          <img className="stage-ed-bg" src={backgroundUrl} alt="" draggable={false} />
        ) : (
          <div className="stage-ed-sky" aria-hidden />
        )}
        <div className="stage-ed-ledge" aria-hidden />
        {config.artifacts.map((artifact, index) => {
          const url = urlBySlug[artifact.slug]
          return (
            <span
              key={`${artifact.slug}-${index}`}
              className={cn('stage-ed-artifact', selected === index && 'is-selected')}
              style={{
                left: `${artifact.x * 100}%`,
                top: `${artifact.y * 100}%`,
                transform: `translate(-50%, -50%) scale(${artifact.scale}) rotate(${artifact.rotation}deg)`,
              }}
              onPointerDown={(e) => startDrag(index, e)}
            >
              {url ? <img src={url} alt="" draggable={false} /> : <ImageOff className="size-5 opacity-50" />}
            </span>
          )
        })}
        {/* Blue stand-in, so the author sees the actors' zone. */}
        <span className="stage-ed-hero" aria-hidden>
          Blue
        </span>
      </div>

      {selectedArtifact ? (
        <div className="stage-ed-controls">
          <label className="author-field author-field--inline">
            <span className="author-label">Size</span>
            <input
              type="range"
              min={0.4}
              max={2}
              step={0.05}
              value={selectedArtifact.scale}
              onChange={(e) => patchArtifact(selected as number, { scale: Number(e.target.value) })}
            />
          </label>
          <label className="author-field author-field--inline">
            <span className="author-label">Rotate</span>
            <input
              type="range"
              min={-180}
              max={180}
              step={5}
              value={selectedArtifact.rotation}
              onChange={(e) => patchArtifact(selected as number, { rotation: Number(e.target.value) })}
            />
          </label>
          <button type="button" className="editor-danger-btn" onClick={() => removeArtifact(selected as number)}>
            <Trash2 className="size-4" aria-hidden="true" />
            Remove
          </button>
        </div>
      ) : null}

      <div className="stage-ed-section">
        <span className="author-label">Backdrop</span>
        <div className="stage-ed-chip-row">
          <button
            type="button"
            className={cn('market-chip', config.background === null && 'is-active')}
            onClick={() => update({ background: null })}
          >
            Sky (default)
          </button>
          {options.map((option) => (
            <button
              key={option.slug}
              type="button"
              className={cn('market-chip', config.background === option.slug && 'is-active')}
              onClick={() => update({ background: option.slug })}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="stage-ed-section">
        <span className="author-label">Artifacts (click to add, then drag on the stage)</span>
        {options.length === 0 ? (
          <p className="author-hint">
            No artifacts yet — upload tower/battle artifacts or buy them in the Shop, then they appear here.
          </p>
        ) : (
          <div className="stage-ed-palette">
            {options.map((option) => (
              <button
                key={option.slug}
                type="button"
                className="editor-palette-cell"
                title={option.label}
                aria-label={`Add ${option.label}`}
                onClick={() => addArtifact(option.slug)}
              >
                <span className="editor-palette-thumb">
                  {option.url ? <img src={option.url} alt="" draggable={false} /> : null}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
