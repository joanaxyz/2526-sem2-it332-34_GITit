import { Navigate, useParams } from 'react-router-dom'

import { storyPath } from '@/shared/navigation/routes'

export function LegacySharedStoryRedirect() {
  return <Navigate replace to={storyPath()} />
}

export function LegacyStoryRouteRedirect() {
  const { storySlug } = useParams()
  return <Navigate replace to={storyPath(storySlug)} />
}

export function LegacyStoryEditorRedirect() {
  return <Navigate replace to={storyPath()} />
}
