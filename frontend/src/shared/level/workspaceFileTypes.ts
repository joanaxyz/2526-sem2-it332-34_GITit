import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

type WorkspaceFile = ApiSchemas['WorkspaceFile']
type WorkspaceFileRename = ApiSchemas['WorkspaceFileRename']

export type WorkspaceFileInput = Pick<WorkspaceFile, 'path'> & {
  content: NonNullable<WorkspaceFile['content']>
}

export type WorkspaceFileRenameInput = Pick<WorkspaceFileRename, 'path'> & {
  newPath: WorkspaceFileRename['new_path']
}
