/** Only authored emphasis and code spans; HTML and links stay inert text. */
export function ScenarioInline({ text }: { text: string }) {
  return <>{text.split(/(`[^`\n]+`|\*\*[^*\n]+\*\*)/g).map((part, index) => {
    if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
      return <code className="scenario-inline-code" key={index}>{part.slice(1, -1)}</code>
    }
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return <strong className="scenario-inline-strong" key={index}><ScenarioInline text={part.slice(2, -2)} /></strong>
    }
    return part
  })}</>
}
