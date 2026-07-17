import { useQuery, useQueryClient } from '@tanstack/react-query'

import { adventuresApi } from '@/features/adventures/api/adventuresApi'
import { syncAdventureRunInCache } from '@/features/adventures/utils/adventureRunCache'
import type { AdventureRun } from '@/features/adventures/types'
import { ChapterBookReader } from '@/features/story-map/components/book/ChapterBookModal'
import { queryKeys } from '@/shared/api/queryKeys'
import { LoadingState } from '@/shared/components/LoadingState'
import { Modal } from '@/shared/components/Modal'

export function AdventureLevelLibraryModal({
  run,
  onClose,
}: {
  run: AdventureRun
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const title = `${run.selected_level?.title ?? 'Adventure Level'} - Command Library`
  const libraryQuery = useQuery({
    queryKey: queryKeys.adventureLevelLibrary(run.id),
    queryFn: async () => {
      const response = await adventuresApi.openLevelLibrary(run.id)
      syncAdventureRunInCache(queryClient, response.run)
      return response.book
    },
    staleTime: 0,
    gcTime: 0,
  })

  if (libraryQuery.isLoading && !libraryQuery.data) {
    return (
      <Modal open title={title} onClose={onClose} className="w-full max-w-xl" contentClassName="p-5">
        <LoadingState description="Opening the command library." label="Loading library" variant="inline" />
      </Modal>
    )
  }

  if (libraryQuery.isError || !libraryQuery.data) {
    return (
      <Modal open title={title} onClose={onClose} className="w-full max-w-xl" contentClassName="p-5">
        <div className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm leading-6 text-destructive">
          {libraryQuery.error?.message ?? 'Could not open the command library.'}
        </div>
      </Modal>
    )
  }

  return <ChapterBookReader book={libraryQuery.data} title={title} onClose={onClose} />
}
