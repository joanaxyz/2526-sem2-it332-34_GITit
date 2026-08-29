import { useQuery } from '@tanstack/react-query'

import { storyMapApi } from '@/features/story-map/api/storyMapApi'
import { queryKeys } from '@/shared/api/queryKeys'

export function useStories() {
  return useQuery({
    queryKey: queryKeys.stories,
    queryFn: storyMapApi.listStories,
    staleTime: 5 * 60 * 1000,
  })
}
