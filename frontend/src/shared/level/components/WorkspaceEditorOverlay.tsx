import { AlertTriangle, FileText, RotateCcw, Save, X } from 'lucide-react'
import type { KeyboardEvent, UIEvent } from 'react'
import { useMemo, useRef, useState } from 'react'

import type { ConflictDetail, RepositorySnapshot, RepositoryValue } from '@/shared/level/types'
import {
  buildProjectTree,
  editorContent,
  flattenProjectFiles,
  lineNumbersFor,
  workspaceFileErrorMessage,
} from '@/shared/level/utils/projectFiles'
import type { ProjectTreeNode, WorkspaceFileInput } from '@/shared/level/utils/projectFiles'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

type WorkspaceEditorOverlayProps = {
  snapshot: RepositorySnapshot
  filePath: string | null
  open: boolean
  writeDisabled?: boolean
  onClose: () => void
  onWriteFile?: (input: WorkspaceFileInput) => Promise<unknown> | void
}

type WorkspaceEditorSurfaceProps = Omit<WorkspaceEditorOverlayProps, 'snapshot'> & {
  selectedFile?: ProjectTreeNode
  conflictDetail?: ConflictDetail
  isConflicted: boolean
  sourceContent: string
}

function stringifyConflictValue(value: RepositoryValue | undefined) {
  return editorContent(value)
}

function stripConflictMarkerLines(value: string) {
  return value
    .split('\n')
    .filter((line) => !line.startsWith('<<<<<<<') && line !== '=======' && !line.startsWith('>>>>>>>'))
    .join('\n')
}

function confirmDiscard() {
  return window.confirm('Discard unsaved file edits?')
}

function StatusBadge({ children, tone = 'muted' }: { children: string; tone?: 'muted' | 'danger' | 'primary' }) {
  return <span className="workspace-editor-badge" data-tone={tone}>{children}</span>
}

function ConflictSidePanel({
  title,
  value,
}: {
  title: string
  value: RepositoryValue | undefined
}) {
  if (value === undefined) return null
  const lineCount = Math.max(1, stringifyConflictValue(value).split('\n').length)

  return (
    <section className="workspace-editor-side-panel">
      <div className="workspace-editor-side-panel__header">
        <span>{title}</span>
        <span>{lineCount} {lineCount === 1 ? 'line' : 'lines'}</span>
      </div>
      <pre className="workspace-editor-side-panel__content app-scrollbar">
        {stringifyConflictValue(value)}
      </pre>
    </section>
  )
}

function selectedFileFor(snapshot: RepositorySnapshot, filePath: string | null): ProjectTreeNode | undefined {
  if (!filePath) return undefined
  return flattenProjectFiles(buildProjectTree(snapshot)).find((file) => file.path === filePath)
}

function WorkspaceEditorSurface({
  filePath,
  open,
  writeDisabled = false,
  onClose,
  onWriteFile,
  selectedFile,
  conflictDetail,
  isConflicted,
  sourceContent,
}: WorkspaceEditorSurfaceProps) {
  const [baselineContent, setBaselineContent] = useState(sourceContent)
  const [draftContent, setDraftContent] = useState(sourceContent)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const gutterRef = useRef<HTMLDivElement>(null)
  const dirty = draftContent !== baselineContent
  const canWriteFile = Boolean(onWriteFile) && !writeDisabled && !submitting && Boolean(filePath)
  const lineNumbers = lineNumbersFor(draftContent, 18)
  const lineCount = Math.max(1, draftContent.split('\n').length)
  const byteCount = new Blob([draftContent]).size
  const isReadOnly = !onWriteFile || writeDisabled

  if (!open || !filePath) return null

  function closeOverlay() {
    if (dirty && !confirmDiscard()) return
    onClose()
  }

  function resetDraft() {
    if (dirty && !confirmDiscard()) return
    setDraftContent(baselineContent)
    setError('')
  }

  async function handleWriteFile() {
    if (!onWriteFile || !filePath || !dirty) return

    setSubmitting(true)
    setError('')
    try {
      await onWriteFile({ path: filePath, content: draftContent })
      setBaselineContent(draftContent)
    } catch (writeError) {
      setError(workspaceFileErrorMessage(writeError))
    } finally {
      setSubmitting(false)
    }
  }

  function handleEditorKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
      event.preventDefault()
      void handleWriteFile()
    }
  }

  function handleDialogKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key !== 'Escape') return
    event.preventDefault()
    closeOverlay()
  }

  function syncGutterScroll(event: UIEvent<HTMLTextAreaElement>) {
    if (gutterRef.current) {
      gutterRef.current.scrollTop = event.currentTarget.scrollTop
    }
  }

  const conflictBranch = conflictDetail?.merge_branch
  const canUseAuthoredResolution = conflictDetail?.resolution !== undefined && conflictDetail.resolution !== null

  return (
    <div
      aria-label={isConflicted ? 'Conflict resolver' : 'Workspace file editor'}
      aria-modal="true"
      className="workspace-editor-backdrop"
      onKeyDown={handleDialogKeyDown}
      role="dialog"
    >
      <section className="workspace-editor-shell" data-conflicted={isConflicted ? 'true' : 'false'}>
        <header className="workspace-editor-commandbar">
          <div className="workspace-editor-titleblock">
            <span className={cn('workspace-editor-file-icon', isConflicted && 'is-conflicted')}>
              {isConflicted ? <AlertTriangle aria-hidden="true" /> : <FileText aria-hidden="true" />}
            </span>
            <div className="workspace-editor-titlecopy">
              <p className="workspace-editor-eyebrow">{isConflicted ? 'Conflict resolver' : 'Workspace editor'}</p>
              <h2>{filePath}</h2>
              <div className="workspace-editor-badges" aria-label="File state">
                {isConflicted ? <StatusBadge tone="danger">conflict</StatusBadge> : null}
                {selectedFile?.status && selectedFile.status !== 'clean' ? (
                  <StatusBadge>{selectedFile.status}</StatusBadge>
                ) : null}
                {conflictBranch ? <StatusBadge tone="primary">{conflictBranch}</StatusBadge> : null}
                {isReadOnly ? <StatusBadge>read only</StatusBadge> : null}
                {dirty ? <StatusBadge tone="primary">unsaved</StatusBadge> : null}
              </div>
            </div>
          </div>
          <div className="workspace-editor-actions">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="workspace-editor-action"
              disabled={!dirty || submitting}
              onClick={resetDraft}
            >
              <RotateCcw aria-hidden="true" />
              Reset
            </Button>
            <Button
              type="button"
              size="sm"
              aria-busy={submitting || undefined}
              className="workspace-editor-action"
              disabled={!canWriteFile || !dirty}
              onClick={handleWriteFile}
            >
              <Save aria-hidden="true" />
              {submitting ? 'Saving' : 'Save'}
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="Close editor"
              className="workspace-editor-close"
              title="Close editor"
              onClick={closeOverlay}
            >
              <X aria-hidden="true" />
            </Button>
          </div>
        </header>

        <div
          className="workspace-editor-body"
          data-conflicted={isConflicted ? 'true' : 'false'}
        >
          <section className="workspace-editor-main">
            {isConflicted ? (
              <div className="workspace-editor-toolbar workspace-editor-toolbar--resolver">
                <span className="workspace-editor-section-label">Resolve using</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="workspace-editor-preset"
                  disabled={conflictDetail?.ours === undefined || submitting}
                  onClick={() => setDraftContent(stringifyConflictValue(conflictDetail?.ours))}
                >
                  Use ours
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="workspace-editor-preset"
                  disabled={conflictDetail?.theirs === undefined || submitting}
                  onClick={() => setDraftContent(stringifyConflictValue(conflictDetail?.theirs))}
                >
                  Use theirs
                </Button>
                {canUseAuthoredResolution ? (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="workspace-editor-preset"
                    disabled={submitting}
                    onClick={() => setDraftContent(stringifyConflictValue(conflictDetail?.resolution))}
                  >
                    Use authored resolution
                  </Button>
                ) : null}
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="workspace-editor-preset"
                  disabled={submitting}
                  onClick={() => setDraftContent((value) => stripConflictMarkerLines(value))}
                >
                  Clear markers
                </Button>
              </div>
            ) : (
              <div className="workspace-editor-toolbar">
                <span className="workspace-editor-section-label">File content</span>
                <div className="workspace-editor-metrics" aria-label="Editor metrics">
                  <span>{lineCount} {lineCount === 1 ? 'line' : 'lines'}</span>
                  <span>{byteCount} bytes</span>
                </div>
              </div>
            )}
            {isConflicted ? (
              <div className="workspace-editor-toolbar workspace-editor-toolbar--metrics">
                <span className="workspace-editor-section-label">Working resolution</span>
                <div className="workspace-editor-metrics" aria-label="Editor metrics">
                  <span>{lineCount} {lineCount === 1 ? 'line' : 'lines'}</span>
                  <span>{byteCount} bytes</span>
                </div>
              </div>
            ) : null}
            <div className="workspace-editor-codeframe" data-readonly={isReadOnly ? 'true' : 'false'}>
              <div
                aria-hidden="true"
                className="workspace-editor-gutter"
                ref={gutterRef}
              >
                {lineNumbers.map((lineNumber) => (
                  <div key={lineNumber}>
                    {lineNumber}
                  </div>
                ))}
              </div>
              <textarea
                value={draftContent}
                aria-label="File content"
                aria-keyshortcuts="Control+S Meta+S"
                readOnly={!canWriteFile}
                spellCheck={false}
                wrap="off"
                onKeyDown={handleEditorKeyDown}
                onScroll={syncGutterScroll}
                onChange={(event) => setDraftContent(event.target.value)}
                className="workspace-editor-textarea app-scrollbar"
              />
            </div>
            {error ? (
              <p role="alert" className="workspace-editor-error">
                {error}
              </p>
            ) : (
              <div className="workspace-editor-error-spacer" />
            )}
          </section>

          {isConflicted ? (
            <aside className="workspace-editor-side-rail app-scrollbar" aria-label="Conflict versions">
              <ConflictSidePanel title="Ours / HEAD" value={conflictDetail?.ours} />
              <ConflictSidePanel title="Theirs / Incoming" value={conflictDetail?.theirs} />
              <ConflictSidePanel title="Base / Common Ancestor" value={conflictDetail?.base} />
            </aside>
          ) : null}
        </div>
      </section>
    </div>
  )
}

export function WorkspaceEditorOverlay({
  snapshot,
  filePath,
  open,
  writeDisabled = false,
  onClose,
  onWriteFile,
}: WorkspaceEditorOverlayProps) {
  const selectedFile = useMemo(() => selectedFileFor(snapshot, filePath), [snapshot, filePath])
  const conflictDetail = filePath ? snapshot.conflict_details?.[filePath] : undefined
  const isConflicted = Boolean(filePath && snapshot.conflicts?.includes(filePath))
  const sourceContent = editorContent(selectedFile?.content)

  return (
    <WorkspaceEditorSurface
      key={`${filePath ?? 'none'}:${sourceContent}`}
      filePath={filePath}
      open={open}
      writeDisabled={writeDisabled}
      selectedFile={selectedFile}
      conflictDetail={conflictDetail}
      isConflicted={isConflicted}
      sourceContent={sourceContent}
      onClose={onClose}
      onWriteFile={onWriteFile}
    />
  )
}
