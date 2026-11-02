import { ArrowLeft } from 'lucide-react'
import { isRouteErrorResponse, useRouteError } from 'react-router-dom'

import gitLogoImage from '@/assets/images/git-it-logo-arcane.webp'
import { Button } from '@/shared/components/Button'

import './route-error.css'

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
    <main className="route-error">
      <header className="route-error__header">
        <a className="route-error__brand" href="/" aria-label="GIT it! home">
          <img src={gitLogoImage} alt="" width={900} height={305} />
        </a>
      </header>

      <section className="route-error__content" aria-labelledby="route-error-title">
        <div className="route-error__scene">
          {notFound ? <span className="route-error__digit" aria-hidden="true">4</span> : null}
          <div className="route-error__portal">
            <img
              className="route-error__mascot"
              src="/mascot/portrait.png"
              alt="Git-It, the GIT it! mascot"
              width={1122}
              height={1402}
              draggable={false}
            />
          </div>
          {notFound ? <span className="route-error__digit" aria-hidden="true">4</span> : null}
        </div>

        <p className="route-error__status">
          {notFound ? '404 / Off the map' : 'Journey interrupted'}
        </p>
        <h1 id="route-error-title" className="route-error__title">
          {notFound ? 'Page not found' : 'This page could not load.'}
        </h1>
        <p className="route-error__description">
          {notFound
            ? 'This page may have moved, or the address may be incorrect. Let’s get you back on track.'
            : 'Something went wrong while opening this page. Your progress on the server is safe.'}
        </p>
        <Button className="route-error__home" onClick={() => window.location.assign('/')}>
          <ArrowLeft size={16} aria-hidden="true" />
          Back to GIT it!
        </Button>
      </section>
    </main>
  )
}
