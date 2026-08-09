# design-sync notes — claude-code-visualizer

## What this repo is, and why the sync looks unusual

This is **not** a JS design-system repo. It is a Python data processor
(`process_data.py`) plus one monolithic `index.html` containing a `<style>`
block and imperative D3 v7 scrollytelling. There is no `package.json`, no
`dist/`, no Storybook, and no React components anywhere.

So this is a **tokens-only** sync: the palette, typography, and stylesheet ship;
zero components do. The Claude Design agent gets the *look* but still composes
from its own generic components. That is the ceiling for this repo — do not
"fix" it by authoring components, which would mean inventing a design system
rather than syncing one.

The converter supports this natively — it is not a workaround. Zero PascalCase
exports plus a `cssEntry` puts `lib/source-kit.mjs` into tokens-only mode
(`[ZERO_MATCH] … treating as tokens-only DS`), and `package-validate.mjs`
reports `tokens-only DS — no component previews` instead of failing.

## The shim package

`.design-sync/ds/` is a nominal npm package that exists only to give the
converter something to point at:

- `dist/index.d.ts` is `export {};` — **the empty export list is what triggers
  tokens-only mode.** Never add a PascalCase export here.
- `css/base.css` is the real payload: the whole visual identity.
- `react`/`react-dom` are installed only so the bundler can populate `_vendor/`.

Build and validate (both must be run separately, checking each exit code):

```bash
node .ds-sync/package-build.mjs --config .design-sync/config.json \
  --node-modules .design-sync/ds/node_modules --entry .design-sync/ds/dist/index.js --out ./ds-bundle
node .ds-sync/package-validate.mjs ./ds-bundle
```

## Decisions made, with reasons

- **Tokens are inlined at the top of `css/base.css`, not kept in a separate
  `tokens/` directory.** This was a real bug caught during the first build:
  `copyTokens()` in `lib/css.mjs` returns immediately unless `tokensPkg` names a
  package inside `node_modules`, so `tokensGlob: "tokens/*.css"` silently copied
  nothing and the emitted `tokens/` was empty. Rendered designs receive only
  `styles.css`'s `@import` closure, so every `var(--*)` would have been
  undefined and every design unstyled. `cfg.tokensGlob` was removed.
  **Verify after any build:** validate must print `tokens: 18 defined`.
- **JetBrains Mono stays a remote Google Fonts `@import`** rather than vendored
  woff2 files, matching how `index.html:8` loads it. Validate reports
  `[FONT_REMOTE]`, which is informational. If self-contained fonts are ever
  wanted, JetBrains Mono is OFL and redistributable — vendor via
  `cfg.extraFonts`.
- **`--no-render-check` was offered and declined**; playwright + chromium were
  installed instead, and the render check ran clean at `0/0 previews`.

## Known render warns

None. The final validate run exits 0 with no warnings at all.

## Re-sync risks

- **`.design-sync/ds/css/base.css` is a manual copy of `index.html`'s `<style>`
  block and will silently drift.** Nothing detects this — not the build, not the
  validator, not the anchor. **Before any re-sync, diff the two.** As of this
  sync it mirrors `index.html:10-272` verbatim (tokens plus 73 rules), with only
  the tokens relocated to the top and the font `<link>` converted to an
  `@import`.
- **`.design-sync/conventions.md` enumerates real class and token names** and is
  inlined into the design agent's system prompt. If `index.html`'s CSS gains,
  renames, or drops a class, the header goes stale and the agent will confidently
  emit vocabulary that no longer resolves. Re-run the validation pass — grep every
  class and token named in the header against `ds-bundle/_ds_bundle.css` — and
  fix or cut anything that no longer verifies. Do not rewrite the file wholesale;
  it is human-editable and its content belongs to its authors.
- **`[DTS_REACT] @types/react not found`** appears in the build log. It is
  harmless here (zero components means nothing has props to extract) and was
  deliberately not fixed. It would matter only if this ever stopped being
  tokens-only.
- The build assumes node 24 / npm 11 and network access for the npm installs.

## If someone later wants real components

That is a separate engagement: author a React library from `index.html`'s
patterns (stat tiles, terminal bars, section headers, heatmap, tooltip), give it
a build, and re-sync as a normal `package` shape. It is not a design-sync task
and should not be done silently as part of one.
