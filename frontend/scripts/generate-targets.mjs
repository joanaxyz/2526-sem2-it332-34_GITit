// Target-state generator for the curriculum seed.
//
// Reads {case_id: {initial_state, solution_commands, workspace_files}} from
// `inputPath`, replays each solution through the SAME browser git engine the
// learner runs, and writes {case_id: target_state} to `outputPath`. Driven by
// `python manage.py generate_targets` — do not run by hand.
//
// The engine is TypeScript with a `@` path alias, so we load it through a Vite
// dev server (`ssrLoadModule`), which resolves the alias from vite.config.ts.

import { readFileSync, writeFileSync } from 'node:fs'
import { createServer } from 'vite'

const [, , inputPath, outputPath] = process.argv
if (!inputPath || !outputPath) {
  console.error('usage: node generate-targets.mjs <input.json> <output.json>')
  process.exit(2)
}

const server = await createServer({
  configFile: 'vite.config.ts',
  logLevel: 'silent',
  server: { middlewareMode: true },
  appType: 'custom',
})

try {
  const { executeGitCommand } = await server.ssrLoadModule('/src/shared/git/simulator/engine.ts')
  const { normalizeState } = await server.ssrLoadModule('/src/shared/git/simulator/state.ts')
  const { createWorkspaceFile, writeWorkspaceFile } = await server.ssrLoadModule(
    '/src/shared/git/simulator/workspaceFiles.ts',
  )

  // Mid-sequence file edits (e.g. resolve a conflict, then `git add`). `create`
  // adds an untracked file; anything else writes an existing one. Fall back to
  // the other operation so an authored action mismatch never aborts generation.
  const applyFile = (state, file) => {
    const input = { path: file.path, content: file.content ?? '' }
    if (file.action === 'create') {
      try {
        return createWorkspaceFile(state, input)
      } catch {
        return writeWorkspaceFile(state, input)
      }
    }
    try {
      return writeWorkspaceFile(state, input)
    } catch {
      return createWorkspaceFile(state, input)
    }
  }

  const cases = JSON.parse(readFileSync(inputPath, 'utf8'))
  const targets = {}

  for (const [caseId, spec] of Object.entries(cases)) {
    let state = normalizeState(spec.initial_state ?? {})
    const commands = spec.solution_commands ?? []

    // Group file edits by the command index they apply *before* (after N commands
    // have run). `after_command_index: 1` => applied just before command index 1.
    const filesByIndex = new Map()
    for (const file of spec.workspace_files ?? []) {
      const index = Number(file.after_command_index ?? 0)
      if (!filesByIndex.has(index)) filesByIndex.set(index, [])
      filesByIndex.get(index).push(file)
    }

    try {
      for (let i = 0; i < commands.length; i += 1) {
        for (const file of filesByIndex.get(i) ?? []) state = applyFile(state, file)
        state = executeGitCommand(state, commands[i]).next_state
      }
      for (const file of filesByIndex.get(commands.length) ?? []) state = applyFile(state, file)
    } catch (error) {
      console.error(`Failed to replay case '${caseId}': ${error?.message ?? error}`)
      process.exitCode = 1
    }

    // Emit the canonical internal state (what the runtime submit payload carries
    // as `next_state`), not a presentation snapshot - so a target matches the
    // learner's normalized final state key-for-key (incl. read-only scenarios).
    targets[caseId] = normalizeState(state)
  }

  writeFileSync(outputPath, JSON.stringify(targets))
} finally {
  await server.close()
}
