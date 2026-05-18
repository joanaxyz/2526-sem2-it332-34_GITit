import { AlertCircle } from 'lucide-react'

export function ErrorState({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-5 text-sm leading-6 text-destructive">
      <div className="flex items-center gap-2 font-semibold">
        <AlertCircle className="size-4" />
        {title}
      </div>
      <p className="mt-2 text-destructive/85">{description}</p>
    </div>
  )
}
