import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { AppErrorBoundary } from '@/app/AppErrorBoundary'
import { AppProviders } from '@/app/providers'
import { initializePreferences } from '@/shared/preferences/preferences'
import '@/styles/globals.css'
import '@/styles/features/game-outcome.css'
import '@/styles/features/ambient.css'
import '@/styles/features/companion-loader.css'
import '@/styles/features/spinner.css'
import '@/styles/features/panels-stats.css'
import '@/styles/features/story-map-viewer.css'
import '@/styles/features/story-map.css'
import '@/styles/features/drills.css'
import '@/styles/features/shared-effects.css'
import '@/styles/features/charts.css'
import '@/styles/features/home.css'
import '@/styles/features/battle.css'
import '@/styles/features/battle/workspace-project-tree.css'
import '@/styles/features/authoring.css'
import '@/styles/features/shop.css'
import '@/styles/features/auth.css'
import '@/styles/features/settings.css'
import '@/styles/features/onboarding.css'
import '@/styles/features/admin.css'

initializePreferences()

// The boot paint in index.html fades itself out via CSS the moment #root has
// children, so the transition can only fire once React has actually rendered.
// Dropping the node on the way out leaves nothing behind, and if the
// transition never runs the element simply stays hidden as before.
const bootPaint = document.querySelector('.git-it-boot')
bootPaint?.addEventListener('transitionend', () => bootPaint.remove(), { once: true })

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppErrorBoundary>
      <AppProviders>
        <App />
      </AppProviders>
    </AppErrorBoundary>
  </StrictMode>,
)
