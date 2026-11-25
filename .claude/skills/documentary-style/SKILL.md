---
name: documentary-style
description: Build a cinematic, code-rendered documentary motion video — one continuous camera move over a lamp-lit 3D tabletop (map, desk, documents, photos as physical objects) synced to a voiceover and rendered to MP4. Use when the user asks for a documentary/explainer/history reel "in documentary style", a tabletop or war-table map video, an investigation-board video, or a video built entirely from code (no AI video generators, no stock footage) from a script, voiceover and reference photos.
---

# Documentary style

A short-form historical reel where every frame is rendered by code: a three.js
scene of a dark walnut desk under one warm lamp, real maps/photos/documents
lying on it as physical objects, and a single camera that glides, pushes in and
pulls back without ever cutting. Text the narrator says appears once, on a real
document or inked onto the world, landing exactly on the spoken word.

Reference look: tilted war-table / tabletop map shots, shallow depth of field,
lamp pool on the hero with everything else falling into shadow, red pins and
string, aged sepia paper, film grain, vignette.

## Workflow

1. **Collect inputs.** Script + voiceover audio (the master clock), real
   photos/documents/maps, style references, format (default 21:9 3840×1646 30fps).
   Ask for anything missing — especially the voiceover. Uploads land in
   `/root/.claude/uploads/<session>/`; verify every listed file actually arrived.
2. **Write a beat table before building:** time → narration → ONE hero →
   on-screen text. Show it and ask what's unclear.
3. **Measure the voice.** Phrase edges with
   `ffmpeg -i vo.mp3 -af silencedetect=noise=-38dB:d=0.18 -f null -`; then check
   key-word onsets with an RMS envelope (20–30 ms windows, see below). Put all
   cue times in `cues.js`; every animation keys off these names. Video length =
   voice length (+≤1 s hold if the user allows).
4. **Build the world** from `template/film.html` (copy `template/` into a build
   folder). Swap assets, layout, cues, beats.
5. **QA stills** at 1600 wide for every beat (`scripts/stills.js`), contact-sheet
   them, fix clutter/readability/overlaps. Then a full 1280 preview with audio
   (`scripts/render.js`), 1 fps contact sheet + frame strips of fast moves.
6. **Send the preview**, take notes, then render the final 4K (slow: budget
   ~10× the 1280 preview time).

## Storytelling rules (most important)

1. One idea per line, ONE hero per line; the lamp follows the hero and
   everything else dims back.
2. Every phrase appears on screen once — on a real document OR typed/inked,
   never both. If a real map already prints "Abbottabad", circle it; don't type it.
3. No filler text: body copy is soft grey or simply the real document, dimmed
   and out of focus.
4. Big type: a hero word should be ≥7–10% of frame height. If the printed label
   on a real asset is small, push the camera close and circle it in red marker.
5. Less is more: no decorative tape, stamps, memos or labels that aren't story.
6. Visuals land on the word: object drops/pin slams/highlighter sweeps/marker
   circles start or land at the measured cue.

## Look recipe (three.js r160, see template)

- Renderer: PCFSoft shadows (4096 map), ACES tone mapping, exposure ~0.75,
  sRGB output, faint RoomEnvironment (env intensity ~0.07), FogExp2 haze.
- One warm SpotLight (0xffc48a, penumbra ~0.95) positioned up-left of a target
  that follows the camera target with a short lag → the "lamp pool".
  Hemisphere fill ≤0.05. Additive dust motes in the beam.
- Objects with real thickness: paper is a subdivided plane with noise
  displacement + edge curl + bump map; prints have a white border; pins are a
  metal needle + clearcoat sphere; red string is a TubeGeometry revealed with
  `setDrawRange`; discs are cylinders with the photo on the top cap (alphaTest).
- Ink on paper: draw into the texture's canvas (multiply blend) and set
  `needsUpdate` only when the drawn state changes.
- Post chain: scene → HalfFloat RT with DepthTexture → depth-based DOF (focus =
  camera-to-target distance) → camera motion blur (reproject depth with the
  previous half-frame view-projection) → TexturePass → UnrealBloom (0.2) →
  **OutputPass → grade** (warm tint, gentle S-curve, vignette, chromatic fringe,
  grain, fade).
- Camera: keyframes of {t, target, offset, tension k}, cubic Hermite per axis;
  hold keys get k≈0.3–0.5 so the camera keeps drifting toward the next move,
  never stopping dead. Handheld = small sums of sines scaled by distance;
  impact jolts on slams. FOV 28°. On reading beats, frame the whole line of
  text with margin so wobble and drift never clip it.

## Pitfalls learned

- Grade **after** OutputPass. An S-curve on HDR values >1 goes negative and
  produces cyan/orange blotches.
- Frame height must be even for x264 (`Math.round(W*ratio/2)*2`).
- White modern paper (survey maps) blows out under the lamp: age it with
  ffmpeg `curves` (highlights to ~0.82/0.72/0.52) + multiply an aged-paper texture.
- Low-res assets go soft on 4K push-ins; ask for the original scan.
- Procedural-only textures look like PowerPoint; real photographic textures
  (map scan, paper, wood, photos) are what make it look filmed. Ask for them.
- Iridescent physical materials look garish; use the real disc photo instead.
- Headless Chromium uses SwiftShader: all pages share one GPU process, so extra
  workers barely help. 1280 ≈ 1 s/frame; 4K is many times slower.
- Start the local server with Bash `run_in_background` (`python3 -m http.server
  8765` in the build folder); fonts/textures need http, not file://.
- External image/font CDNs may be blocked; fonts come from npm
  (`npm pack @fontsource/<font>`), three.js from `npm pack three@0.160.0`
  (copy `package/build/three.module.min.js` → `lib/`, `package/examples/jsm` → `lib/jsm`).
- Honesty: keep "illustrative" labels on generated/reconstructed assets, don't
  present a generated photo as real, and flag script lines the source doesn't
  support (e.g. a title not in the shown list).

## Measuring word onsets

```bash
ffmpeg -loglevel error -i vo.mp3 -ac 1 -ar 8000 -f s16le - | python3 -c "
import sys,struct,math
d=sys.stdin.buffer.read(); s=struct.unpack('<%dh'%(len(d)//2),d); w=160
print(' '.join('%.2f:%d'%(i/8000,20*math.log10(math.sqrt(sum(x*x for x in s[i:i+w])/w)+1)) for i in range(int(A*8000),int(B*8000),w)))"
```
Replace A/B with the phrase window; dips mark word/syllable boundaries.

## Files

- `template/film.html` — complete working scene (Abbottabad reel): layout,
  assets loading, objects, cue-driven animation, camera path, post chain,
  `window.renderFrame(t, frameIndex)` and `window.ready`.
- `template/cues.js` — cue-time file format.
- `template/fonts/` — Playfair Display 700/900, IBM Plex Mono 600.
- `scripts/stills.js` — `node stills.js <width> <outdir> t1 t2 …`
- `scripts/render.js` — `node render.js <width> <out.mp4> [workers] [audio]`;
  renders `film.html` from `http://127.0.0.1:8765`, encodes segments with x264
  CRF 14, concatenates and muxes the voiceover.
  Run both with `NODE_PATH=$(npm root -g)` so the pre-installed Playwright resolves.
- `scripts/sfx.py` — code-synthesized sound design (numpy only): room tone, drone
  swell, case/disc drops, paper slaps, pin slams, marker scribbles, highlighter
  swipes, whooshes, riser, string run, final boom — each placed on a cue from
  `cues.js` → `sfx.wav`. Always add SFX; a reel without them feels unfinished.
  Mix under the voice with ducking and loudness-normalise:
  `ffmpeg -i vo.mp3 -i sfx.wav -filter_complex "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,apad=whole_dur=DUR,asplit=2[v][vk];[1:a]volume=7dB[s0];[s0][vk]sidechaincompress=threshold=0.1:ratio=2.5:attack=20:release=300[s];[v][s]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=11" mix.wav`
  then mux `mix.wav` onto the video (no re-render needed).
- Assets expected by the template in `assets/`: `map_ams.jpg`, `aerial2011.jpg`,
  `walnut.jpg`, `paper.jpg`, `disc.png`, `list.png`, `vo.mp3`; plus `lib/` (three.js).
