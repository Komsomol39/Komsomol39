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
