import { ScenarioInline } from '@/shared/level/components/ScenarioInline'

type Block =
  | { kind: 'code'; text: string }
  | { kind: 'list'; ordered: boolean; items: string[] }
  | { kind: 'paragraph'; text: string }

const FENCE = /```[^\n]*\n?([\s\S]*?)(?:```|$)/g
const BULLET = /^\s*(?:[-*•]|(\d+)[.)])\s+(.*)$/

/**
 * The light Markdown Git-It writes: paragraphs, fenced code, bullet/numbered lists, and the
 * shared inline marks. Everything else, HTML included, stays inert text.
 */
export function TutorMarkdown({ text }: { text: string }) {
  return <>{blocks(text).map((block, index) => {
    if (block.kind === 'code') return <pre key={index} className="tutor-chat__code"><code>{block.text}</code></pre>
    if (block.kind === 'list') {
      const items = block.items.map((item, position) => <li key={position}><ScenarioInline text={item} /></li>)
      return block.ordered ? <ol key={index}>{items}</ol> : <ul key={index}>{items}</ul>
    }
    return <p key={index}><ScenarioInline text={block.text} /></p>
  })}</>
}

function blocks(text: string): Block[] {
  const result: Block[] = []
  let last = 0
  for (const match of text.matchAll(FENCE)) {
    result.push(...prose(text.slice(last, match.index)))
    const code = match[1].replace(/\n$/, '')
    if (code.trim()) result.push({ kind: 'code', text: code })
    last = match.index + match[0].length
  }
  result.push(...prose(text.slice(last)))
  return result
}

function prose(text: string): Block[] {
  const result: Block[] = []
  for (const chunk of text.split(/\n{2,}/)) {
    let lines: string[] = []
    const flush = () => {
      if (lines.length) result.push({ kind: 'paragraph', text: lines.join('\n') })
      lines = []
    }
    for (const line of chunk.split('\n')) {
      const item = BULLET.exec(line)
      const list = result.at(-1)
      if (item) {
        flush()
        const ordered = Boolean(item[1])
        if (list?.kind === 'list' && list.ordered === ordered) list.items.push(item[2])
        else result.push({ kind: 'list', ordered, items: [item[2]] })
      } else if (line.trim()) {
        lines.push(line.trim())
      }
    }
    flush()
  }
  return result
}
