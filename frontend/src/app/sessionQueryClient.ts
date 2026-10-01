import { QueryClient, type QueryClientConfig } from '@tanstack/react-query'

import { assertAuthSession } from '@/shared/auth/useAuth'

type MutationOptions = NonNullable<Parameters<QueryClient['defaultMutationOptions']>[0]>
type MutationFunction = NonNullable<MutationOptions['mutationFn']>
type SuccessCallback = NonNullable<MutationOptions['onSuccess']>

/** Bind writes to the client that scheduled them, including paused mutations. */
export class SessionQueryClient extends QueryClient {
  private readonly generation: number
  private readonly guardedMutations = new WeakMap<MutationFunction, MutationFunction>()
  private readonly guardedSuccesses = new WeakMap<SuccessCallback, SuccessCallback>()

  constructor(generation: number, config: QueryClientConfig) {
    super(config)
    this.generation = generation
  }

  override defaultMutationOptions<T extends MutationOptions>(options?: T): T {
    const resolved = super.defaultMutationOptions(options)
    const mutationFn = resolved.mutationFn
    const onSuccess = resolved.onSuccess
    // Observers reapply options while a mutation is pending. Guard here so an
    // options update cannot remove the check before a queued write resumes.
    if (mutationFn && !this.guardedMutations.has(mutationFn)) {
      const guarded: MutationFunction = (...args) => {
        assertAuthSession(this.generation)
        return mutationFn(...args)
      }
      this.guardedMutations.set(mutationFn, guarded)
      this.guardedMutations.set(guarded, guarded)
    }
    if (onSuccess && !this.guardedSuccesses.has(onSuccess)) {
      const guarded: SuccessCallback = (...args) => {
        assertAuthSession(this.generation)
        return onSuccess(...args)
      }
      this.guardedSuccesses.set(onSuccess, guarded)
      this.guardedSuccesses.set(guarded, guarded)
    }
    return {
      ...resolved,
      ...(mutationFn ? { mutationFn: this.guardedMutations.get(mutationFn) } : {}),
      ...(onSuccess ? { onSuccess: this.guardedSuccesses.get(onSuccess) } : {}),
    }
  }
}
