import type { ReactNode } from 'react'

export function PageHeading({ title, description }: { title: string; description?: string }) {
  return (
    <div className="admin-page-heading">
      <h1>{title}</h1>
      {description ? <p>{description}</p> : null}
    </div>
  )
}

export function StatTile({ label, value, hint }: { label: string; value: ReactNode; hint?: string }) {
  return (
    <div className="admin-stat-tile">
      <p>{label}</p>
      <strong>{value}</strong>
      {hint ? <small>{hint}</small> : null}
    </div>
  )
}
