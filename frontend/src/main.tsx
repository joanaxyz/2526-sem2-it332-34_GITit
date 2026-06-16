import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { AppErrorBoundary } from '@/app/AppErrorBoundary'
import { AppProviders } from '@/app/providers'
import '@/styles/globals.css'
import '@/styles/features.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppErrorBoundary>
      <AppProviders>
        <App />
      </AppProviders>
    </AppErrorBoundary>
  </StrictMode>,
)
