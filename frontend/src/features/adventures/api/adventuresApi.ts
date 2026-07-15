import type { ApiRequestBody } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type {
  AdventureLevelLibraryResponse,
  AdventureCommandResponse,
  AdventureRun,
} from '@/features/adventures/types'
import type { CommandExecutionPayload } from '@/shared/level/types'
type WorkspaceFileRequest = { path: string; content: string }
type WorkspaceFileRenameRequest = { path: string; newPath: string }

export const adventuresApi = {
  startRun(levelId: number) {
    return apiOperationRequest<'adventure_levels_runs_create', AdventureRun>(
      'adventure_levels_runs_create',
      `/adventure-levels/${levelId}/runs/`,
    )
  },
  getRun(runId: number) {
    return apiOperationRequest<'adventure_runs_retrieve', AdventureRun>('adventure_runs_retrieve', `/adventure-runs/${runId}/`)
  },
  openLevelLibrary(runId: number) {
    return apiOperationRequest<'adventure_runs_level_library_create', AdventureLevelLibraryResponse>(
      'adventure_runs_level_library_create',
      `/adventure-runs/${runId}/level-library/`,
    )
  },
  submitCommand(runId: number, command: string, execution: CommandExecutionPayload) {
    return apiOperationRequest<'adventure_runs_submit_command_create', AdventureCommandResponse>(
      'adventure_runs_submit_command_create',
      `/adventure-runs/${runId}/submit-command/`,
      { body: { command, execution } as ApiRequestBody<'adventure_runs_submit_command_create'> },
    )
  },
  createFile(runId: number, input: WorkspaceFileRequest) {
    return apiOperationRequest<'adventure_runs_files_create', AdventureRun>(
      'adventure_runs_files_create',
      `/adventure-runs/${runId}/files/`,
      { body: input as ApiRequestBody<'adventure_runs_files_create'> },
    )
  },
  writeFile(runId: number, input: WorkspaceFileRequest) {
    return apiOperationRequest<'adventure_runs_files_partial_update', AdventureRun>(
      'adventure_runs_files_partial_update',
      `/adventure-runs/${runId}/files/`,
      { body: input as ApiRequestBody<'adventure_runs_files_partial_update'> },
    )
  },
  renameFile(runId: number, input: WorkspaceFileRenameRequest) {
    return apiOperationRequest<'adventure_runs_files_update', AdventureRun>(
      'adventure_runs_files_update',
      `/adventure-runs/${runId}/files/`,
      { body: { path: input.path, new_path: input.newPath } },
    )
  },
  deleteFile(runId: number, path: string) {
    return apiOperationRequest<'adventure_runs_files_destroy', AdventureRun>(
      'adventure_runs_files_destroy',
      `/adventure-runs/${runId}/files/?path=${encodeURIComponent(path)}`,
    )
  },
  discardRun(runId: number, options?: Omit<RequestInit, 'method' | 'body'>) {
    return apiOperationRequest<'adventure_runs_destroy', null>(
      'adventure_runs_destroy',
      `/adventure-runs/${runId}/`,
      options,
    )
  },
}
