import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'

import { PIECE_TYPE_LABEL } from '@/features/tower-designs/editorUtils'
import { assetsApi } from '@/shared/assets/assetsApi'
import type { TowerPieceType } from '@/shared/assets/types'
import { ApiError } from '@/shared/api/apiError'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

const PIECE_TYPES: TowerPieceType[] = ['crown', 'section', 'landing']
const IMAGE_ACCEPT = '.svg,.png,.webp,.gif,.jpg,.jpeg'

type ScopeBox = {
  x: number
  y: number
  size: number
}

type ImageMetrics = {
  width: number
  height: number
}

export function UploadAssetDialog({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [kind, setKind] = useState<'tower_piece' | 'tower_artifact'>('tower_piece')
  const [label, setLabel] = useState('')
  const [pieceType, setPieceType] = useState<TowerPieceType>('section')
  const [viewBox, setViewBox] = useState('')
  const [tags, setTags] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [hoverFile, setHoverFile] = useState<File | null>(null)
  const [clickFile, setClickFile] = useState<File | null>(null)

  const upload = useMutation({
    mutationFn: () => {
      const form = new FormData()
      form.append('kind', kind)
      form.append('label', label)
      if (tags.trim()) form.append('tags', tags.trim())
      if (file) form.append('file', file)
      if (hoverFile) form.append('file_hover', hoverFile)
      if (clickFile) form.append('file_click', clickFile)
      if (viewBox.trim()) form.append('view_box', viewBox.trim())
      if (kind === 'tower_piece') {
        form.append('piece_type', pieceType)
      }
      return assetsApi.upload(form)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.assetDescriptorsOwned('tower_piece') })
      queryClient.invalidateQueries({ queryKey: queryKeys.assetDescriptorsOwned('tower_artifact') })
      onClose()
    },
  })

  const errorMessage = upload.error instanceof ApiError ? upload.error.message : null
  const canSubmit = label.trim().length > 0 && file !== null && !upload.isPending

  return (
    <div className="upload-dialog-backdrop" role="dialog" aria-modal="true" aria-label="Upload an asset">
      <div className="upload-dialog">
        <header className="upload-dialog-head">
          <h2 className="editor-rail-title">Upload an asset</h2>
          <button type="button" className="editor-icon-btn" onClick={onClose} aria-label="Close">
            <X className="size-4" aria-hidden="true" />
          </button>
        </header>

        <div className="upload-field">
          <span className="upload-label">Type</span>
          <div className="upload-segment">
            <button
              type="button"
              className={kind === 'tower_piece' ? 'is-active' : undefined}
              onClick={() => setKind('tower_piece')}
            >
              Tower piece
            </button>
            <button
              type="button"
              className={kind === 'tower_artifact' ? 'is-active' : undefined}
              onClick={() => setKind('tower_artifact')}
            >
              Artifact
            </button>
          </div>
        </div>

        <label className="upload-field">
          <span className="upload-label">Label</span>
          <input
            className="upload-input"
            value={label}
            onChange={(event) => setLabel(event.target.value)}
            placeholder={kind === 'tower_piece' ? 'My glowing section' : 'My clickable relic'}
          />
        </label>

        {kind === 'tower_piece' ? (
          <label className="upload-field">
            <span className="upload-label">Piece type</span>
            <select
              className="upload-input"
              value={pieceType}
              onChange={(event) => setPieceType(event.target.value as TowerPieceType)}
            >
              {PIECE_TYPES.map((type) => (
                <option key={type} value={type}>
                  {PIECE_TYPE_LABEL[type]}
                </option>
              ))}
            </select>
          </label>
        ) : null}

        <label className="upload-field">
          <span className="upload-label">Default sprite</span>
          <input
            type="file"
            accept={IMAGE_ACCEPT}
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null)
              setViewBox('')
            }}
          />
        </label>

        <ViewBoxScope file={file} viewBox={viewBox} onViewBoxChange={setViewBox} />

        <div className="upload-animation-grid">
          <label className="upload-field">
            <span className="upload-label">Hover sprite</span>
            <input
              type="file"
              accept={IMAGE_ACCEPT}
              onChange={(event) => setHoverFile(event.target.files?.[0] ?? null)}
            />
          </label>
          <label className="upload-field">
            <span className="upload-label">Click sprite</span>
            <input
              type="file"
              accept={IMAGE_ACCEPT}
              onChange={(event) => setClickFile(event.target.files?.[0] ?? null)}
            />
          </label>
        </div>

        <label className="upload-field">
          <span className="upload-label">Tags</span>
          <input
            className="upload-input"
            value={tags}
            onChange={(event) => setTags(event.target.value)}
            placeholder="medieval, neon"
          />
        </label>

        {errorMessage ? <p className="editor-warning is-error">{errorMessage}</p> : null}

        <footer className="upload-dialog-foot">
          <Button variant="outline" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button size="sm" disabled={!canSubmit} onClick={() => upload.mutate()}>
            {upload.isPending ? 'Uploading...' : 'Upload'}
          </Button>
        </footer>
      </div>
    </div>
  )
}

function ViewBoxScope({
  file,
  viewBox,
  onViewBoxChange,
}: {
  file: File | null
  viewBox: string
  onViewBoxChange: (value: string) => void
}) {
  const previewRef = useRef<HTMLDivElement | null>(null)
  const [metrics, setMetrics] = useState<ImageMetrics | null>(null)
  const [box, setBox] = useState<ScopeBox | null>(null)
  const url = useMemo(() => (file ? URL.createObjectURL(file) : null), [file])

  useEffect(() => {
    return () => {
      if (url) URL.revokeObjectURL(url)
    }
  }, [url])

  const previewStyle = useMemo(() => {
    if (!metrics) return undefined
    const ratio = metrics.height / Math.max(metrics.width, 1)
    return { aspectRatio: `${metrics.width} / ${metrics.height}`, maxHeight: `${Math.max(220, 360 * ratio)}px` }
  }, [metrics])

  function initializeBox(image: HTMLImageElement) {
    const width = image.naturalWidth || 512
    const height = image.naturalHeight || 512
    const size = Math.min(width, height)
    const nextBox = { x: (width - size) / 2, y: (height - size) / 2, size }
    setMetrics({ width, height })
    setBox(nextBox)
    onViewBoxChange(formatBox(nextBox))
  }

  function pointFor(event: React.PointerEvent | PointerEvent) {
    const preview = previewRef.current
    if (!preview || !metrics) return null
    const rect = preview.getBoundingClientRect()
    const scaleX = metrics.width / Math.max(rect.width, 1)
    const scaleY = metrics.height / Math.max(rect.height, 1)
    return {
      x: (event.clientX - rect.left) * scaleX,
      y: (event.clientY - rect.top) * scaleY,
    }
  }

  function startMove(event: React.PointerEvent<HTMLDivElement>) {
    event.preventDefault()
    const startPoint = pointFor(event)
    if (!startPoint || !metrics || !box) return
    const initialPoint = startPoint
    const imageMetrics = metrics
    const start = box
    function move(ev: PointerEvent) {
      const point = pointFor(ev)
      if (!point) return
      const next = clampBox(
        {
          ...start,
          x: start.x + point.x - initialPoint.x,
          y: start.y + point.y - initialPoint.y,
        },
        imageMetrics,
      )
      setBox(next)
      onViewBoxChange(formatBox(next))
    }
    function up() {
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', up)
    }
    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', up)
  }

  function startResize(event: React.PointerEvent<HTMLButtonElement>) {
    event.stopPropagation()
    event.preventDefault()
    const startPoint = pointFor(event)
    if (!startPoint || !metrics || !box) return
    const initialPoint = startPoint
    const imageMetrics = metrics
    const start = box
    function move(ev: PointerEvent) {
      const point = pointFor(ev)
      if (!point) return
      const delta = Math.max(point.x - initialPoint.x, point.y - initialPoint.y)
      const next = clampBox({ ...start, size: start.size + delta }, imageMetrics)
      setBox(next)
      onViewBoxChange(formatBox(next))
    }
    function up() {
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', up)
    }
    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', up)
  }

  if (!url) return null

  const boxStyle = metrics && box ? boxToStyle(box, metrics) : undefined

  return (
    <div className="upload-field upload-viewbox-field">
      <span className="upload-label">Visible scope</span>
      <div ref={previewRef} className="upload-viewbox-preview" style={previewStyle}>
        <img src={url} alt="" onLoad={(event) => initializeBox(event.currentTarget)} />
        {boxStyle ? (
          <div className="upload-viewbox-box" style={boxStyle} onPointerDown={startMove}>
            <button
              type="button"
              className="upload-viewbox-handle"
              aria-label="Resize visible scope"
              onPointerDown={startResize}
            />
          </div>
        ) : null}
      </div>
      <output className={cn('upload-viewbox-output', !viewBox && 'is-empty')}>
        {viewBox || 'Move and resize the square to scope the asset.'}
      </output>
    </div>
  )
}

function clampBox(box: ScopeBox, metrics: ImageMetrics): ScopeBox {
  const maxSize = Math.min(metrics.width, metrics.height)
  const size = clamp(box.size, 16, maxSize)
  return {
    size,
    x: clamp(box.x, 0, metrics.width - size),
    y: clamp(box.y, 0, metrics.height - size),
  }
}

function boxToStyle(box: ScopeBox, metrics: ImageMetrics) {
  return {
    left: `${(box.x / metrics.width) * 100}%`,
    top: `${(box.y / metrics.height) * 100}%`,
    width: `${(box.size / metrics.width) * 100}%`,
    height: `${(box.size / metrics.height) * 100}%`,
  }
}

function formatBox(box: ScopeBox) {
  return [box.x, box.y, box.size, box.size].map((value) => Math.round(value).toString()).join(' ')
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}
