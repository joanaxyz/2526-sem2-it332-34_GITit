import { Navigate, useParams } from 'react-router-dom'

/**
 * The tower editor now lives INSIDE the tower page (`/tower?mode=edit`). This
 * route is kept as a redirect so old links / bookmarks still land in the editor.
 */
export function TowerEditorPage() {
  const { designId } = useParams()
  const target = designId
    ? `/tower?view=mine&mode=edit&design=${designId}`
    : '/tower?view=mine&mode=edit'
  return <Navigate replace to={target} />
}

export default TowerEditorPage
