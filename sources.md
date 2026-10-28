# Sources — "Round One, On You" (CC0 Halloween comic)

Everything used in this comic, with source and licence. No movie, TV, game,
meme or real-person material is used. No paid or cloud image API was used —
every pixel was produced locally from the sources below.

## Characters (Nouns — CC0, public domain)

Both characters are Nouns, assembled from the collection's own public image
data and rendered with the official Nouns SVG builder. CC0 status is
declared by Nouns' own site (first-party, saved with the claim evidence
outside this public tree):

> "The logos, traits and every Noun generated on the playground are CC0
> (Creative Commons Zero), meaning they are in the public domain and free to
> use for any purpose without restriction."

- **Ghost Noun** (the trickster, floating, slightly translucent):
  `body-blue-sky` + `head-ghost-B` + `glasses-square-black`
- **Pumpkin Noun** (who eats the sweet and becomes the new ghost):
  `body-orange` + `head-pumpkin`

Art data (RLE-encoded layer selections + palette), first-party:
- File: `packages/nouns-assets/src/image-data.json`
- Repo: https://github.com/nounsDAO/nouns-monorepo
- Commit: `2213eea1c15f331f786784c2621d53bdecf907e2`
- Local copy: `src/data/image-data.json` (sha256
  `4493db539e9ab540b7af0aa011872734dfad9b6adb4309d94a014aef01d60662`).
  **Normalization note:** the shipped copy is *semantically* identical to
  the upstream file (same keys, same trait records — the five traits used
  here match upstream in their `data` fields) but is stored with different
  JSON whitespace, so the whole-file hash differs from the upstream bytes
  (upstream
  `a03f22b7838b35fdf0332617c9b8e2b032eb26cf1632afbefb200fec64c4bc20`). It
  is NOT a byte-identical copy; it is a normalized copy of the same data.
  A **raw fetch of the upstream file is retained with the claim evidence** at
  `evidence/nouns-image-data-upstream-2213eea-raw.json` (outside this public
  tree; sha256
  `a03f22b7838b35fdf0332617c9b8e2b032eb26cf1632afbefb200fec64c4bc20`), and
  `verify.sh` checks that (a) the retained raw file hashes to the pinned
  upstream value and (b) it **parses equal** to the shipped
  `src/data/image-data.json` (full-document comparison, including the five
  trait records, palette and bgcolors).

Renderer (build-time tool only, never shipped as art):
- `@nouns/sdk` v1.2.0 `buildSVG` — vendored as `src/sdk/nouns-sdk.cjs`.
  **ESM-to-CJS adaptation:** the file is the official `dist/index.js`
  implementation (verified identical to
  https://unpkg.com/@nouns/sdk@1.2.0/dist/index.js up to the export
  suffix), with its trailing ESM `export{...}` + source-map line **replaced**
  by a CommonJS `module.exports = { buildSVG, PNGCollectionEncoder };` line
  so it can be `require()`d by the Node one-liner in `render.py`. It is
  not merely an appended line; the suffix was swapped.
- The bundle is self-contained (zero runtime dependencies), so no
  `node_modules` ships.

## Everything else (ours, dedicated to CC0 by submission)

- **Backgrounds** (night sky gradient, stars, moon, graveyard ground, two
  tombstones reading "RIP est. 2020"): drawn in code with Pillow in
  `src/render.py` (`sky`, `stars`, `moon`, `ground`, `tombstone`).
- **The glowing sweet** (the treat that transfers the soul): drawn in code
  with Pillow in `src/render.py` (`treat`). It is drawn *after* both
  figures in every panel, so it is never hidden behind a character.
- **Motion trail** (the sweet being handed over): drawn in code
  (`lift_lines`, `trail`).
- **Speech bubbles and all lettering**: drawn in code (`bubble`); text:
  1. "A treat for you."  2. "Mmm. Spooky-good."  3. "Whoops."
  4. "Round one, on you."
  Each bubble's tail is pointed at the character who speaks in that panel.
- **Character name labels** ("GHOST", "PUMPKIN", and in panel 4
  "PUMPKIN (NOW A GHOST)"): drawn in code (`label`), below each figure's
  feet, so the recurring cast is unambiguous in every panel.
- **Translucency** of the Ghost (alpha 235/255) and of the fading Ghost in
  panel 3 (alpha 110/255): code (`place_noun`).

## Fonts (OFL — bundled, not system)

- **Liberation Sans Bold** — `src/fonts/LiberationSans-Bold.ttf`
  (sha256 `b72c65e551d653b54217ffad0d1454ce0657e4e8d4a28bcc79e0acd2598f4bf3`)
- **Liberation Sans Regular** — `src/fonts/LiberationSans-Regular.ttf`
  (sha256 `075e71be4c58beda172ecb574a799308f04c3d054c6a5b7434954d3b0f1b28d8`)
- **Licence:** SIL Open Font License 1.1. The first-party Liberation licence
  notice (verbatim, from the liberationfonts project's own `LICENSE` file,
  `main` == tag `2.1.5`) is bundled at `src/fonts/OFL.txt` (sha256
  `93fed46019c38bbe566b479d22148e2e8a1e85ada614accb0211c37b2c61c19b`).
  It carries the Liberation copyright notices — Google 2010 (Arimo/Tinos/
  Cousine) and Red Hat 2012 (Reserved Font Name "Liberation") — so it
  matches the bundled font files.
- **Font metadata (parsed from the bundled TTFs):** `verify.sh` check 9e
  parses each font's `name` table (struct-based, no PIL/FreeType dependency)
  and asserts the EXACT recorded values: family **Liberation Sans** (nameID
  1), version **Version 2.1.5** (nameID 5), copyright exactly
  **"Digitized data copyright (c) 2010 Google Corporation."** +
  **"Copyright (c) 2012 Red Hat, Inc."** (nameID 0), and licence
  **"Licensed under the SIL Open Font License, Version 1.1"** (nameID 13).
  It asserts each field's full value — including the copyright years and the
  licence version — not merely a substring. A year mutation (2010/2012 to
  2099) in an isolated font copy is rejected (negative-control probe in the
  work tree).
- **Licensing evidence (first-party):** the liberationfonts project's own
  `LICENSE` (the same text shipped as `OFL.txt`) states the fonts are
  licensed under SIL OFL 1.1 with Reserved Font Name Liberation; upstream
  source at github.com/liberationfonts. Liberation is a distinct
  OFL-licensed family (Arimo metric-compatible with Arial) — it is NOT
  Bitstream Vera / DejaVu, which carries the Bitstream Vera licence, and we
  do not relabel it as anything else.
- Because the fonts are bundled in `src/fonts/`, the render does not depend
  on any host's system font directory; `render.py` loads them by relative
  path.

## Determinism

`src/render.py` uses no randomness and no network access, and loads only
bundled files (fonts in `src/fonts/`, Nouns art in `src/data/`, the vendored
SDK in `src/sdk/`). Re-running it in the **recorded producer environment**
(Python 3.11.15, Pillow 12.3.0, FreeType 2.14.3, zlib 1.3.1, Node v22.23.4 —
see `README.md`) reproduces the committed `comic.png` byte-for-byte:

```
sha256 deliver/comic.png = 4632d8e7894d51f26d86bc2d82871310306dac8f9ef7088effbc141e6199843a
```

We also reproduced a second, independent build (Python 3.14.4, Pillow 12.1.1,
FreeType 2.14.2-class) and measured its output against the committed PNG:
5,644 changed pixels, 5,632 with a channel delta greater than 1, maximum
single-channel delta 57 (that build's sha256 is `97b610aa…`, in `README.md`).
This is the only *other* build we have actually rendered. It does not tell us
what an arbitrary third build will produce, and we do not claim otherwise.
The measured numbers are an **observation** of this one same-content pair,
not an acceptance rule: `verify.sh` accepts ONLY the committed bytes or that
known build's exact bytes (reference A or reference B), and fails on anything
else. Unknown output is reported as unsupported/unverified — no pixel-count
or magnitude threshold participates in acceptance.

## Panels (exactly 4, 2×2 grid, one 2080×2080 PNG)

- Panel 1 (top-left):  x 40–1020,   y 40–1020   — "A treat for you."
- Panel 2 (top-right): x 1060–2040, y 40–1020   — "Mmm. Spooky-good."
- Panel 3 (bottom-left):  x 40–1020,   y 1060–2040 — "Whoops."
- Panel 4 (bottom-right): x 1060–2040, y 1060–2040 — "Round one, on you."
  (panel size 980×980, margin 40, gutter 40 — constants in render.py)
