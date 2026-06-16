import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'

import { PIECE_TYPE_LABEL } from '@/features/tower-designs/editorUtils'
import { assetsApi } from '@/shared/assets/assetsApi'
import type { TowerPieceType } from '@/shared/assets/types'
import { ApiError } from '@/shared/api/apiError'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'

const PIECE_TYPES: TowerPieceType[] = ['crown', 'section', 'landing']
const IMAGE_ACCEPT = '.svg,.png,.webp,.gif,.jpg,.jpeg'

export function UploadAssetDialog({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [kind, setKind] = useState<'tower_piece' | 'tower_artifact'>('tower_piece')
  const [label, setLabel] = useState('')
  const [pieceType, setPieceType] = useState<TowerPieceType>('section')
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
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
        </label>

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
