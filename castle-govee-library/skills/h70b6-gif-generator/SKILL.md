---
name: h70b6-gif-generator
description: Produce, optimize and validate autonomous GIF89a effects for the Govee H70B6 30×32 LED curtain and publish curated frames to the CastleGovee GitHub library. Respect the empirically measured native GIF upload limit.
---

# H70B6 GIF generation and GitHub gallery publishing

Use this skill when preparing, optimizing, reviewing, or publishing a GIF animation for **Govee Curtain Lights Pro H70B6** using Castle Lights / CastleGovee.

## Hardware and empirical safety limits (measured 2026-10-10)

- Controller canvas: **30 × 32 LEDs**, exactly **960 pixels** per full frame.
- Native autonomous animations are **GIF87a/GIF89a** delivered through effect payload **0x5D** using encrypted BLE **A6 / 0x58**, then activated through **DIY preview 254 (0xFE)**.
- **Maximum accepted compressed GIF file size in our byte-precise experiment: 1,048,560 bytes.** This same 36,001-frame red clock GIF was accepted and activated at **1,048,560 bytes**, but **1,048,561 bytes** failed with no device acceptance ACK followed by Bluetooth disconnection. **1,048,568 bytes** failed twice; **1,048,576 bytes (1 MiB)** failed twice.
- The accepted value is **1 MiB − 16 bytes**, suggesting a 16-byte internal allowance; **this is only a hypothesis**, not a proved firmware implementation or RAM/flash capacity.
- **Use an engineering target of ≤1,000,000 bytes per native GIF** to keep a safety margin. **Never exceed 1,048,560 bytes** when uploading through the tested H70B6 protocol. Count the **actual GIF file bytes**, not raw pixels, BLE packets, or the leading 0x5D protocol marker.
- These results are **specific to the measured GIF/firmware/transfer path**. A GIF of equal size but greater frame complexity is not automatically guaranteed to work. There is no verified BLE free-memory query and no established per-frame-count hardware maximum.
- Upload confirmation requires **both** the controller's decrypted **A6 58 00** (effect accepted) and **33 05 00** (DIY preview activated). A successful phone-side BLE write does **not** imply controller acceptance. On disconnect, timeout, or missing ACK: **do not claim success or increase the file size**. Do not run erase/flash-format experiments.

## Generate native autonomous GIFs

1. Generate exactly **30×32** frames, ideally starting with a deliberately small looping scene that looks good on the actual LED curtain. Plan perceptual cadence; GIF delays are expressed in **10 ms units** but actual hardware timing must be checked visually.
2. Limit colors to what is actually needed. For monochrome animations, use **2 colors** and **LZW minimum code size 2**, not an 8-bit encoder with a 256-color palette.
3. Delta-compress frames: encode only the **changed subrectangle**, preserving prior pixels with the correct disposal mode (typically disposal=1 for composited changed rectangles). Minimize dither and random noise that destroy interframe compression.
4. Use palette quantization (e.g. **2, 4, 8, 16 colors**) when appropriate, keeping the visual quality on the LED curtain. Large areas with slow localized motion compress much better than a full-scene random change each frame.
5. Prefer short, **seamless repeatable loops** (e.g. 10–20 seconds) over a massive unique one-hour timeline, unless the goal specifically requires a long timeline. For infinite loops set the NETSCAPE loop extension accordingly (e.g. Pillow `loop=0`).
6. Keep generated final GIF at **≤1,000,000 bytes**; reject above **1,048,560 bytes**. Do not fake compressibility by inserting large GIF comment extensions: comments are used only for **controlled byte-size boundary research**, not production effects.
7. Validate with Pillow or equivalent before delivery: GIF header, **30×32 canvas**, all frame counts, durations, decoded full frames, alpha/disposal, color fidelity, exact output file length, and seamlessly matching first/last positions when looping.
8. Test on hardware with native GIF upload, record device acceptance **A6 58 00**, activation **33 05 00**, and ask for visible confirmation of motion with the phone app stopped. Do not silently replace an effect the user wants to keep.

## Distinguish GitHub library from native GIF transfer

**The existing GitHub gallery is NOT a raw GIF upload service.** It is a curated PNG-frame manifest:

- Repository: `Komsomol39/Komsomol39`
- Library directory: `castle-govee-library/`
- Manifest: `castle-govee-library/catalog.json`
- Animations: `castle-govee-library/animations/<id>/frame-XX.png`
- Each PNG frame must be **30×32**, SHA-256 recorded in the manifest. The existing local staging tool `D:\Project\CastleGovee\scripts\prepare_gallery_item.py` currently enforces **≤80 frames** and **≤460 compressed bytes per PNG frame**. These are **gallery streaming constraints**, not the 1,048,560-byte native autonomous GIF cap.
- For GitHub gallery publication, use the curated publishing pipeline: prepare source GIF/PNG locally, validate all frames, run the staging tool with a unique id/title, inspect manifest diffs, publish only reviewed PNG assets and `catalog.json`, then refresh the Android gallery. **No secrets, device keys, reports, cookies, phone identifiers, APKs or bugreports** are allowed in the public library.
- To provide a native autonomous GIF, separately prepare the compressed GIF within the safe size and ship through the Castle Lights approved-effect path. At present the **custom GIF file-picker UI is temporarily hidden** pending visual quality/creative validation; do not tell end-users that direct arbitrary GIF upload is currently available.

## Local reference implementations

- `D:\Project\CastleGovee\scripts\create_lzw2_red_clock.py`: validated compact red 2-color clock, **36,001 frames / 941,338 GIF bytes**, with LZW minimum size 2 and changed-rectangle encoding.
- `D:\Project\CastleGovee\scripts\create_compact_red_clock.py`: baseline full-frame/delta-frame encoding.
- `D:\Project\CastleGovee\scripts\prepare_gallery_item.py`: curate a GIF as GitHub gallery PNG frame assets.
- `D:\Project\CastleGovee\research\GIF_KIB_BOUNDARY_2026-10-10.md`: full empirical byte-boundary report.
- Never assume **controller RAM/flash capacity** equals the upload limit; until a documented read-only memory query exists, report accepted **file size** only.
