# Castle GIF Library v2

Public, **ready-to-upload native GIF** library for Govee H70B6 (30 × 32 LEDs).
Castle Lights does not generate or modify GitHub-gallery GIF files on the phone. Speed and reverse/street display are embedded in finished GIFs published here.

## Rules

- Source of truth: catalog.json with schema = 2, format = castle-govee-native-gif-v2.
- Each item has an id, title, type (animation or image), optional description, a 30×32 PNG preview (file, sha256) and a variants array.
- Each variant has orientation = normal or street, file, sha256, sizeBytes, frameCount and durationMs.
- Animated variants also specify speedPercent: 10, 20, ... 200, in 10% steps. Only publish available speeds; the complete set is optional.
- Static image variants DO NOT contain speedPercent, and NEVER display a speed menu.
- The UI only offers an orientation if that variant exists and only offers speeds published for the selected orientation. Missing variants are never synthesized on Android.
- Paths: gifs/<id>/<normal|street>/<3-digit speed>.gif for animations (e.g. gifs/russian-wave/normal/100.gif); gifs/<id>/<normal|street>.gif for static images.
- normal = original image; street = horizontal mirror for viewing through the curtain from outdoors.
- One final GIF file is downloaded by HTTPS, checked against its SHA-256 and exact byte count, cached on the phone, then uploaded through BLE after a deliberate user selection.
- An autonomous GIF upload is only successful after controller acknowledgments A6 58 00 and 33 05 00.

## Published gallery

| Effect | Orientations | Speed presets | GIFs |
| --- | --- | --- | ---: |
| Russian waving flag | normal / street | 10% through 200% | 40 |
| Autumn leaves | normal / street | 10% through 200% | 40 |
| Svetlogorsk coat of arms | normal / street | none (static) | 2 |
| Russian tricolor | normal / street | none (static) | 2 |
| Baltic heart | normal / street | none (static) | 2 |
| **Total** | | | **86** |

## Example animation item

    {
      "schema": 2,
      "format": "castle-govee-native-gif-v2",
      "width": 30, "height": 32,
      "items": [{
        "id": "example", "title": "Example",
        "type": "animation", "loop": true,
        "preview": {
          "file": "animations/example/frame-00.png",
          "sha256": "<SHA256 of 30x32 preview PNG>"
        },
        "variants": [{
          "orientation": "normal",
          "speedPercent": 100,
          "file": "gifs/example/normal/100.gif",
          "sha256": "<SHA256 of final GIF bytes>",
          "sizeBytes": 4000, "frameCount": 12, "durationMs": 3000
        }]
      }]
    }

For static images, omit speedPercent, set frameCount=1, and use gifs/<id>/normal.gif or gifs/<id>/street.gif.

## Publication checklist

1. Create the desired 30×32 animation and encode all supported final GIF89a variants OFF the phone. Bake individual frame delays into the GIF Graphic Control Extensions. At speed P, frame delay is approximately source delay × 100/P, rounded to 10ms.
2. Verify decoded pixel frames, duration, loop, orientation, exact compressed file size and SHA-256. For H70B6, target **1,000,000 bytes or less per GIF**.
3. Publish only the variants that exist. Upload every GIF and update catalog.json atomically in one Git commit so the mobile app never sees missing files.
4. Never publish credentials, tokens, device identifiers, private logs or APKs.

## Experimental H70B6 native GIF size boundary

On the tested controller and padded 36,001-frame GIF, **1,048,560 bytes were accepted** but **1,048,561 bytes failed**. This is a measured input-file limit, NOT a measurement of free RAM or flash. Complex files may behave differently. Recommended production target: <= 1,000,000 bytes.

Older schema 1 with PNG-frame streaming is deprecated for the gallery. A v2-compatible APK is required to use this catalog. GIF animation authoring and safety rules: skills/h70b6-gif-generator/SKILL.md.
