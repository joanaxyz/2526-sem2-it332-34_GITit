import { MessageSquareText } from 'lucide-react'

import type { ScenarioSession } from '@/features/practice/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'

export function ContextualFeedbackPanel({ session, feedback }: { session: ScenarioSession; feedback: string }) {
  if (!session.scaffolding.contextual_feedback) return null
  return (
    <Card className="shadow-none">
      <CardHeader className="p-4">
        <CardTitle className="flex items-center gap-2 text-base">
          <MessageSquareText className="size-5 text-primary" />
          Contextual Feedback
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <p className="text-sm leading-6 text-muted-foreground">
          {feedback || 'After a simulator-processed command, a consequence summary appears here without revealing the answer path.'}
        </p>
      </CardContent>
    </Card>
  )
}
