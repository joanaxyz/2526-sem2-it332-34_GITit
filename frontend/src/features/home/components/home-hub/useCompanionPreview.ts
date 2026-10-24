import { useState } from 'react'

import type { CompanionPresentation } from '@/features/home/components/home-hub/companionPresentation'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'

/**
 * The profile and showcase follow whoever is picked in the roster, falling
 * back to the equipped companion. Lives outside HomeProfileWorkspace so the
 * workspace stays a stateless composition of the Home Hub panels.
 */
export function useCompanionPreview(companion: CompanionPresentation) {
  const [previewSlug, setPreviewSlug] = useState<string | null>(null)
  const previewDefinition = previewSlug ? COMPANIONS[previewSlug] : undefined
  const shownCompanion: CompanionPresentation =
    companion.status === 'ready' && previewSlug && previewDefinition
      ? { status: 'ready', definition: previewDefinition, slug: previewSlug }
      : companion

  return { shownCompanion, previewCompanion: setPreviewSlug }
}
