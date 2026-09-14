import { createContext, useContext } from 'react'

/**
 * Hover/focus state for the commit details overlay.
 *
 * This deliberately does NOT travel through ReactFlow node data. Handing
 * ReactFlow a new `nodes` array re-creates its node internals, which drops the
 * measured width/height and paints every node `visibility: hidden` until the
 * ResizeObserver re-measures - i.e. the whole graph flickers on every hover.
 * Context keeps the array identity stable so only the node re-renders.
 */
export type CommitActivation = {
  activeCommitId: string | null
  activate: (commitId: string) => void
  dismiss: (commitId: string) => void
}

const INERT_ACTIVATION: CommitActivation = {
  activeCommitId: null,
  activate: () => {},
  dismiss: () => {},
}

export const CommitActivationContext = createContext<CommitActivation>(INERT_ACTIVATION)

export function useCommitActivation() {
  return useContext(CommitActivationContext)
}
