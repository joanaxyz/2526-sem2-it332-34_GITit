import type { ButtonSound } from '@/shared/audio/battleAudioCatalog'
import { BUTTON_SOUND_SET } from '@/shared/audio/battleAudioCatalog'

export function buttonSoundForElement(element: Element): ButtonSound | null {
  if (isDisabledButtonLike(element)) return null

  const explicit = element.getAttribute('data-button-sound')?.trim()
  if (explicit === 'none') return null
  if (explicit && BUTTON_SOUND_SET.has(explicit)) return explicit as ButtonSound

  const classText = element.getAttribute('class')?.toLowerCase() ?? ''
  const labelText = [
    element.getAttribute('aria-label'),
    element.getAttribute('title'),
    element.textContent,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()

  if (/\b(danger|destructive|is-danger)\b/.test(classText)) return 'button-danger'
  if (/\b(delete|remove|revoke|sign out|unpublish|destroy|discard|reset|deduct)\b/.test(labelText)) {
    return 'button-danger'
  }
  if (/\b(close|cancel|back|exit|dismiss|previous)\b/.test(labelText) || /\b(close|dismiss)\b/.test(classText)) {
    return 'button-dismiss'
  }
  if (
    element.getAttribute('aria-pressed') !== null ||
    element.getAttribute('aria-selected') !== null ||
    element.getAttribute('role') === 'tab' ||
    element.getAttribute('role') === 'switch' ||
    /\b(tab|toggle|filter|selector|carousel|pager|switch)\b/.test(classText)
  ) {
    return 'button-toggle'
  }
  if (
    element.getAttribute('type') === 'submit' ||
    /\b(primary|submit|action|cta)\b/.test(classText) ||
    /\b(start|play|try again|retry|continue|next|buy|purchase|unlock|save|update|apply|create|publish|add|copy|submit|confirm|open|search)\b/.test(
      labelText,
    )
  ) {
    return 'button-confirm'
  }

  return 'button-click'
}

export function buttonSoundForEventTarget(target: EventTarget | null): ButtonSound | null {
  if (!(target instanceof Element)) return null
  const element = target.closest('button, [role="button"], [role="tab"], [role="switch"], .ui-button')
  if (!element) return null
  return buttonSoundForElement(element)
}

function isDisabledButtonLike(element: Element): boolean {
  if (element.closest('[aria-disabled="true"]')) return true
  if (element.closest('[disabled]')) return true
  if (element instanceof HTMLButtonElement || element instanceof HTMLInputElement) return element.disabled
  return false
}
