import optimizedMedia from './optimizedPublicMedia.json'

const replacements: Record<string, string> = optimizedMedia

/** Resolve dynamic media URLs to verified smaller delivery copies. */
export function publicMediaUrl(source: string): string {
  return replacements[source] ?? source
}
