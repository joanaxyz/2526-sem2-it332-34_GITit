import { TutorWindow } from './TutorWindow'

/** Help scoped to the open command guide, in its own window beside the guide card; it closes with the guide. */
export function GuideTutor({ runId, teachingKey, usageForm, guideToken }: { runId: number; teachingKey: string; usageForm: string; guideToken: string }) {
  return <TutorWindow workspace context={{ surface: 'command_guide', run_id: runId, teaching_key: teachingKey, usage_form: usageForm, guide_token: guideToken }} />
}
