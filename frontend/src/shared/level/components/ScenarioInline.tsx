/**
 * Authored inline marks only: `code`, **strong**, *emphasis*, __underline__.
 * Code spans stay literal; HTML, links, and other Markdown stay inert text.
 */
const INLINE_MARK = /(`[^`\n]+`|\*\*[^\s*](?:[^\n]*?[^\s*])?\*\*|__[^\s_](?:[^\n]*?[^\s_])?__|\*[^\s*](?:[^*\n]*?[^\s*])?\*)/g

export function ScenarioInline({ text }: { text: string }) {
  return <>{text.split(INLINE_MARK).map((part, index) => {
    if (part.length > 2 && part.startsWith('`') && part.endsWith('`')) {
      return <code className="scenario-inline-code" key={index}>{part.slice(1, -1)}</code>
    }
    if (part.length > 4 && part.startsWith('**') && part.endsWith('**')) {
      return <strong className="scenario-inline-strong" key={index}><ScenarioInline text={part.slice(2, -2)} /></strong>
    }
    if (part.length > 4 && part.startsWith('__') && part.endsWith('__')) {
      return <u className="scenario-inline-underline" key={index}><ScenarioInline text={part.slice(2, -2)} /></u>
    }
    if (part.length > 2 && part.startsWith('*') && part.endsWith('*')) {
      return <em className="scenario-inline-em" key={index}><ScenarioInline text={part.slice(1, -1)} /></em>
    }
    return part
  })}</>
}
