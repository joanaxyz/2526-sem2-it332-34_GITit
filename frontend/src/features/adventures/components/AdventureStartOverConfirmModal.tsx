import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'

export function AdventureStartOverConfirmModal({
  open,
  isRestarting,
  onClose,
  onRestart,
}: {
  open: boolean
  isRestarting: boolean
  onClose: () => void
  onRestart: () => void
}) {
  return (
    <Modal open={open} title="Start fresh run?" className="w-full max-w-md" onClose={onClose}>
      <div className="space-y-5">
        <p className="text-sm leading-6 text-muted-foreground">
          This starts a fresh adventure run. Your current workspace state resets, and the terminal history from this run will not carry over.
        </p>
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li>Completed progress is not deleted.</li>
          <li>This action cannot be undone.</li>
        </ul>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" disabled={isRestarting} onClick={onClose}>
            Cancel
          </Button>
          <Button type="button" disabled={isRestarting} onClick={onRestart}>
            {isRestarting ? 'Starting' : 'Start fresh run'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
