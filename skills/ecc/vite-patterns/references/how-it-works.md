---
skill_id: 4f9625493343
usage_count: 1
last_used: 2026-06-16
---
## How It Works

- **Dev mode** serves source files as native ESM — no bundling. Transforms happen on-demand per module request, which is why cold starts are fast and HMR is precise.
- **Build mode** uses Rolldown (v7+) or Rollup (v5–v6) to bundle the app for production with tree-shaking, code-splitting, and Oxc-based minification.
- **Dependency pre-bundling** converts CJS/UMD deps to ESM once via esbuild and caches the result under `node_modules/.vite`, so subsequent starts skip the work.
- **Plugins** share a unified interface across dev and build — the same plugin object works for both the dev server's on-demand transforms and the production pipeline.
- **Environment variables** are statically inlined at build time. `VITE_`-prefixed vars become public constants in the bundle; everything unprefixed is invisible to client code.