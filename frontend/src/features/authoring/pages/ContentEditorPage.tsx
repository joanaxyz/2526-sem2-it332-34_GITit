import { BattleStageEditor } from '@/features/authoring/components/BattleStageEditor'
import { ChapterLessonPagesEditor } from '@/features/authoring/components/ChapterLessonPagesEditor'
import { ContentDestinationSection } from '@/features/authoring/components/content-editor/ContentDestinationSection'
import { ContentEditorDiagnostics } from '@/features/authoring/components/content-editor/ContentEditorDiagnostics'
import { ContentEditorHeader } from '@/features/authoring/components/content-editor/ContentEditorHeader'
import { ContentMetadataSection } from '@/features/authoring/components/content-editor/ContentMetadataSection'
import { LevelsEditor } from '@/features/authoring/components/LevelsEditor'
import { useContentEditorController } from '@/features/authoring/hooks/useContentEditorController'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function ContentEditorPage() {
  const {
    form,
    setForm,
    sourceKey,
    isNew,
    isOfficialMode,
    chapters,
    commandFormOptions,
    isLoading,
    loadError,
    busy,
    isDirty,
    canUseActions,
    officialDestinationMissing,
    formError,
    validationErrors,
    save,
    validate,
    publish,
    createChapter,
  } = useContentEditorController()

  if (isLoading) return <LoadingState label="Loading content" variant="page" />
  if (loadError) return <ErrorState title="Could not load content" description={loadError} />

  const selectedChapterId = isOfficialMode ? form.officialChapterId : form.chapterId

  return (
    <div className="author-page">
      <ContentEditorHeader
        kind={form.kind}
        title={form.title}
        isNew={isNew}
        busy={busy}
        isDirty={isDirty}
        canUseActions={canUseActions}
        officialDestinationMissing={officialDestinationMissing}
        onSave={save}
        onValidate={validate}
        onPublish={publish}
      />
      <ContentDestinationSection
        isOfficialMode={isOfficialMode}
        chapters={chapters}
        selectedChapterId={selectedChapterId}
        createChapterDisabled={busy}
        onDestinationChange={(id) => setForm({
          ...form,
          chapterId: isOfficialMode ? null : id,
          officialChapterId: isOfficialMode ? id : null,
        })}
        onCreateChapter={createChapter}
      />
      <ContentMetadataSection
        sourceKey={sourceKey}
        kind={form.kind}
        title={form.title}
        slug={form.slug}
        summary={form.summary}
        commandFamily={form.commandFamily}
        difficulty={form.difficulty}
        tags={form.tags}
        visibility={form.visibility}
        onTitleChange={(title) => setForm({ ...form, title })}
        onSlugChange={(slug) => setForm({ ...form, slug })}
        onSummaryChange={(summary) => setForm({ ...form, summary })}
        onCommandFamilyChange={(commandFamily) => setForm({ ...form, commandFamily })}
        onDifficultyChange={(difficulty) => setForm({ ...form, difficulty })}
        onTagsChange={(tags) => setForm({ ...form, tags })}
        onVisibilityChange={(visibility) => setForm({ ...form, visibility })}
      />

      {form.kind !== 'lesson' ? (
        <BattleStageEditor
          value={form.battleStage}
          onChange={(battleStage) => setForm({ ...form, battleStage })}
        />
      ) : null}
      {form.kind === 'lesson' ? (
        <ChapterLessonPagesEditor
          pages={form.pages}
          onChange={(pages) => setForm({ ...form, pages })}
        />
      ) : (
        <LevelsEditor
          kind={form.kind}
          levels={form.levels}
          onChange={(levels) => setForm({ ...form, levels })}
          commandFormOptions={commandFormOptions}
        />
      )}

      <ContentEditorDiagnostics
        form={form}
        formError={formError}
        validationErrors={validationErrors}
      />
    </div>
  )
}
