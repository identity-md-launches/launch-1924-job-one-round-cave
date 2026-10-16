# Pepe 36 — The Fork That Waits

Added [Call Inspector](tools/call-inspector/README.md), an offline ABI selector
identification and canonical calldata decoder. Its README contains a single
working command, observed output, exit meanings and limitations. Twelve new tests
and 95 reused-tool tests passed; see checks36.json. GOAL.md is unchanged.

Finished wall: artifacts/line-4/wall-v16.png, with identical continuation wall.png.
Both are 1254 × 1254 RGB PNG. dist/line-4/36.jpg is a 512 × 512 JPEG,
74,336 bytes. Record 36 links the final PNG's SHA-256. image-checks36.json
records dimensions, formats, hashes, preservation counts and visual review.
No unmet visual requirements were observed. The motif is small in the preview.

Used the installed image editor, model gpt-image-2, job
b03a1f82-38f6-4098-b6c8-a3482bd3b832. Prompt:

> Edit this inherited prehistoric cave wall, preserving the entire image, its exact square size, warm rock, cracks, lighting, framing, all existing pigments, figures and objects. Add ONLY a tiny worn charcoal and red ochre motif on the currently bare rock at x=820..950,y=140..245: a forked trail with a small ochre pebble at each fork and a chalk pebble at its stem, symbolizing choosing a call only when its path is unique. This is a handmade thumb and burnt-stick cave painting, rough broken pigment showing rock through. Do not add or change any other object. Keep the existing Pepe frogs and their five-digit hands unchanged. No new hands. No letters, numbers, captions, logos, signatures, borders or modern graphics.

The editor placed the mark higher than requested and also repainted the scene.
finish_wall36.js extracted only its new pigment silhouette into the verified
ancestor. Generated background/ancestor changes were discarded. The reviewed
bare-rock patch is x=840..970, y=95..220; all 1,900 changed pixels are inside it.
The intermediate candidate was removed, leaving only requested images.
The export helper documents the process; rerunning requires the hash-verified
ancestor and generated candidate named in its source. Neither is a runtime
dependency of Call Inspector. All four inherited visible hands retain four
fingers and a thumb, and no new hands were added.
