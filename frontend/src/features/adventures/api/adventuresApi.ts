import { apiOperationRequest } from '@/shared/api/httpClient'
import type {
  AdventureLevelLibraryResponse,
  AdventureCommandResponse,
  AdventureRun,
} from '@/features/adventures/types'
import type { CommandExecutionPayload } from '@/shared/level/types'
import {
  commandSubmitBody,
  workspaceFileBody,
  workspaceFileRenameBody,
} from '@/shared/level-runtime/runMutationInputs'
import type {
  WorkspaceFileInput,
  WorkspaceFileRenameInput,
} from '@/shared/level/workspaceFileTypes'

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
      { body: commandSubmitBody(command, execution) },
    )
  },
  createFile(runId: number, input: WorkspaceFileInput) {
    return apiOperationRequest<'adventure_runs_files_create', AdventureRun>(
      'adventure_runs_files_create',
      `/adventure-runs/${runId}/files/`,
      { body: workspaceFileBody(input) },
    )
  },
  writeFile(runId: number, input: WorkspaceFileInput) {
    return apiOperationRequest<'adventure_runs_files_partial_update', AdventureRun>(
      'adventure_runs_files_partial_update',
      `/adventure-runs/${runId}/files/`,
      { body: workspaceFileBody(input) },
    )
  },
  renameFile(runId: number, input: WorkspaceFileRenameInput) {
    return apiOperationRequest<'adventure_runs_files_update', AdventureRun>(
      'adventure_runs_files_update',
      `/adventure-runs/${runId}/files/`,
      { body: workspaceFileRenameBody(input) },
    )
  },
  deleteFile(runId: number, path: string) {
    return apiOperationRequest<'adventure_runs_files_destroy', AdventureRun>(
      'adventure_runs_files_destroy',
      `/adventure-runs/${runId}/files/?path=${encodeURIComponent(path)}`,
    )
  },
  discardRun(runId: number, options?: Omit<RequestInit, 'method' | 'body'>) {
    return apiOperationRequest(
      'adventure_runs_destroy',
      `/adventure-runs/${runId}/`,
      options,
    )
  },
}
