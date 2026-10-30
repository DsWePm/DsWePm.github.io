# homepage

Personal homepage: a rain-wet white slab split by a crack; below it, an urban
canyon of dense Walled-City facades. Scrolling drops you into the crack and you
land in the archive. Vue 3 for the page; the canyon is modelled and rendered
offline in Blender (Cycles), and three.js only composites the pre-renders
(depth parallax, rain ripples, ASCII decode).

## Develop

```bash
npm install
npm run dev
```

## Content

- Profile, skill files (the archive drawer), timeline, links: `src/data/profile.ts`
- Log posts: one Markdown file each in `src/content/log/`, projects in `src/content/projects/`.
  The file name is the URL (`/log/<name>`, `/projects/<name>`); the front matter fields are
  listed at the top of `src/data/posts.ts`.
- Categories for both (AI, CG, ...): `src/data/categories.ts`; an entry picks one with `category:`.
- In a post, `![caption](path)` takes an image, a video file (`.mp4` / `.webm`, plays inline) or a
  YouTube / Bilibili / Vimeo link (embedded player). Paths without `https://` are under `public/`.
  Links to other sites open in a new tab.
- Repositories: `GITHUB_USER=<login> npm run fetch:github` rewrites `src/data/repos.json`
  (the deploy workflow does this automatically for the repo owner); a project whose `repo:`
  matches one shows its stars and language.
- Dossier cards play their `video` (see `src/data/profile.ts`) when opened;
  cards without one show their ASCII plate. Blender's bundled FFmpeg can
  transcode your footage, so no separate ffmpeg install is needed.

## Rebuild the 3D assets

```bash
node tools/blender/fetch_textures.mjs   # once: CC0 Poly Haven textures + overcast HDRI (git-ignored)
npm run build:assets
```

The laundry and potted plants use three model packs that are not in the repo.
Unpack them (git-ignored) as `tools/blender/assets/tshirt/` (`22-t-shirt.zip`),
`tools/blender/assets/banjo/` (`PlantBanjoFig001.zip`) and `tools/blender/assets/zz/`
(`PlantZZ001.zip`); `tools/blender/props.py` cloth-simulates the shirts and sheets.

`build:assets` runs two steps:

1. `tools/blender/build_city.py [-- --seed 7]` models the scene and saves
   `tools/blender/out/city.blend` plus review renders `preview_top.jpg` / `preview_inside.jpg`.
2. `tools/blender/render_hero.py [-- --stills-only | --fall-only | --rain-only]` renders into `public/hero/`:
   `slab.jpg` and `canyon.jpg` (the two parallax layers), `depth.png` (depth + slab mask),
   `fall/f_####.webp` + `fall.json` (the free fall the page scrubs with the scroll: the camera
   rides a simulated falling body with air drag, the alley floor is rendered as a transparent
   hole the archive shows through, and the last frame is the moment of impact) and `rain.mp4`
   (a seamless rain loop with splashes, added over the still).
   The fall (60 fps) takes roughly an hour and a half on an RTX 2080.

The dev server ignores `public/hero/` while Blender writes into it, so restart
`npm run dev` after a render to pick up new files.

Demo footage for a dossier card: `blender -b tools/blender/out/city.blend -P tools/blender/render_clip.py`.

## Deploy

Push to `main`; `.github/workflows/deploy.yml` builds and publishes `dist/` with
GitHub Pages (Settings → Pages → Source: "GitHub Actions"). In this repository,
`Personal_Website`, the site is served at https://dswepm.github.io/Personal_Website/;
the workflow sets the base path from the repository name (a repo named
`<login>.github.io` would be served at the root). The build also writes
`404.html` (a copy of `index.html`) so links straight to `/log/...` work on Pages.

On a phone, `npm run dev:lan` serves the dev site over HTTPS on the local network
(phones only give the tilt sensor to secure pages).
