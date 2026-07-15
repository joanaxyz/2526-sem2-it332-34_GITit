import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
    rules: {
      // These React Compiler-oriented rules are intentionally not enabled yet.
      // The project does not use the compiler, and the rules flag established
      // callback-ref and state-reset patterns that are valid in plain React.
      'react-hooks/immutability': 'off',
      'react-hooks/refs': 'off',
      'react-hooks/set-state-in-effect': 'off',
    },
  },
  {
    files: ['src/shared/git/commandCatalog/commandIcons.tsx'],
    rules: {
      // This module deliberately co-locates the icon component with the command
      // catalog and resolver helpers used across non-component modules.
      'react-refresh/only-export-components': 'off',
    },
  },
])
