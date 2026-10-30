---
title: Homepage / Rain-city crack
date: 2026-10-30
category: cg
status: active
demo: https://dswepm.github.io/Personal_Website/
tags: vue, three.js, blender, cycles
summary: This site itself: a Kowloon Walled City canyon generated procedurally in Blender, a free fall pre-rendered in Cycles, brought back to the web with Vue 3 and three.js.
cover: hero/slab.jpg
---

A personal homepage. It opens on a white slab with a crack in it; scroll down and you fall into the canyon of buildings beneath the crack, then land in the archive.

![The homepage still: the crack and the canyon below](hero/slab.jpg)

## Parts

- **Blender scripts**: `build_city.py` generates the whole city; `render_hero.py` renders the stills, the 254-frame fall and the rain loop
- **The web page**: Vite + Vue 3 + TypeScript, with three.js handling the homepage's parallax, ripples and frame sequence
- **Content**: logs and projects are Markdown files sharing one detail-page template

## Rebuilding the assets

```bash
npm run build:assets
```

The full render takes about 1.5 hours on an RTX 2080.

The making-of is in the [Falling into the canyon](/log/falling-into-the-canyon) log.
