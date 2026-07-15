import { Component, type ErrorInfo, type ReactNode } from 'react'

import { Button } from '@/shared/components/Button'

/**
 * Last-resort boundary above the router: a render crash anywhere in the tree
 * shows a recovery screen instead of unmounting to a white page. Route-level
 * errors are still handled by react-router; this only catches what escapes.
 */
export class AppErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('Unhandled render error', error, info.componentStack)
  }

  render() {
    if (!this.state.hasError) return this.props.children
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background px-6 text-center">
        <h1 className="text-xl font-semibold text-foreground">Something broke in the app.</h1>
        <p className="max-w-md text-sm text-muted-foreground">
          An unexpected error interrupted the page. Your progress on the server is safe -
          reload to pick up where you left off.
        </p>
        <Button onClick={() => window.location.assign('/')}>Reload GIT it!</Button>
      </div>
    )
  }
}
