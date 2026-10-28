# Round One, On You — a CC0 Halloween comic

A 4-panel Halloween comic (2×2 grid, one 2080×2080 PNG) starring two Nouns:
a floating **Ghost Noun** and a **Pumpkin Noun**. The Ghost offers the
Pumpkin a single glowing sweet. The sweet transfers the soul — the Pumpkin
becomes the ghost, and in the final panel it floats and hands a fresh sweet
back to the original Ghost: **"Round one, on you."**

The panels, in order:

1. **"A treat for you."** — the Ghost (left, floating) offers the Pumpkin (right) a sweet.
2. **"Mmm. Spooky-good."** — the Pumpkin (right, the eater) eats the sweet.
3. **"Whoops."** — the soul transfers: the Ghost (left) fades, the Pumpkin (right) steadies.
4. **"Round one, on you."** — role reversal: the Pumpkin (left, now the ghost) offers the original Ghost (right) a fresh sweet.

## Characters — Nouns (CC0, public domain)

Both characters are Nouns, built from the collection's own public image data
(`image-data.json`) and rendered with the official Nouns SVG builder.

- CC0 statement (Nouns' own site): the Nouns playground's License page
  declares *"The logos, traits and every Noun generated on the playground
  are CC0 (Creative Commons Zero), meaning they are in the public domain
  and free to use for any purpose without restriction."*
  — https://nouns.wtf (License page)
- Art data: https://github.com/nounsDAO/nouns-monorepo
  (`packages/nouns-assets/src/image-data.json`, commit `2213eea`)
- Nouns: https://nouns.wtf

All other elements (backgrounds, moon, graveyard, the glowing sweet, speech
bubbles, lettering) are drawn in code with Pillow. Fonts are Liberation Sans
Bold/Regular, SIL Open Font License 1.1, **bundled with the source** in
`src/fonts/` (see `sources.md`). No paid or cloud image API was used; no
movie, TV, game or real-person material appears.

## Licence

The comic and its code are dedicated to the public domain under **CC0 1.0
Universal** — see `LICENSE`. That dedication covers the comic image and all
of our code, scenery and lettering. It does **not** re-licence the fonts.

The two bundled font files are **Liberation Sans** (Regular and Bold,
version 2.1.5) and are licensed **only** under the SIL Open Font License
1.1 — the terms in the first-party Liberation licence notice shipped at
`src/fonts/OFL.txt`. (The OFL explicitly allows a document created with the
fonts to be licensed under separate terms, which is what the CC0 dedication
of this comic relies on — but the font files themselves remain OFL-only;
they may not be treated as dual-licensed.)

## Re-render

```
python3 src/render.py --out comic.png
```

Needs Python 3 with Pillow and Node.js (to run the vendored Nouns SVG
builder, `src/sdk/nouns-sdk.cjs`). **No network access, no system fonts —
the fonts are bundled in `src/fonts/`.**

### Pinned setup route (reproducible from scratch)

The contract this route serves: the verifier accepts EXACTLY two output
hashes — reference A (the committed PNG) or reference B (the measured
cross-build pair) — and nothing else. There is no pixel-count or magnitude
fallback. To recreate a supported reference you must therefore install a
Pillow build whose wheel hash is pinned below, on a Python of the exact
pinned version, with the pinned Node.

**Pinned prerequisites (each is an assertion in the recipe below, not a
comment — the recipe exits nonzero on the first mismatch):**

| component | reference A (committed PNG) | reference B |
|-----------|-----------------------------|-------------|
| Python    | 3.11.15                     | 3.14.4      |
| Pillow    | 12.3.0 (exact wheel below)  | 12.1.1 (exact wheel below) |
| FreeType (as the pinned wheel reports) | 2.14.3 | 2.14.1 |
| zlib (interpreter: header constant AND runtime library) | 1.3.1 and 1.3.1 | 1.3.1 and 1.3.1 |
| Node.js   | v22.23.4                    | v22.23.4    |

Two zlib facts, kept separate:

1. The recipe asserts the **interpreter's** zlib, both
   `zlib.ZLIB_VERSION` (header constant) and `zlib.ZLIB_RUNTIME_VERSION`
   (the library actually linked into that Python build) — both pinned 1.3.1.
2. Pillow's PNG encoder does **not** use the interpreter's zlib: it is
   compiled into Pillow's `_imaging` extension and links the **system**
   `libz.so.1`. On the machine where both references were produced, that
   system library also reports 1.3.1. The recipe asserts that encoder
   library directly: it resolves the libz mapping of the installed
   `PIL._imaging` extension via `ldd`, calls `zlibVersion()` on that
   resolved library, and fails nonzero unless it reports **1.3.1**. That
   check asserts only this one thing — the version of the zlib library the
   encoder links — and nothing else.

The FreeType value a build reports depends on the FreeType linked into a
specific Pillow wheel, so a pinned Python + a pinned FreeType is the
executable statement of the requirement — not a prose comment.

- **Reference A wheel** (cp311, manylinux):
  `pillow-12.3.0-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`,
  sha256 `23d27a3e0307ec2244cc51e7287b919aa68d097504ebe19df4e76a98a3eea5bd`.
- **Reference B wheel** (cp314, manylinux):
  `pillow-12.1.1-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`,
  sha256 `a37691702ed687799de29a518d63d4682d9016932db66d4e90c345831b02fb4e`.

**Self-contained recipe (reference A, shown in full).** Runs from a fresh
copy of THIS repository (this directory) as the working directory — it
uses only files shipped here (`src/render.py`, the bundled fonts and data)
plus the pinned wheel URL. Every prerequisite above is asserted with a
hard failure; `set -e` makes any failed step abort with a nonzero exit, and
the cleanup at the end cannot hide an earlier failure because `set -e`
exits before reaching it:

```bash
set -e
# run from the repository root (the directory that contains src/)
WORKDIR=$(mktemp -d)                       # venv + output live here only, never in this tree
trap 'rm -rf "$WORKDIR"' EXIT
python3.11 -m venv "$WORKDIR/venvA"
printf 'https://files.pythonhosted.org/packages/3b/2d/ede717bc1144f63886c21fd349bb95860b0d1a21149ff16f2bb362b612b6/pillow-12.3.0-cp311-cp311-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl --hash=sha256:23d27a3e0307ec2244cc51e7287b919aa68d097504ebe19df4e76a98a3eea5bd\n' > "$WORKDIR/requirementsA.txt"
"$WORKDIR/venvA/bin/python" -m pip install --no-cache-dir --require-hashes -r "$WORKDIR/requirementsA.txt"
# every line below is an assertion; the first mismatch exits nonzero
"$WORKDIR/venvA/bin/python" -c "import sys;assert '.'.join(map(str,sys.version_info[:3]))=='3.11.15'"
"$WORKDIR/venvA/bin/python" -c "import PIL;assert PIL.__version__=='12.3.0'"
"$WORKDIR/venvA/bin/python" -c "import zlib;assert zlib.ZLIB_VERSION=='1.3.1'"
"$WORKDIR/venvA/bin/python" -c "import zlib;assert zlib.ZLIB_RUNTIME_VERSION=='1.3.1'"
# zlib of the encoder itself: the libz library PIL._imaging actually links (via ldd),
# interrogated on that library — asserts ONLY that one thing, 1.3.1
"$WORKDIR/venvA/bin/python" -c "import ctypes,subprocess,sys;import PIL._imaging as m;out=subprocess.run(['ldd',m.__file__],capture_output=True,text=True).stdout;path=[l.split('=>')[-1].split()[0] for l in out.splitlines() if 'libz.so' in l and '=>' in l][0];lib=ctypes.CDLL(path);lib.zlibVersion.restype=ctypes.c_char_p;print('encoder-zlib',lib.zlibVersion().decode(),'from',path);assert lib.zlibVersion().decode()=='1.3.1'"
"$WORKDIR/venvA/bin/python" -c "from PIL import features;assert features.version_module('freetype2')=='2.14.3'"
[ "$(node --version)" = "v22.23.4" ]
"$WORKDIR/venvA/bin/python" src/render.py --out "$WORKDIR/comic.png"
[ "$(sha256sum "$WORKDIR/comic.png" | cut -d' ' -f1)" = "4632d8e7894d51f26d86bc2d82871310306dac8f9ef7088effbc141e6199843a" ]
echo "RECIPE OK: reference A reproduced exactly (4632d8e7894d51f26d86bc2d82871310306dac8f9ef7088effbc141e6199843a)"
```

Reference B is the identical recipe with `python3.14`, the cp314 wheel
(`https://files.pythonhosted.org/packages/d1/ee/c85a38a9ab92037a75615aba572c85ea51e605265036e00c5b67dfafbfe2/pillow-12.1.1-cp314-cp314-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl`,
sha256 `a37691702ed687799de29a518d63d4682d9016932db66d4e90c345831b02fb4e`),
and the asserted values Python 3.14.4 / Pillow 12.1.1 / FreeType 2.14.1 /
zlib 1.3.1 (header and runtime) / Node v22.23.4, ending on the hash check
for `97b610aa17b3db61c61268bcb360ba72a0f8be36cd1592c53a9fab236a824972`.

**Private work-tree helpers (NOT part of this repository).** In the
authoring work tree — which also holds the verifier and the negative
controls — the same route is wrapped as `work/setupA.sh` / `work/setupB.sh`
around `work/setup_check.py`. Those scripts are development conveniences
for the authoring environment; they are not shipped here and are not
needed to follow the recipe above. The recipe is the complete public
route.

Reference B was reproduced exactly in a from-scratch venv built this way:
Python 3.14.4 / Pillow 12.1.1 / zlib 1.3.1 (header and runtime) / Node
v22.23.4 (FreeType as the pinned cp314 wheel reports: 2.14.1).

**What is actually demonstrated, and only that:**

- Reference A's environment reproduces the committed PNG **byte-for-byte**
  (verified: `4632d8e7894d51f26d86bc2d82871310306dac8f9ef7088effbc141e6199843a`);
  the verifier accepts that exact hash and the reference B exact hash, and
  nothing else.
- Reference B, the second independently reproduced build, differs from the
  committed PNG by **5,644 pixels, 5,632 of them with a channel delta greater
  than 1, and a maximum single-channel delta of 57**. This is the measured
  same-content difference of these two specific builds — recorded as an
  observation. It is NOT an acceptance rule: the verifier does not measure
  pixel deltas and does not accept unknown outputs on that basis.
- We do **not** claim what a third, unknown build will do, and we do **not**
  attribute the A/B difference solely to the Pillow version. The two
  environments differ in Python, Pillow and FreeType together; only the
  whole-environment byte-level comparisons above are demonstrated. No
  cross-runtime byte-identity beyond these two references is claimed, and
  cross-runtime byte identity is not required by the contract.

The committed PNG was produced by this exact renderer, and re-running it on
the producer's own runtime reproduces it **byte-for-byte**:

```
sha256 comic.png = 4632d8e7894d51f26d86bc2d82871310306dac8f9ef7088effbc141e6199843a
```

**What the verifier guarantees (and does not claim):**

- It re-renders and accepts the output ONLY if it is byte-identical to
  reference A or reference B. Any other output — a changed dialogue line, a
  changed label, a changed artwork colour, or an unknown third build — FAILS.
  Unknown output is reported as **unsupported / unverified**; it is neither
  labelled "proved content change" (which would be a false precision — we did
  not establish what it is) nor "same content in another build" (which was
  the r4 envelope defect).
- It therefore **rejects changed dialogue, changed labels, and changed
  artwork colour** — the tombstone-subtitle colour change that fooled the r4
  envelope now fails check 1 (see the negative-control probes in the work
  tree). It does not "confirm unchanged content while accepting changed
  dialogue"; no threshold of any kind remains in the acceptance path.

Full element-by-element sourcing is in `sources.md`.
