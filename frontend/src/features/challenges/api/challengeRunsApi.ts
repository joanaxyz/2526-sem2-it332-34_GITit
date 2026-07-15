import type { ApiRequestBody } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type { ChallengeCommandResponse, ChallengeRun } from '@/features/challenges/types'
import type { CommandExecutionPayload } from '@/shared/level/types'

type WorkspaceFileRequest = { path: string; content: string }
type WorkspaceFileRenameRequest = { path: string; newPath: string }

export const challengeRunsApi = {
  getRun(runId: number) {
    return apiOperationRequest<'challenge_runs_retrieve', ChallengeRun>('challenge_runs_retrieve', `/challenge-runs/${runId}/`)
  },
  submitCommand(runId: number, command: string, execution: CommandExecutionPayload) {
    return apiOperationRequest<'challenge_runs_submit_command_create', ChallengeCommandResponse>(
      'challenge_runs_submit_command_create',
      `/challenge-runs/${runId}/submit-command/`,
      { body: { command, execution } as ApiRequestBody<'challenge_runs_submit_command_create'> },
    )
  },
  createFile(runId: number, input: WorkspaceFileRequest) {
    return apiOperationRequest<'challenge_runs_files_create', ChallengeRun>(
      'challenge_runs_files_create',
      `/challenge-runs/${runId}/files/`,
      { body: input as ApiRequestBody<'challenge_runs_files_create'> },
    )
  },
  writeFile(runId: number, input: WorkspaceFileRequest) {
    return apiOperationRequest<'challenge_runs_files_partial_update', ChallengeRun>(
      'challenge_runs_files_partial_update',
      `/challenge-runs/${runId}/files/`,
      { body: input as ApiRequestBody<'challenge_runs_files_partial_update'> },
    )
  },
  renameFile(runId: number, input: WorkspaceFileRenameRequest) {
    return apiOperationRequest<'challenge_runs_files_update', ChallengeRun>(
      'challenge_runs_files_update',
      `/challenge-runs/${runId}/files/`,
      { body: { path: input.path, new_path: input.newPath } },
    )
  },
  deleteFile(runId: number, path: string) {
    return apiOperationRequest<'challenge_runs_files_destroy', ChallengeRun>(
      'challenge_runs_files_destroy',
      `/challenge-runs/${runId}/files/?path=${encodeURIComponent(path)}`,
    )
  },
}
