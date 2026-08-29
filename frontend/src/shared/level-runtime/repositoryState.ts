type SparseRepositoryState = {
  project_tree?: unknown
  visible_tree?: unknown
}

export function mergeRepositoryState<TState extends SparseRepositoryState>(
  previous: TState,
  next: TState,
): TState {
  const carriesTree = next.project_tree !== undefined || next.visible_tree !== undefined
  if (carriesTree) return next

  return {
    ...next,
    project_tree: previous.project_tree,
    visible_tree: previous.visible_tree,
  } as TState
}
