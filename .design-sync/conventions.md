# claude-code-visualizer — how to build with this design system

This is a **tokens-only** design system: it ships a palette, a typeface, and a
stylesheet — **no React components**. Build your own markup and style it with
the classes and custom properties below. Do not expect `window.CCVis` to
contain components; it is deliberately empty.

The look is a dark terminal: Tokyo-Night surfaces, a warm orange accent,
JetBrains Mono everywhere, and lowercase text.

## Setup

There is no provider and no wrapper component. Loading `styles.css` is the
whole setup — it `@import`s `_ds_bundle.css`, which carries the tokens, the
reset, the base `body` rules, and every class below.

**The one gotcha that will bite you:** the base stylesheet sets
`text-transform: lowercase` on `body`. Every piece of text renders lowercase
unless you opt out with the `preserve-case` class:

```html
<span class="preserve-case">JetBrains Mono</span>
```

Use `preserve-case` for proper nouns, code, file paths, and user data. It
applies to the element and all its descendants. This is intentional brand
styling, not a bug — do not override it globally.

Two other base rules to know: `* { margin: 0; padding: 0; box-sizing:
border-box; }` (so all spacing is yours to add), and `body` sets the mono font
stack, `var(--text)` on `var(--bg)`, and `line-height: 1.7`.

## Styling idiom

Plain CSS classes and `var(--*)` custom properties. **No utility classes, no
style props, no theme objects.** For your own layout glue, write ordinary CSS
that references the tokens — never hardcode a hex value that a token already
names.

### Tokens

Surfaces (darkest → lightest): `--bg-darker` `#0f0f14`, `--bg-dark` `#16161e`,
`--bg` `#1a1b26` (page default), `--bg-current` `#292e42` (raised/hover).

Text: `--text` `#c0caf5` (body), `--text-muted` `#565f89` (secondary, axis
labels), `--text-light` (alias of `--text-muted`).

Accent: `--accent` `#e8855a` (the Claude Code orange — headings' eyebrow text,
emphasis, key values), `--accent-light` `#f0a878`, `--accent-glow`
`rgba(232,133,90,0.15)`. `--border` `#292e42` matches `--bg-current`.

Categorical hues for data: `--cyan` `#7dcfff`, `--green` `#9ece6a`, `--orange`
`#e0af68`, `--pink` `#f7768e`, `--purple` `#bb9af7`. `--red` and `--yellow` are
aliases of `--pink` and `--orange`.

All 18 are defined in the stylesheet. `--bg-dark`, `--text-light`, `--border`,
`--accent-light`, `--accent-glow`, `--purple`, `--red`, and `--yellow` are
palette entries the source page does not currently use — they are available and
on-brand.

### Class families

- **Page sections** — `hero` (full-viewport gradient with `hero-label`,
  `hero-subtitle`, `hero-stats`, `hero-meta`), `section-intro` (add `visible`
  to fade it in) with `section-num` for the eyebrow number, `outro` with
  `outro-grid` / `outro-card` (child `val` and `lbl`) / `outro-subtitle` /
  `outro-note`.
- **Stats** — `stat-card` wrapping `stat-value` (gradient-filled numerals,
  `tabular-nums`) and `stat-label`.
- **Scrollytelling** — `scroll-section` splits into `scroll-text` and a sticky
  `scroll-graphic` holding `graphic-container`; narrative beats are `step`
  (add `active` to bring one to full opacity).
- **Inline emphasis** — `hl` (accent), `hl-pink`, `hl-green`, `hl-amber`.
- **Charts (SVG)** — `axis`, `grid`, `chart-title`, `bar-label`, `bar-value`,
  `bar-prompt`, `bar-blocks`, `heatmap-label`, `annotation-line`,
  `annotation-text`. These style SVG `fill`/`stroke`, so apply them to SVG
  nodes, not divs.
- **Chrome** — `tooltip` (add `visible` to show), `loading-screen`,
  `scroll-hint`, `term-cursor` (blinking block cursor).

## Where the truth lives

Read `styles.css` and the `_ds_bundle.css` it imports before styling anything.
They are the complete, authoritative source — every class and token above is
defined there, and there is nothing else to consult.

## Idiomatic example

```html
<div class="hero">
  <div class="hero-label">your claude code story</div>
  <h1>2,847 messages</h1>
  <div class="hero-subtitle">across 14 projects</div>
  <div class="hero-stats">
    <div class="stat-card">
      <div class="stat-value">312</div>
      <div class="stat-label">sessions</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">1.2m</div>
      <div class="stat-label">tokens</div>
    </div>
  </div>
  <p>most of it in <span class="hl preserve-case">claude-code-visualizer</span></p>
</div>
```
