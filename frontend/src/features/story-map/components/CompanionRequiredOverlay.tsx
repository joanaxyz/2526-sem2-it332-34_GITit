import { Store } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  GameplayWorkspaceTour,
  type WorkspaceTourCloseReason,
  type WorkspaceTourStep,
} from '@/shared/level/components/GameplayWorkspaceTour'
import { SHOP_ROUTE } from '@/shared/navigation/routes'

const MOBILE_NAV_QUERY = '(max-width: 720px)'

function useMobileShopTarget() {
  const [mobile, setMobile] = useState(
    () => typeof window !== 'undefined' && typeof window.matchMedia === 'function'
      ? window.matchMedia(MOBILE_NAV_QUERY).matches
      : false,
  )

  useEffect(() => {
    if (typeof window.matchMedia !== 'function') return
    const media = window.matchMedia(MOBILE_NAV_QUERY)
    const update = () => setMobile(media.matches)
    update()
    media.addEventListener('change', update)
    return () => media.removeEventListener('change', update)
  }, [])

  return mobile
}

export function CompanionRequiredOverlay({
  open,
  onDismiss,
}: {
  open: boolean
  onDismiss: () => void
}) {
  const navigate = useNavigate()
  const mobile = useMobileShopTarget()
  const shopTarget = `[data-companion-shop-target="${mobile ? 'mobile' : 'desktop'}"]`
  const steps = useMemo(
    () => [
      {
        id: 'companion-shop',
        selector: shopTarget,
        icon: Store,
        title: 'Choose a companion before you enter',
        body: 'Every Adventure needs a companion. Buy one in the Shop and it will equip automatically.',
        placement: mobile ? 'top' : 'bottom',
      },
    ] satisfies WorkspaceTourStep[],
    [mobile, shopTarget],
  )
  const shopReveal = useMemo(() => [shopTarget], [shopTarget])

  useEffect(() => {
    if (!open) return
    const target = document.querySelector<HTMLElement>(shopTarget)
    target?.classList.add('is-companion-required-target')
    return () => target?.classList.remove('is-companion-required-target')
  }, [open, shopTarget])

  if (!open) return null

  function close(reason: WorkspaceTourCloseReason) {
    if (reason === 'finish') {
      navigate(`${SHOP_ROUTE}?required=1`)
      return
    }
    onDismiss()
  }

  return (
    <GameplayWorkspaceTour
      label="Companion required"
      finishLabel="Buy a companion"
      skipLabel="Not now"
      showProgress={false}
      cardClassName="companion-required-tour"
      reveal={shopReveal}
      steps={steps}
      onClose={close}
    />
  )
}
