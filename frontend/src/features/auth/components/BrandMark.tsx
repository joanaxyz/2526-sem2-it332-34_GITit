import { Link } from 'react-router-dom'

import gitLogoImage from '@/assets/images/git-it-logo.webp'
import { cn } from '@/shared/utils/cn'

type BrandMarkProps = {
  size?: 'sm' | 'lg'
  className?: string
}

export function BrandMark({ size = 'lg', className }: BrandMarkProps) {
  return (
    <Link
      to="/"
      aria-label="GIT it! home"
      className={cn('auth-brand', size === 'sm' && 'auth-brand--sm', className)}
    >
      <img src={gitLogoImage} alt="" width={900} height={305} />
    </Link>
  )
}
