import { Code2 } from 'lucide-react'
import { useMemo, useState } from 'react'

import {
  compileSummary,
  definitionErrorMessage,
  formToDefinition,
  type AuthoringForm,
} from '@/features/authoring/utils/authoringModel'

type ValidationError = { field: string; message: string }

type ContentEditorDiagnosticsProps = {
  form: AuthoringForm
  formError: string | null
  validationErrors: ValidationError[]
}

const RAW_JSON_ID = 'content-editor-generated-json'

export function ContentEditorDiagnostics({
  form,
  formError,
  validationErrors,
}: ContentEditorDiagnosticsProps) {
  const [showRaw, setShowRaw] = useState(false)
  const rawJson = useMemo(() => {
    try {
      return JSON.stringify(formToDefinition(form), null, 2)
    } catch (error) {
      return definitionErrorMessage(error) ?? 'Definition is not yet valid.'
    }
  }, [form])

  return (
    <>
      {formError || validationErrors.length ? (
        <div role="alert">
          {formError ? <p className="editor-warning is-error">{formError}</p> : null}
          {validationErrors.length ? (
            <ul className="author-errors">
              {validationErrors.map((error) => (
                <li key={`${error.field}-${error.message}`}>{error.field}: {error.message}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
      <section className="author-card">
        <p className="author-hint">Compiles to {compileSummary(form)}.</p>
        <button
          type="button"
          className="author-raw-toggle"
          aria-expanded={showRaw}
          aria-controls={RAW_JSON_ID}
          onClick={() => setShowRaw((value) => !value)}
        >
          <Code2 className="size-4" aria-hidden="true" /> {showRaw ? 'Hide' : 'Show'} the generated JSON
        </button>
        {showRaw ? <pre className="author-raw" id={RAW_JSON_ID}>{rawJson}</pre> : null}
      </section>
    </>
  )
}
