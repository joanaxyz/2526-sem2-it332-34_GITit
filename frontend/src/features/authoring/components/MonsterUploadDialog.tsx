import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'

import { assetsApi } from '@/shared/assets/assetsApi'
import {
  DEFAULT_ACTION_FPS,
  MONSTER_ACTIONS,
  REQUIRED_MONSTER_ACTIONS,
  type MonsterAction,
} from '@/shared/assets/spriteActions'
import { ApiError } from '@/shared/api/apiError'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'

const TIERS = ['mob', 'elite', 'boss'] as const

/**
 * Upload an owned monster: one sprite sheet per action (frames counted
 * server-side) plus tier + attack config. Created private until a tower that
 * uses it is shared.
 */
export function MonsterUploadDialog({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [label, setLabel] = useState('')
  const [tier, setTier] = useState<(typeof TIERS)[number]>('mob')
  const [attackKind, setAttackKind] = useState<'melee' | 'projectile'>('melee')
  const [hitFrame, setHitFrame] = useState('3')
  const [lungePx, setLungePx] = useState('48')
  const [tags, setTags] = useState('')
  const [files, setFiles] = useState<Partial<Record<MonsterAction, File>>>({})

  const upload = useMutation({
    mutationFn: () => {
      const form = new FormData()
      form.append('label', label)
      form.append('tier', tier)
      const attack: Record<string, unknown> = { kind: attackKind, hit_frame: Number(hitFrame) || 0 }
      if (attackKind === 'melee') attack.lunge_px = Number(lungePx) || 0
      form.append('attack', JSON.stringify(attack))
      form.append('metrics', JSON.stringify({}))
      if (tags.trim()) form.append('tags', tags.trim())
      for (const action of MONSTER_ACTIONS) {
        const file = files[action]
        if (file) {
          form.append(`sprite_${action}`, file)
          form.append(`fps_${action}`, String(DEFAULT_ACTION_FPS[action]))
        }
      }
      return assetsApi.uploadMonster(form)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.assetDescriptorsOwned('monster') })
      onClose()
    },
  })

  const errorMessage = upload.error instanceof ApiError ? upload.error.message : null
  const hasRequired = REQUIRED_MONSTER_ACTIONS.every((action) => files[action])
  const canSubmit = label.trim().length > 0 && hasRequired && !upload.isPending

  return (
    <div className="upload-dialog-backdrop" role="dialog" aria-modal="true" aria-label="Upload a monster">
      <div className="upload-dialog">
        <header className="upload-dialog-head">
          <h2 className="editor-rail-title">Upload a monster</h2>
          <button type="button" className="editor-icon-btn" onClick={onClose} aria-label="Close">
            <X className="size-4" aria-hidden="true" />
          </button>
        </header>

        <label className="upload-field">
          <span className="upload-label">Name</span>
          <input className="upload-input" value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Gloom Slime" />
        </label>

        <div className="upload-field">
          <span className="upload-label">Tier</span>
          <div className="upload-segment">
            {TIERS.map((value) => (
              <button key={value} type="button" className={tier === value ? 'is-active' : undefined} onClick={() => setTier(value)}>
                {value}
              </button>
            ))}
          </div>
        </div>

        <div className="upload-field">
          <span className="upload-label">Attack</span>
          <div className="upload-segment">
            <button type="button" className={attackKind === 'melee' ? 'is-active' : undefined} onClick={() => setAttackKind('melee')}>
              Melee
            </button>
            <button
              type="button"
              className={attackKind === 'projectile' ? 'is-active' : undefined}
              onClick={() => setAttackKind('projectile')}
            >
              Ranged
            </button>
          </div>
        </div>

        <div className="upload-grid-2">
          <label className="upload-field">
            <span className="upload-label">Hit frame</span>
            <input className="upload-input" type="number" min={0} value={hitFrame} onChange={(e) => setHitFrame(e.target.value)} />
          </label>
          {attackKind === 'melee' ? (
            <label className="upload-field">
              <span className="upload-label">Lunge (px)</span>
              <input className="upload-input" type="number" min={0} value={lungePx} onChange={(e) => setLungePx(e.target.value)} />
            </label>
          ) : null}
        </div>

        <label className="upload-field">
          <span className="upload-label">Tags (optional, comma-separated)</span>
          <input className="upload-input" value={tags} onChange={(e) => setTags(e.target.value)} placeholder="bone, shadow" />
        </label>

        <div className="upload-field">
          <span className="upload-label">Sprite sheets (idle + attack required; horizontal strips)</span>
          <div className="upload-sprite-grid">
            {MONSTER_ACTIONS.map((action) => (
              <label key={action} className="upload-sprite-slot">
                <span>
                  {action}
                  {REQUIRED_MONSTER_ACTIONS.includes(action) ? ' *' : ''}
                  {files[action] ? ' ✓' : ''}
                </span>
                <input
                  type="file"
                  accept=".png,.webp,.gif,.jpg,.jpeg"
                  onChange={(e) => setFiles((prev) => ({ ...prev, [action]: e.target.files?.[0] ?? undefined }))}
                />
              </label>
            ))}
          </div>
        </div>

        {errorMessage ? <p className="editor-warning is-error">{errorMessage}</p> : null}

        <footer className="upload-dialog-foot">
          <Button variant="outline" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button size="sm" disabled={!canSubmit} onClick={() => upload.mutate()}>
            {upload.isPending ? 'Uploading…' : 'Upload monster'}
          </Button>
        </footer>
      </div>
    </div>
  )
}
