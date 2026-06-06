"""Step 3 - multi-category zero-shot detection on anonymized images.

KVKK guard: reads ONLY data/anon/. Refuses to run if that folder is empty.

Pipeline per image:
  1. One combined Grounding DINO prompt ("traffic sign. billboard. garbage.").
  2. Map every box to a category by its matched phrase (drop unmapped = noise).
  3. Apply each category's OWN confidence threshold (precision).
  4. Class-agnostic NMS to drop overlapping duplicate boxes on the same object.
"""

from __future__ import annotations

import json
import sys

from PIL import Image, ImageStat

import config
from _model import detect


def _is_uniform(image: Image.Image, box: list[float], threshold: float = 18.0) -> bool:
    """True if the box region is near-uniform (a blur artifact or flat sky),
    i.e. low texture -> almost certainly not a real signposted object."""
    x0, y0, x1, y1 = (int(v) for v in box)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(image.width, x1), min(image.height, y1)
    if x1 <= x0 or y1 <= y0:
        return True
    crop = image.crop((x0, y0, x1, y1)).convert("L")
    return ImageStat.Stat(crop).stddev[0] < threshold


def _iou(a: list[float], b: list[float]) -> float:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    area_a = max(0.0, ax1 - ax0) * max(0.0, ay1 - ay0)
    area_b = max(0.0, bx1 - bx0) * max(0.0, by1 - by0)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _nms(candidates: list[dict], iou_threshold: float = 0.5) -> list[dict]:
    """Class-agnostic non-max suppression: keep highest score, drop overlaps."""
    kept: list[dict] = []
    for cand in sorted(candidates, key=lambda c: c["score"], reverse=True):
        if all(_iou(cand["box"], k["box"]) < iou_threshold for k in kept):
            kept.append(cand)
    return kept


def main() -> int:
    config.ensure_dirs()

    anon_images = sorted(config.ANON_DIR.glob("*.jpg")) + sorted(config.ANON_DIR.glob("*.png"))
    if not anon_images:
        print("KVKK STOP: data/anon/ is empty. Run anonymize.py before detect.py.", file=sys.stderr)
        return 1

    manifest = {}
    if config.MANIFEST_JSON.exists():
        for entry in json.loads(config.MANIFEST_JSON.read_text(encoding="utf-8")):
            manifest[entry["id"]] = entry

    prompt = config.detection_prompt()
    print(f"[detect] prompt='{prompt}' base_box>={config.BASE_BOX_THRESHOLD} text>={config.TEXT_THRESHOLD}")

    detections = []
    for img_path in anon_images:
        image = Image.open(img_path).convert("RGB")
        result = detect(image, prompt, config.BASE_BOX_THRESHOLD, config.TEXT_THRESHOLD)

        candidates = []
        for score, box, raw_label in zip(result["scores"], result["boxes"], result["labels"]):
            category = config.category_for_label(raw_label)
            if category is None:
                continue  # phrase didn't map to any category -> noise
            if score < category["threshold"]:
                continue  # below this category's confidence floor
            if _is_uniform(image, box):
                continue  # blur artifact / flat sky -> not a real object
            candidates.append(
                {
                    "category": category["key"],
                    "label": category["label"],
                    "color": category["color"],
                    "score": round(float(score), 4),
                    "box": [round(float(v), 1) for v in box],
                }
            )

        kept = _nms(candidates, iou_threshold=0.5)

        meta = manifest.get(img_path.stem, {})
        for c in kept:
            detections.append(
                {
                    "id": img_path.stem,
                    "image": img_path.name,
                    "lat": meta.get("lat"),
                    "lng": meta.get("lng"),
                    "address": meta.get("address", ""),
                    "captured_at": meta.get("captured_at", ""),
                    **c,
                }
            )

        summary = ", ".join(f"{c['label']}:{c['score']}" for c in kept) or "-"
        print(f"[{img_path.name}] {len(kept)} kept ({summary})")

    config.RAW_DETECTIONS_JSON.write_text(
        json.dumps(detections, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    by_cat: dict[str, int] = {}
    for d in detections:
        by_cat[d["label"]] = by_cat.get(d["label"], 0) + 1
    print(f"\n{len(detections)} detection(s) -> {config.RAW_DETECTIONS_JSON}")
    print(f"by category: {by_cat}")
    print(">> NEXT: run export.py to draw boxes and publish detections.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
