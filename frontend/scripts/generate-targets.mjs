// Target-state generator for the curriculum seed.
//
// Replays each authored solution through the SAME browser git engine the learner
// runs, rejects unprocessable or over-budget routes, and writes
// {targets: {case_id: target_state}, replays: {case_id: replay}} to `outputPath`.
// A replay records the state in front of every solution command; the backend
// fingerprints it into the variant's solution trajectory. Driven by
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
  const { executeTerminalCommand } = await server.ssrLoadModule('/src/shared/git/simulator/engine.ts')
  const { shellProgram } = await server.ssrLoadModule('/src/shared/git/simulator/shell/index.ts')
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
  const replays = {}

  for (const [caseId, spec] of Object.entries(cases)) {
    let state = normalizeState(spec.initial_state ?? {})
    const commands = spec.solution_commands ?? []
    const maxCountedCommands = Number(spec.max_counted_commands)
    if (!Number.isInteger(maxCountedCommands) || maxCountedCommands < 1) {
      console.error(`Invalid command budget for case '${caseId}': ${spec.max_counted_commands}`)
      process.exitCode = 1
      continue
    }

    // Group file edits by the command index they apply *before* (after N commands
    // have run). `after_command_index: 1` => applied just before command index 1.
    const filesByIndex = new Map()
    for (const file of spec.workspace_files ?? []) {
      const index = Number(file.after_command_index ?? 0)
      if (!Number.isInteger(index) || index < 0 || index > commands.length) {
        console.error(
          `Invalid workspace edit index for case '${caseId}': ${file.after_command_index}`,
        )
        process.exitCode = 1
        continue
      }
      if (!filesByIndex.has(index)) filesByIndex.set(index, [])
      filesByIndex.get(index).push(file)
    }

    const steps = []
    let finalBeforeEdits = null
    // The state before authored edits is only worth recording when edits exist:
    // the learner stands there until they make the edit themselves.
    const applyEdits = (index) => {
      const files = filesByIndex.get(index) ?? []
      const beforeEdits = files.length ? normalizeState(state) : null
      for (const file of files) state = applyFile(state, file)
      return beforeEdits
    }
    try {
      let countedCommands = 0
      // Shell commands (`cd src`, `mkdir docs`) run in the terminal's working
      // directory, which carries over between commands like in a real shell.
      let cwd = ''
      for (let i = 0; i < commands.length; i += 1) {
        const beforeEdits = applyEdits(i)
        const terminal = executeTerminalCommand(state, commands[i], { cwd })
        const execution = terminal.execution
        cwd = terminal.cwd
        steps.push({
          command: commands[i],
          diagnostic: Boolean(execution.diagnostic),
          before_edits: beforeEdits,
          ready: normalizeState(state),
        })
        if (!execution.processed) {
          throw new Error(
            `solution command ${i + 1}/${commands.length} was rejected: ${JSON.stringify(commands[i])}` +
              ` (${execution.output || `exit ${execution.exit_code}`})`,
          )
        }
        // Shell commands are free at runtime, file-changing ones included.
        if (!execution.diagnostic && !shellProgram(commands[i])) countedCommands += 1
        if (countedCommands > maxCountedCommands) {
          throw new Error(
            `solution exceeds its ${maxCountedCommands}-command budget at command ` +
              `${i + 1}/${commands.length}: ${JSON.stringify(commands[i])}`,
          )
        }
        state = execution.next_state
      }
      finalBeforeEdits = applyEdits(commands.length)
    } catch (error) {
      console.error(`Failed to replay case '${caseId}': ${error?.message ?? error}`)
      process.exitCode = 1
    }

    // Emit the canonical internal state (what the runtime submit payload carries
    // as `next_state`), not a presentation snapshot - so a target matches the
    // learner's normalized final state key-for-key (incl. read-only scenarios).
    targets[caseId] = normalizeState(state)
    replays[caseId] = { steps, final: targets[caseId], final_before_edits: finalBeforeEdits }
  }

  writeFileSync(outputPath, JSON.stringify({ targets, replays }))
} finally {
  await server.close()
}
