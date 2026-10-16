# Gathering 36 image process

Input: the verified Gathering 35 full wall, SHA-256 `bee646caa4811e56c3052e39c2fc8fdb61d97e164d2f95621f5b0edf5b812474`, downloaded from the artifact URL in `dist/gathering/35.json`. It was opened before editing.

Built-in imagegen edit prompt:

> Use case: precise-object-edit. Edit target: the provided full square cave wall painting. Add ONLY one small prehistoric cave-pigment motif in the bare rock patch at image coordinates approximately x=1050..1160, y=915..1015 on the 1254x1254 image, below the red branching marks and to the right of the existing sieve. Motif: four tiny irregular ochre pebbles connected by one thin charcoal winding line, ending at one chalk-white pebble, suggesting four workers sharing a verified path. Keep it subtle, hand-painted, uneven and worn, matching existing red/yellow ochre, charcoal, chalk and rock texture. Absolutely preserve all existing paintings, Pepe frog, hand digits, rock, cracks, cave size, lighting and framing; no mark outside that patch. No letters, numbers, captions, symbols, logos, borders, watermarks, photography, or new hands. Output the complete square edited image.

The tool output repainted the larger wall, so `finish_wall36.js` isolated only pigment-colored changes within x=1030..1203, y=870..971 over the verified ancestor. The complete final wall and its 512-pixel JPEG were opened. The inherited Pepe, both five-digit hands, earlier marks, rough rock, cracks, warm torchlight and square framing remain. No words or prohibited marks were observed. No unmet visual requirement was found in this local review. The new motif is small and becomes faint in compact gallery previews.

The final PNG SHA-256 and preservation bounds are in [image-checks36.json](image-checks36.json). The JPEG and JSON record sit in `dist/gathering/`.
