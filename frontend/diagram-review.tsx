import React from 'react'
import { createRoot } from 'react-dom/client'
import { LiveDagPanel } from './src/shared/level/components/LiveDagPanel'
import './src/styles/globals.css'
import './src/styles/features/battle.css'
const snapshot = { repository_initialized: true, commits: [{ id: 'c1', message: 'Initial commit', parents: [] }, { id: 'c2', message: 'Update README', parents: ['c1'] }], branches: { main: 'c2' }, head: { type: 'branch', name: 'main', target: 'c2' }, staging: {}, working_tree: { 'README.md': 'changed' }, conflicts: [], remotes: { origin: 'https://example.test/repo.git' } }
createRoot(document.getElementById('root')!).render(<div style={{height:'95vh', padding:'1rem'}}><LiveDagPanel snapshot={snapshot} showRepositoryDetails className="flex h-full min-h-0 flex-col" contentClassName="h-full min-h-0 flex-1" /></div>)
