import type { QueryClient } from '@tanstack/react-query'

export const drillRunMutationKey = (levelId: number) => ['drill-run', levelId] as const

/** A returning session must read after its previous checkpoint/report/discard. */
export function waitForDrillWrites(
  client: QueryClient,
  levelId: number,
  signal: AbortSignal,
): Promise<void> {
  return new Promise((resolve, reject) => {
    let unsubscribe = () => {}
    const dispose = () => {
      unsubscribe()
      signal.removeEventListener('abort', abort)
    }
    const abort = () => {
      dispose()
      reject(new DOMException('Drill loading cancelled.', 'AbortError'))
    }
    const check = () => {
      if (client.isMutating({ mutationKey: drillRunMutationKey(levelId) }) === 0) {
        dispose()
        resolve()
      }
    }
    unsubscribe = client.getMutationCache().subscribe(check)
    signal.addEventListener('abort', abort, { once: true })
    if (signal.aborted) abort()
    else check()
  })
}
