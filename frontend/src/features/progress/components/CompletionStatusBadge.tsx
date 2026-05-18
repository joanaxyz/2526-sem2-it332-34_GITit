import { Badge } from '@/shared/components/Badge'

export function CompletionStatusBadge({ status }: { status: string }) {
  return <Badge variant={status === 'complete' ? 'default' : status === 'locked' ? 'outline' : 'blue'}>{status}</Badge>
}
