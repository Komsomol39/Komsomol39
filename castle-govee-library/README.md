# CastleGovee Library

Public content library for the CastleGovee H70B6 30x32 LED curtain.

- `catalog.json` defines static images and frame-based animations.
- Assets are pixel-perfect 30x32 PNG with per-frame SHA-256 hashes.
- Changes to catalog or PNGs appear in the Android gallery after refresh; no APK update required.
- App reads content via HTTPS and caches verified PNGs offline.
- Modes: original, horizontal flip, and center-symmetric mirror.

Only image content and manifest are published here; no device keys, reports, credentials or phone data.

## Govee H70B6 autonomous GIF: measured limits

The **GitHub gallery** and the **controller's native autonomous GIF mode** are two different playback mechanisms. The gallery stores separate PNG frames and their timings in `catalog.json`. Autonomous GIFs are compressed GIF87a/GIF89a data uploaded to the controller over BLE as `0x5D` effects and activated in DIY preview mode `254`. The controller can play a successfully accepted GIF without constant phone frame streaming.

Tests on H70B6 (2026-10-10) established the following *input file size* boundary using the same **30×32, 36,001-frame** red-clock GIF, padded to exact byte sizes using valid GIF comment extensions:

| Compressed GIF file size | Actual result |
| ---: | --- |
| **1,048,560 bytes** | **Accepted**: device replied `A6 58 00`, then `33 05 00` |
| **1,048,561 bytes** | **Not accepted**: no success ACK; BLE disconnected |
| 1,048,568 bytes | Not accepted, reproduced twice |
| 1,048,576 bytes (1 MiB) | Not accepted, reproduced twice |

The boundary is **1 MiB − 16 bytes** for this tested device/transfer. The potential 16-byte protocol overhead is a hypothesis, **not** a measured RAM/Flash capacity. A file-size acceptance ACK does not prove complete visual playback, timing accuracy, or persistence after power cycling. Free/used controller memory cannot currently be queried through a verified command.

### Recommendations for GIF generators

- **Exact canvas:** 30×32 pixels. **Production target:** compressed GIF **≤1,000,000 bytes** for margin; **never upload above 1,048,560 bytes** through our tested H70B6 uploader.
- Prefer short seamless loops, 2–16 color palettes as the scene allows, and **changed-rectangle GIF frames** with appropriate disposal. Monochrome GIFs can use a 2-color palette and **LZW minimum code size 2**. The tested red hour clock is **941,338 bytes for 36,001 frames**.
- Frame complexity strongly affects compression. Neither a 36,001-frame cap nor a fixed animation-duration cap has been established for other visual content.
- Verify frame count, 30×32 canvas, individual frame delays, visual continuity, decoded output, and final file byte count before publishing or deploying.
- Mark a BLE transfer successful **only after** the controller acknowledges `A6 58 00` (data accepted) **and** `33 05 00` (preview activated); a completed BLE write alone is insufficient.
- For the **GitHub gallery**, keep publishing verified **PNG frames and `catalog.json`**, not raw native GIFs. The current local gallery staging tool supports at most **80 frames** and **460 bytes per compressed PNG frame**. These gallery limits are unrelated to the native GIF upload ceiling.
- Importing arbitrary user GIF files in the Android app is **temporarily hidden** while custom GIF artwork quality is being evaluated; tested built-in effects and GitHub gallery content remain available.

See the reusable [H70B6 GIF generator skill](skills/h70b6-gif-generator/SKILL.md) for the exact production checklist, validation workflow, and reference implementations.
