# GIT it! Frontend

React + TypeScript + Vite student-facing client for the GIT it! current-release MVP.

The app is feature-sliced under `src/features`, uses semantic CSS custom-property
tokens in `src/styles`, TanStack Query for server state, React Router for protected
routes, and React Flow for data-driven DAG rendering.

Local development:

```bash
npm ci
npm run dev
```

Production builds require `VITE_API_BASE_URL`. The reference nginx deployment uses
`/api` and includes an SPA fallback so nested-route refreshes resolve to `index.html`.
