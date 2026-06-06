import { MessageSquareText } from 'lucide-react'

import type { PracticeSession } from '@/features/practice/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'

export function ContextualFeedbackPanel({ session, feedback }: { session: PracticeSession; feedback: string }) {
  if (!session.scaffolding.contextual_feedback) return null
  return (
    <Card className="h-full w-full min-w-0 shadow-none">
      <CardHeader className="p-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <MessageSquareText className="size-5 text-primary" />
          Contextual Feedback
        </CardTitle>
      </CardHeader>
      <CardContent className="p-3 pt-0">
        <p className="text-sm leading-6 text-muted-foreground">
          {feedback || 'After a simulator-processed command, a consequence summary appears here without revealing the answer path.'}
        </p>
      </CardContent>
    </Card>
  )
}
