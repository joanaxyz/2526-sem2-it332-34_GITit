import { useEffect, useRef, useState } from 'react'

import {
  battleAssetsWarm,
  warmBattleAssets,
  type BattleAssetManifest,
} from '@/shared/battle/battleAssets'

type CapturedEntry = {
  key: string
  manifest: BattleAssetManifest | null
}

/**
 * Keep a playable surface behind its loading screen until every image it can
 * paint has decoded. The manifest is captured once per entry key, so live
 * encounter updates do not throw an already-open workspace back behind a gate.
 */
export function useBattleAssetGate({
  entryKey,
  enabled,
  buildManifest,
}: {
  entryKey: string | null
  enabled: boolean
  buildManifest: () => BattleAssetManifest | null
}): boolean {
  const capturedRef = useRef<CapturedEntry | null>(null)
  if (entryKey && enabled && capturedRef.current?.key !== entryKey) {
    capturedRef.current = { key: entryKey, manifest: buildManifest() }
  }

  const captured = capturedRef.current?.key === entryKey ? capturedRef.current : null
  const manifest = captured?.manifest ?? null
  const [readyKey, setReadyKey] = useState<string | null>(() =>
    entryKey && captured && (!manifest || battleAssetsWarm(manifest)) ? entryKey : null,
  )

  useEffect(() => {
    if (!entryKey || !enabled || !captured) return undefined
    if (!manifest || battleAssetsWarm(manifest)) {
      setReadyKey(entryKey)
      return undefined
    }

    let active = true
    // Deliberately no timeout: dismissing the loading screen while decoding is
    // still in flight is the exact source of the first-paint and action flicker.
    void warmBattleAssets(manifest).then(() => {
      if (active) setReadyKey(entryKey)
    })
    return () => {
      active = false
    }
  }, [captured, enabled, entryKey, manifest])

  if (!entryKey) return true
  if (!enabled || !captured) return false
  return !manifest || readyKey === entryKey || battleAssetsWarm(manifest)
}
