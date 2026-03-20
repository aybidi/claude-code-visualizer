# claude-code-visualizer

A scrollytelling visualization of your local [Claude Code](https://docs.anthropic.com/en/docs/claude-code) usage data. See your sessions, projects, tools, coding rhythm, and AI-generated insights — all rendered as an interactive, scroll-driven narrative in the style of [R2D3](http://www.r2d3.us/).

Styled to match Claude Code's dark terminal theme with JetBrains Mono and warm orange accents.

![Claude Code Visualizer](https://img.shields.io/badge/Claude_Code-Visualizer-e8855a?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiPjxwYXRoIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTVMMTIgMnoiLz48cGF0aCBkPSJNMiAxN2wxMCA1IDEwLTUiLz48cGF0aCBkPSJNMiAxMmwxMCA1IDEwLTUiLz48L3N2Zz4=)

## What You'll See

The visualization walks you through 6 interactive sections:

1. **The Timeline** — Daily message activity as an area chart with annotated peaks
2. **Your Projects** — Circle-packed bubble chart showing where you spent your time
3. **The Tool Belt** — Horizontal bars of Claude's tool usage (Read, Bash, Edit, etc.)
4. **Your Rhythm** — Day-of-week x hour-of-day heatmap revealing your coding patterns
5. **Your Intentions** — Goal categories and session types from `/insights` analysis
6. **How It Went** — Outcome success rates, friction points, and helpfulness ratings

Each section uses scroll-triggered animations — the visualization updates as you read the narrative text beside it.

https://github.com/user-attachments/assets/4f194751-f81f-473f-aa35-3203a7c414d6


## Quick Start

```bash
# 1. Clone
git clone git@github.com:aybidi/claude-code-visualizer.git
cd claude-code-visualizer

# 2. Generate your data (reads from ~/.claude/)
python3 process_data.py

# 3. Serve locally and open
python3 -m http.server 8765
# Visit http://localhost:8765
```

That's it. No dependencies, no `npm install`, no build step.

## Requirements

- **Python 3.7+** (standard library only — no pip packages needed)
- **Claude Code** installed with some session history in `~/.claude/`
- A modern browser (Chrome, Firefox, Safari, Edge)

## How It Works

### Data Pipeline

`process_data.py` reads your local Claude Code data from three sources:

| Source | Path | What it contains |
|--------|------|-----------------|
| Session logs | `~/.claude/projects/*/` | JSONL files with every message, tool call, and token count |
| Insight facets | `~/.claude/usage-data/facets/` | Per-session goal analysis, outcomes, friction, satisfaction |
| Session metadata | `~/.claude/usage-data/session-meta/` | Lines of code, languages, response times, duration |

It aggregates everything into a single `data.json` with:
- Timeline (daily message/token counts)
- Project breakdown (messages, sessions, top tools per project)
- Tool usage with per-project distribution
- Model usage (Opus vs Sonnet split)
- Hourly/weekly activity heatmap
- Session duration distribution
- Insight facets (goals, outcomes, helpfulness, friction, session types)

### Visualization

`index.html` is a self-contained single page that loads `data.json` and renders everything with:
- **D3.js v7** (loaded from CDN) for all charts
- **IntersectionObserver** for scroll-triggered transitions
- **CSS sticky positioning** for the scrollytelling layout

No framework, no bundler, no node_modules.

## Privacy

All data stays local. Nothing is sent anywhere.

- `process_data.py` reads only from `~/.claude/` on your machine
- `data.json` is generated locally and gitignored by default
- The page loads D3.js from CDN — that's the only network request
- No analytics, no tracking, no telemetry

If you want to go fully offline, download d3.v7.min.js locally and update the `<script src>` in `index.html`.

## Generating Insight Data

The "Your Intentions" and "How It Went" sections use data from Claude Code's `/insights` command. If those sections appear empty:

```bash
# Run this inside Claude Code first
/insights
```

This generates analysis files in `~/.claude/usage-data/` that `process_data.py` will pick up on the next run.

## Customization

### Colors

All colors are defined as CSS custom properties in `:root`. The default theme matches Claude Code's terminal:

```css
--bg: #1a1b26;        /* deep dark background */
--accent: #e8855a;    /* Claude's warm orange */
--cyan: #7dcfff;      /* terminal cyan */
--green: #9ece6a;     /* success green */
--orange: #e0af68;    /* warning amber */
--pink: #f7768e;      /* error/highlight pink */
--purple: #bb9af7;    /* purple accent */
```

The D3 chart palette is in the `COLORS` array in the `<script>` block.

### Adding Sections

Each scrollytelling section follows the same pattern:

```html
<section class="scroll-section" id="sec-YOURNAME">
  <div class="scroll-text">
    <div class="step" data-step="0" id="yn-step-0"></div>
    <div class="step" data-step="1" id="yn-step-1"></div>
  </div>
  <div class="scroll-graphic">
    <div class="graphic-container" id="viz-YOURNAME"></div>
  </div>
</section>
```

Then add a `createYourName(data)` function that returns a step updater, and register it in the `updaters` object.

## Built With

- [D3.js](https://d3js.org/) — Data visualization
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/) — Terminal font
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — Built entirely with Claude Code

## License

MIT
