import { AlertTriangle, FileText, RotateCcw, Save, X } from 'lucide-react'
import { useMemo, useState } from 'react'

import type { ConflictDetail, RepositorySnapshot, RepositoryValue } from '@/shared/practice/types'
import {
  buildProjectTree,
  editorContent,
  flattenProjectFiles,
  lineNumbersFor,
  workspaceFileErrorMessage,
} from '@/shared/practice/utils/projectFiles'
import type { ProjectTreeNode, WorkspaceFileInput } from '@/shared/practice/utils/projectFiles'
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
  return (
    <span
      className={cn(
        'rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase leading-none',
        tone === 'danger' && 'bg-destructive/10 text-destructive',
        tone === 'primary' && 'bg-primary/10 text-primary',
        tone === 'muted' && 'bg-muted text-muted-foreground',
      )}
    >
      {children}
    </span>
  )
}

function ConflictSidePanel({
  title,
  value,
}: {
  title: string
  value: RepositoryValue | undefined
}) {
  if (value === undefined) return null

  return (
    <section className="min-h-0 overflow-hidden rounded-md border border-border/70 bg-background/75">
      <div className="border-b border-border/70 px-3 py-2 text-xs font-semibold uppercase text-muted-foreground">
        {title}
      </div>
      <pre className="max-h-36 overflow-auto whitespace-pre-wrap break-words p-3 font-mono text-xs leading-5 text-foreground app-scrollbar">
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
  const dirty = draftContent !== baselineContent
  const canWriteFile = Boolean(onWriteFile) && !writeDisabled && !submitting && Boolean(filePath)
  const lineNumbers = lineNumbersFor(draftContent, 18)

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

  const conflictBranch = conflictDetail?.merge_branch
  const canUseAuthoredResolution = conflictDetail?.resolution !== undefined && conflictDetail.resolution !== null

  return (
    <div
      aria-label={isConflicted ? 'Conflict resolver' : 'Workspace file editor'}
      aria-modal="true"
      className="absolute inset-2 z-40 grid rounded-lg bg-black/55 p-2"
      role="dialog"
    >
      <section className="grid min-h-0 grid-rows-[auto_minmax(0,1fr)] overflow-hidden rounded-lg border border-border bg-card shadow-2xl">
        <header className="flex min-h-14 items-center justify-between gap-3 border-b border-border px-4">
          <div className="flex min-w-0 items-center gap-2">
            {isConflicted ? (
              <AlertTriangle className="size-4 shrink-0 text-destructive" />
            ) : (
              <FileText className="size-4 shrink-0 text-muted-foreground" />
            )}
            <div className="min-w-0">
              <h2 className="truncate font-mono text-sm font-semibold text-foreground">{filePath}</h2>
              <div className="mt-1 flex flex-wrap items-center gap-1.5">
                {isConflicted ? <StatusBadge tone="danger">conflict</StatusBadge> : null}
                {selectedFile?.status && selectedFile.status !== 'clean' ? (
                  <StatusBadge>{selectedFile.status}</StatusBadge>
                ) : null}
                {conflictBranch ? <StatusBadge tone="primary">{conflictBranch}</StatusBadge> : null}
                {dirty ? <StatusBadge tone="primary">unsaved</StatusBadge> : null}
              </div>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-1.5">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={!dirty || submitting}
              onClick={resetDraft}
            >
              <RotateCcw className="size-4" />
              Reset
            </Button>
            <Button
              type="button"
              size="sm"
              disabled={!canWriteFile || !dirty}
              onClick={handleWriteFile}
            >
              <Save className="size-4" />
              {submitting ? 'Saving' : 'Save'}
            </Button>
            <Button type="button" variant="ghost" size="icon" aria-label="Close editor" onClick={closeOverlay}>
              <X className="size-4" />
            </Button>
          </div>
        </header>

        <div
          className={cn(
            'grid min-h-0 gap-3 overflow-hidden p-3',
            isConflicted ? 'grid-cols-[minmax(0,1.4fr)_minmax(18rem,0.6fr)] max-xl:grid-cols-1' : 'grid-cols-1',
          )}
        >
          <section className="grid min-h-0 grid-rows-[auto_minmax(0,1fr)_auto] overflow-hidden rounded-md border border-border/70 bg-background">
            {isConflicted ? (
              <div className="flex flex-wrap items-center gap-2 border-b border-border/70 px-3 py-2">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  disabled={conflictDetail?.ours === undefined || submitting}
                  onClick={() => setDraftContent(stringifyConflictValue(conflictDetail?.ours))}
                >
                  Use ours
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
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
                  disabled={submitting}
                  onClick={() => setDraftContent((value) => stripConflictMarkerLines(value))}
                >
                  Clear markers
                </Button>
              </div>
            ) : (
              <div className="border-b border-border/70 px-3 py-2 text-xs font-semibold uppercase text-muted-foreground">
                File content
              </div>
            )}
            <div className="grid min-h-0 grid-cols-[3.25rem_minmax(0,1fr)] overflow-hidden bg-[#111827] font-mono text-xs">
              <div
                aria-hidden="true"
                className="select-none border-r border-white/10 bg-black/20 py-3 text-right leading-5 text-slate-500"
              >
                {lineNumbers.map((lineNumber) => (
                  <div key={lineNumber} className="px-3">
                    {lineNumber}
                  </div>
                ))}
              </div>
              <textarea
                value={draftContent}
                aria-label="File content"
                readOnly={!canWriteFile}
                spellCheck={false}
                onChange={(event) => setDraftContent(event.target.value)}
                className="h-full min-h-0 w-full resize-none overflow-auto bg-transparent px-4 py-3 leading-5 text-slate-100 caret-primary outline-none placeholder:text-slate-500 read-only:cursor-default read-only:text-slate-300 app-scrollbar"
              />
            </div>
            {error ? (
              <p role="alert" className="border-t border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </p>
            ) : (
              <div className="h-0" />
            )}
          </section>

          {isConflicted ? (
            <aside className="grid min-h-0 content-start gap-3 overflow-auto app-scrollbar">
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
