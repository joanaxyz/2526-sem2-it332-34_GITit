/**
 * Deterministic shuffling, seeded per question.
 *
 * The backend sends option *pools*, never a shuffled question, so ordering
 * is decided here. It is seeded rather than random so that re-rendering a
 * question (a resize, a re-mount, React 18 double-invoking in dev) cannot
 * move the options out from under someone mid-answer, while a later ask of
 * the same card still gets a different order.
 */

function hash(seed: string): number {
  let value = 2166136261
  for (let index = 0; index < seed.length; index += 1) {
    value ^= seed.charCodeAt(index)
    value = Math.imul(value, 16777619)
  }
  return value >>> 0
}

function nextRandom(state: number): [number, number] {
  let value = state
  value ^= value << 13
  value >>>= 0
  value ^= value >> 17
  value ^= value << 5
  value >>>= 0
  return [value / 0xffffffff, value]
}

export function seededShuffle<T>(items: T[], seed: string): T[] {
  const result = [...items]
  let state = hash(seed) || 1
  for (let index = result.length - 1; index > 0; index -= 1) {
    const [fraction, nextState] = nextRandom(state)
    state = nextState
    const swap = Math.floor(fraction * (index + 1))
    ;[result[index], result[swap]] = [result[swap], result[index]]
  }
  return result
}

/**
 * Shuffle until the order actually differs, where that is possible.
 *
 * An "order these steps" question that opens already in order is not a
 * question, and a token bank that reads left-to-right as the answer lets
 * someone clear the rung without reading it.
 */
export function shuffleAway<T>(items: T[], seed: string): T[] {
  if (items.length < 2) return [...items]
  for (let attempt = 0; attempt < 6; attempt += 1) {
    const shuffled = seededShuffle(items, `${seed}:${attempt}`)
    if (shuffled.some((item, index) => item !== items[index])) return shuffled
  }
  return [...items].reverse()
}
