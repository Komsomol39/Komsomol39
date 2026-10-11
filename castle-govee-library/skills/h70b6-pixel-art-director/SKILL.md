---
name: h70b6-pixel-art-director
description: Art-direct and render original expressive 30x32 pixel animations for Govee H70B6; integrates pixel composition, frame motion, palettes, physical-device QA and Castle GIF Library v2.
---

# Castle Pixel Art Studio: H70B6 art director

Use for requests like "нарисуй чайку над морем", "сделай северное сияние", "пиксельный закат", "анимируй животное на гирлянде". This is an ART CREATION skill; pair with existing h70b6-gif-generator/SKILL.md for final publishable GIFs.

## Canvas and physical medium
- 30 columns × 32 rows = 960 RGB LEDs, exact 30x32 canvas, y downward.
- Each pixel is a physical LED. Draw at native resolution, never shrink a large photograph and call it pixel art.
- 1-2 clearly recognizable animated focal subjects; simple background; major forms about 7-18 pixels across.
- Palette generally 8-24 harmonious colors, max 48. Dark backgrounds, clustered highlights, value contrast, readable silhouettes; avoid excessive white LEDs.
- No blur/antialiasing, subpixel rendering, noisy dithering, random-per-frame grain, or interpolation that blurs pixel positions.

## Toolchain
1. Pixelorama 1.2.3 (free GUI, onion skin, layers, timeline): D:\Project\CastleGovee\tools\pixelorama\v1.2.3\Pixelorama-Windows-64bit\Pixelorama.exe. Draw at native 30x32; retain source .pxo, export PNG frames.
2. Python 3.14 + Pillow 12 + NumPy 2: D:\Project\CastleGovee\.pixel-venv\Scripts\python.exe. Isolated from Castle Relay's Python env. Pillow is implemented as rendering/encoding engine, NumPy optional for further geometry and simulations.
3. Lospec: palette references. Hand-pick colors; avoid copying copyrighted sprites.
4. Aseprite (OPTIONAL licensed professional app, not installed): command-line batch sprite-sheet export.
5. Piskel (OPTIONAL browser art editor): export spritesheet or PNG frames.
6. Existing GIF Library v2: D:\Project\CastleGovee\scripts\add_effect_v2.py; do not duplicate phone-side/upload encoding.

## Workflow
1. Brief: specify main subject, atmosphere, visual priority, era/season and looping action. Choose what to OMIT at only 960 LEDs.
2. Storyboard 30x32: sky, background, focus, foreground, negative space, light source and silhouette.
3. Author a declarative JSON using templates/island-sunset.json or templates/northern-lights.json. Build ordered layers using: bands, polygon, rect, sun, cloud, stars, aurora, waves, island, palm, bird. Palette keys are referenced with @name; all visible colors must appear in palette. For different subjects extend scripts/render_scene.py with new documented pixel-precise drawing primitives.
4. Animate with cycle-periodic motion, arcs and purposeful rhythm. Preserve a stable background and use selective moving foreground. Make a seamless loop, ideally 3-7 seconds.
5. Render from D:\Project\CastleGovee:
   .pixel-venv\Scripts\python.exe skills\h70b6-pixel-art-director\scripts\render_scene.py --scene skills\h70b6-pixel-art-director\templates\island-sunset.json --output artwork\island-sunset
6. Review artwork\island-sunset\preview.png (nearest-neighbor zoom), contact-sheet.png (all frames), original 30x32 frames. Read report.json: color count, frame count, boundary change, byte count. Evaluate native-size legibility, silhouette, rhythm, color harmony and perceptual flicker. Iterate rather than treating an algorithmic score as subjective proof of beauty.
7. Create official finished v2 GIF variants with scripts/add_effect_v2.py, unique id, title, speed presets and mirror orientations in library-v2-staging or another safe working directory; verify exact hashes, frame counts and manifest against GIFs.
8. Publish only when requested: use existing h70b6-gif-generator instructions (atomically commit all GIFs, previews and manifest); verify remote manifest and actual BLE controller acknowledgments A6 58 00 and 33 05 00. Successful write alone is not device success.

## Case study: what NOT to do (original "Остров и чайка")

This is a **negative example**, based on photos of the physical Govee H70B6 curtain viewed through sheer curtains. It is NOT a universal artistic recipe, and the redesigned animation is NOT a mandatory template. Decide what "good" should look like together with the user for every new scene.

Original example: `island-sun-seagull`, pre-redesign 40-frame GIF (e.g. `gifs/island-sun-seagull/normal/100.gif` in the GitHub history before commit `8560eb9`). The controller accepted and displayed the file, but the user photo showed poor recognition.

Avoid repeating these **specific failure modes** without checking the real display:
- Filling most of the 30×32 field with similarly bright cyan/blue sky and water. On LEDs behind tulle these areas visually merged into a luminous haze, obscuring the subject. The issue was not "blue" itself, but the relative brightness, competing lit areas and real viewing environment.
- Treating a clean enlarged PNG preview as proof that the composition will be readable on a 960-LED curtain. Small shapes and color boundaries became far less distinct through the fabric, LED spacing and camera exposure.
- Giving background highlights, sun, water, sand, palm foliage and bird comparable visual weight all at once; the main silhouettes competed rather than reading as separate objects.
- Having a bird whose wing flaps and path overlap or visually blend with the palm, sun or bright sky. A bird identifiable in an enlarged 30×32 bitmap may become random blinking dots at actual distance.
- Adding frequent tiny wave/reflection detail because it looks decorative at zoom; at installation scale it turned into more scattered light points instead of legible scenery.
- Confusing technical success (valid GIF, GitHub SHA-256, BLE upload and A6/58 + 33/05 acknowledgements) with **artistic success**. Transport/device ACK proves delivery and activation, not legibility or beauty.

Outcome observed: after redesign, the user's next photograph and feedback were much more positive; however this only validates **that one scene under that viewing setup**, not any fixed formula such as "always black sky", "always giant palm", specific colors or compulsory silhouette sizes.

**Future approach:** keep these mistakes in mind as pitfalls to investigate, not hard bans. For every new effect, discuss artistic direction with the user anew, compare its actual appearance on the curtain when possible, and allow deliberate exceptions when they serve the intended image.

## Art-quality rubric, manual (score 0-5)
- Subject recognizable from a few meters at 30x32, not merely enlarged in preview.
- Clear visual hierarchy, depth, negative space.
- Cohesive warm/cool color relationship and contrast.
- Appealing animation timing, arcs, coherent seamless motion.
- Physical display comfort, visibility, no disruptive flicker.
Target >=4 in subject, palette and motion before publication. Scores are human/agent visual judgment and must not be invented without inspection.

## Constraints and safeguards
- Official autonomous GIF target <=1,000,000 bytes; empirical tested upper boundary 1,048,560 bytes is controller-specific.
- Orientation normal/street and 10-200% speed variants are pre-rendered OFF Android; publish ONLY actually present variants.
- GIF frame delays operate in 10ms increments; test re-encoding behavior.
- Never overwrite existing catalog IDs without checking. Never publish secrets, logs, credentials, private device IDs, debug APKs.
- Don't claim real-device testing before physical BLE ACKs are observed.

## Evidence to return
Describe visual concept and palette, local PNG/GIF paths, frame and byte counts, QA result, and explicit status LOCAL / STAGED / PUBLISHED / DEVICE-VERIFIED.
