import { apiOperationRequest } from '@/shared/api/httpClient'
import type { ChallengeCommandResponse, ChallengeRunResponse } from '@/features/challenges/types'
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

export const challengeRunsApi = {
  getRun(runId: number) {
    return apiOperationRequest<'challenge_runs_retrieve', ChallengeRunResponse>('challenge_runs_retrieve', `/challenge-runs/${runId}/`)
  },
  submitCommand(runId: number, command: string, execution: CommandExecutionPayload) {
    return apiOperationRequest<'challenge_runs_submit_command_create', ChallengeCommandResponse>(
      'challenge_runs_submit_command_create',
      `/challenge-runs/${runId}/submit-command/`,
      { body: commandSubmitBody(command, execution) },
    )
  },
  createFile(runId: number, input: WorkspaceFileInput) {
    return apiOperationRequest<'challenge_runs_files_create', ChallengeRunResponse>(
      'challenge_runs_files_create',
      `/challenge-runs/${runId}/files/`,
      { body: workspaceFileBody(input) },
    )
  },
  writeFile(runId: number, input: WorkspaceFileInput) {
    return apiOperationRequest<'challenge_runs_files_partial_update', ChallengeRunResponse>(
      'challenge_runs_files_partial_update',
      `/challenge-runs/${runId}/files/`,
      { body: workspaceFileBody(input) },
    )
  },
  renameFile(runId: number, input: WorkspaceFileRenameInput) {
    return apiOperationRequest<'challenge_runs_files_update', ChallengeRunResponse>(
      'challenge_runs_files_update',
      `/challenge-runs/${runId}/files/`,
      { body: workspaceFileRenameBody(input) },
    )
  },
  deleteFile(runId: number, path: string) {
    return apiOperationRequest<'challenge_runs_files_destroy', ChallengeRunResponse>(
      'challenge_runs_files_destroy',
      `/challenge-runs/${runId}/files/?path=${encodeURIComponent(path)}`,
    )
  },
}
