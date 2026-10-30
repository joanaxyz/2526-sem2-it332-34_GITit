import { isRouteErrorResponse, useRouteError } from 'react-router-dom'

import { Button } from '@/shared/components/Button'

/**
 * The router's own error screen. An address with no route reaches it as a 404
 * (unknown paths stay unregistered rather than redirecting), and a route that
 * fails to load reaches it as any other error.
 */
export function RouteErrorPage() {
  const error = useRouteError()
  const notFound = isRouteErrorResponse(error) && error.status === 404
  if (!notFound) console.error('Route error', error)

  return (
    <main
      className="flex flex-col items-center justify-center gap-4 bg-background px-5 text-center"
      style={{ minHeight: '100svh' }}
    >
      <h1 className="text-xl font-semibold text-foreground">
        {notFound ? 'Page not found' : 'This page could not load.'}
      </h1>
      <p className="max-w-md text-sm text-muted-foreground">
        {notFound
          ? 'This address is not part of GIT it! anymore, or it was typed incorrectly.'
          : 'Something went wrong while opening this page. Your progress on the server is safe.'}
      </p>
      <Button onClick={() => window.location.assign('/')}>Back to GIT it!</Button>
    </main>
  )
}
