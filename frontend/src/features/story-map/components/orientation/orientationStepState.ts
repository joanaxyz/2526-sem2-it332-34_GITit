export const BUILDER_TOKENS = ['git', 'commit', 'log', 'status', '-m', '--oneline', '--graph', '--all', '"message"']

export function addToSet(current: Set<string>, value: string) {
  return new Set([...current, value])
}
