import { useState } from 'react'

type TagsFieldProps = {
  value: string[]
  onChange: (tags: string[]) => void
}

/** Comma-separated tag input that preserves in-progress text such as a trailing comma. */
export function TagsField({ value, onChange }: TagsFieldProps) {
  const [text, setText] = useState(() => value.join(', '))

  return (
    <label className="author-field">
      <span className="author-label">Tags</span>
      <span className="author-hint">Comma-separated, used for search and the store.</span>
      <input
        className="author-input"
        value={text}
        onChange={(event) => {
          setText(event.target.value)
          onChange(
            event.target.value
              .split(',')
              .map((tag) => tag.trim())
              .filter(Boolean),
          )
        }}
        placeholder="branching, merge"
      />
    </label>
  )
}
