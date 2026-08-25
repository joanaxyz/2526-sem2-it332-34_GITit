import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
import type { CommandExecutionPayload } from '@/shared/level/types'
import type {
  WorkspaceFileInput,
  WorkspaceFileRenameInput,
} from '@/shared/level/workspaceFileTypes'

export function commandSubmitBody(
  command: string,
  execution: CommandExecutionPayload,
): ApiSchemas['CommandSubmit'] {
  return { command, execution }
}

export function workspaceFileBody(input: WorkspaceFileInput): ApiSchemas['WorkspaceFile'] {
  return input
}

export function workspaceFileRenameBody(
  input: WorkspaceFileRenameInput,
): ApiSchemas['WorkspaceFileRename'] {
  return { path: input.path, new_path: input.newPath }
}
