---
name: h70b6-gif-generator
description: Publish validated, finished 30x32 H70B6 GIF variants to Castle GIF Library v2 on GitHub; no device-side or mobile GIF re-encoding.
---

# Govee H70B6 — GIF generator and GitHub publisher

Use this skill for new art, animation speed variants, street-view mirror variants and publication to repository Komsomol39/Komsomol39, directory castle-govee-library/.

## Mandatory schema v2

All gallery effects must publish finished autonomous GIF89a assets into GitHub. The Android app downloads, verifies and uploads those bytes unchanged to the controller. No runtime GIF compilation, speed conversion or reflection on the phone.

Manifest: catalog.json, schema 2, format castle-govee-native-gif-v2, width 30, height 32. Each item provides id/title/type, PNG preview with SHA256, variants array. Each variant supplies orientation (normal or street), path, SHA256, sizeBytes, frameCount, durationMs. Animated variants also have speedPercent, from 10 to 200 in steps of 10. Static variants omit speedPercent completely.

Animated paths are gifs/<id>/<normal|street>/<DDD>.gif, DDD = 010 to 200. Static paths are gifs/<id>/<normal|street>.gif. Publish only actually available combinations. Missing speed or orientation variants must NOT be displayed in Castle Lights.

## Art production

- Generate exact 30 × 32 RGB pixels. Street-view is the horizontal mirror of normal-view, for viewing from behind/outdoors.
- Bake speed presets into the GIF per-frame delays: delayMs = round(originalDelayMs × 100 / speedPercent / 10) × 10. 100% is the artist-chosen nominal speed. GIF timing has 10ms units, so small rounding variations are expected.
- Provide 10, 20, ..., 200% only when requested and generated. Static images have no meaningful speed parameter.
- Prefer a small palette, minimal dithering, LZW compression, coherent transitions, delta rectangles and seamless loop, as the artwork permits. Check visual quality on real LEDs.
- Validate each exact finished file by decoding all frames; verify pixels, dimension, disposal, delays, loop, mirrored output and total duration. Store the SHA256 of GIF bytes, not a PNG hash, as the variant sha256. Ensure sizeBytes equals exact compressed GIF size.

## Hardware constraints

Empirical input GIF acceptance boundary on tested H70B6: 1,048,560 accepted; 1,048,561 not accepted. This is not controller free memory. Keep production GIF files <= 1,000,000 bytes, leaving margin. Device upload requires A6 58 00 acceptance and 33 05 00 DIY-preview ACK. BLE write success alone is insufficient.

## Workflow

1. Create all needed full GIF variants on a PC or CI, not in Android. Store source PNGs separately as optional editable artwork and small preview images.
2. Produce catalog v2 with only published variants. Check that missing speedPercent means no speed menu, missing street variant means no street mode. Check exact hashes/lengths.
3. Commit GIF files, preview images, README and catalog.json in one atomic GitHub commit. Do not commit secrets, device authentication material, APKs, logs or phone identifiers.
4. Verify repository manifest on GitHub and test download/ACK on a physical H70B6.
5. When an asset changes, update its SHA, byte size and duration and atomically publish the new version.

## Local tools

Project D:\Project\CastleGovee. v2 migration data are staged in library-v2-staging/. Conversion tool scripts/build_library_v2_from_android.py migrated already-built cached GIFs from our test device and is not a generic generator. Future new animations should be authored on a PC or CI and validated before publishing. Mobile GifPresetCache.java is retired from the active library pipeline.
