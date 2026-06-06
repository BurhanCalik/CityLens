"""Step 3 - run zero-shot detection of the TARGET object on anonymized images.

KVKK guard: this step reads ONLY data/anon/. It refuses to run if that folder is
empty, so detection can never accidentally touch un-anonymized raw imagery.
"""

from __future__ import annotations

import json
import sys

from PIL import Image

import config
from _model import detect


def main() -> int:
    config.ensure_dirs()

    anon_images = sorted(config.ANON_DIR.glob("*.jpg")) + sorted(config.ANON_DIR.glob("*.png"))
    if not anon_images:
        print(
            "KVKK STOP: data/anon/ is empty. Run anonymize.py before detect.py.",
            file=sys.stderr,
        )
        return 1

    manifest = {}
    if config.MANIFEST_JSON.exists():
        for entry in json.loads(config.MANIFEST_JSON.read_text(encoding="utf-8")):
            manifest[entry["id"]] = entry

    prompt = config.TARGET_OBJECT.strip().lower().rstrip(".") + "."
    print(f"[detect] prompt='{prompt}' box>={config.BOX_THRESHOLD} text>={config.TEXT_THRESHOLD}")

    detections = []
    for img_path in anon_images:
        image = Image.open(img_path).convert("RGB")
        result = detect(image, prompt, config.BOX_THRESHOLD, config.TEXT_THRESHOLD)

        meta = manifest.get(img_path.stem, {})
        kept = 0
        for score, box in zip(result["scores"], result["boxes"]):
            detections.append(
                {
                    "id": img_path.stem,
                    "image": img_path.name,
                    "lat": meta.get("lat"),
                    "lng": meta.get("lng"),
                    "address": meta.get("address", ""),
                    "captured_at": meta.get("captured_at", ""),
                    "label": config.TARGET_LABEL,
                    "score": round(float(score), 4),
                    "box": [round(v, 1) for v in box],
                }
            )
            kept += 1
        print(f"[{img_path.name}] {kept} detection(s)")

    config.RAW_DETECTIONS_JSON.write_text(
        json.dumps(detections, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{len(detections)} detection(s) -> {config.RAW_DETECTIONS_JSON}")
    print(">> NEXT: run export.py to publish detections.json + anonymized evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
