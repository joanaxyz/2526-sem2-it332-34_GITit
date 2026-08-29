import { describe, expect, it } from 'vitest'

import {
  commandSubmitBody,
  workspaceFileBody,
  workspaceFileRenameBody,
} from '@/shared/level-runtime/runMutationInputs'

const execution = {
  processed: true,
  next_state: {
    commits: [],
    branches: {},
    head: { type: 'branch' as const, name: 'main', target: null },
    staging: {},
    working_tree: {},
    conflicts: [],
  },
  output: '',
  normalized_command: 'git status',
  exit_code: 0,
  diagnostic: true,
  stdout: '',
  stderr: '',
  command_family: 'status',
  diagnostic_metadata: [],
}

describe('run mutation input adapters', () => {
  it('builds the generated command and workspace request bodies', () => {
    expect(commandSubmitBody('git status', execution)).toEqual({
      command: 'git status',
      execution,
    })
    expect(workspaceFileBody({ path: 'README.md', content: 'hello' })).toEqual({
      path: 'README.md',
      content: 'hello',
    })
  })

  it('maps the UI rename field to the generated wire field', () => {
    expect(workspaceFileRenameBody({ path: 'old.md', newPath: 'new.md' })).toEqual({
      path: 'old.md',
      new_path: 'new.md',
    })
  })
})
