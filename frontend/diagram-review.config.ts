import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
export default defineConfig({plugins:[react()], cacheDir:'node_modules/.vite-diagram-review', resolve:{alias:{'@':path.resolve(import.meta.dirname,'src')}}})
