import { useEffect, useState } from 'react'

type RuntimeStatus = string | null | undefined

function isTerminalRuntimeStatus(status: RuntimeStatus) {
  return status === 'completed' || status === 'failed'
}

export function useOutcomeAnimationGate({
  runId,
  status,
  animating,
}: {
  runId: number | null | undefined
  status: RuntimeStatus
  animating: boolean
}) {
  const [pendingOutcomeAnimationRunId, setPendingOutcomeAnimationRunId] = useState<number | null>(null)
  const [readyOutcomeAnimationRunId, setReadyOutcomeAnimationRunId] = useState<number | null>(null)

  useEffect(() => {
    if (!runId || !isTerminalRuntimeStatus(status)) {
      setPendingOutcomeAnimationRunId(null)
      setReadyOutcomeAnimationRunId(null)
      return
    }
    if (pendingOutcomeAnimationRunId !== runId || animating) return
    setReadyOutcomeAnimationRunId(runId)
    setPendingOutcomeAnimationRunId(null)
  }, [animating, pendingOutcomeAnimationRunId, runId, status])

  return {
    pendingOutcomeAnimationRunId,
    readyOutcomeAnimationRunId,
    queueOutcomeAnimation(runIdToQueue: number) {
      setPendingOutcomeAnimationRunId(runIdToQueue)
      setReadyOutcomeAnimationRunId(null)
    },
    completionAnimationReady(targetRunId: number) {
      return pendingOutcomeAnimationRunId !== targetRunId || readyOutcomeAnimationRunId === targetRunId
    },
  }
}
