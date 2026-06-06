"""Step 4 - draw detection boxes on evidence images and publish detections.json.

Writes the SAME document to three places (backend embed, web public, data/processed)
and renders each anonymized evidence image with its detection box(es) + category
label + score, so the map's evidence panel SHOWS where each detection is.

Safety: never publishes an empty result. If detection produced nothing, the
previously published detections.json is kept untouched.
"""

from __future__ import annotations

import json
import math
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont

import config


DETECTION_NAMESPACE = uuid.UUID("6f1b3c9e-0b3a-4c2a-9b7e-9c1d2e3f4a5b")


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _confidence(score: float) -> str:
    """Honest, absolute confidence tier = field-verification priority.
    Not an emergency scale; the UI legend explains the colors as confidence.
      >=0.40 high (info) · 0.30-0.40 medium (warning) · <0.30 low (urgent)
    """
    if score >= 0.40:
        return "info"
    if score >= 0.30:
        return "warning"
    return "urgent"


def _draw_boxes(src_path, dets: list[dict], out_path) -> None:
    """Renders all detection boxes (category color + label + score) on an image."""
    image = Image.open(src_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = _font(16)

    for d in dets:
        x0, y0, x1, y1 = d["box"]
        color = d.get("color", "#2dd4bf")
        draw.rectangle([x0, y0, x1, y1], outline=color, width=3)

        caption = f"{d['label']} {d['score']:.2f}"
        tb = draw.textbbox((0, 0), caption, font=font)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        ly = max(0, y0 - th - 6)
        draw.rectangle([x0, ly, x0 + tw + 8, ly + th + 6], fill=color)
        draw.text((x0 + 4, ly + 3), caption, fill="#0b1220", font=font)

    image.save(out_path, quality=92)


def _jitter_colocated(records: list[dict]) -> None:
    """Spreads detections that share an identical coordinate onto a small circle
    (~18 m) so map pins don't stack and stay individually clickable."""
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in records:
        groups[(r["lat"], r["lng"])].append(r)

    radius = 0.00016  # ~18 m
    for (lat, lng), items in groups.items():
        if len(items) < 2:
            continue
        for i, r in enumerate(items):
            angle = 2 * math.pi * i / len(items)
            r["lat"] = round(lat + radius * math.cos(angle), 6)
            r["lng"] = round(lng + radius * math.sin(angle) / math.cos(math.radians(lat)), 6)


def main() -> int:
    config.ensure_dirs()

    if not config.RAW_DETECTIONS_JSON.exists():
        print("No raw_detections.json. Run detect.py first.")
        return 1

    raw = json.loads(config.RAW_DETECTIONS_JSON.read_text(encoding="utf-8"))
    raw = [d for d in raw if d.get("lat") is not None and d.get("lng") is not None]

    if not raw:
        print("WARNING: 0 detections — keeping the existing detections.json untouched.")
        return 2

    processed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Draw boxes once per image (all of that image's detections together).
    by_image: dict[str, list[dict]] = defaultdict(list)
    for d in raw:
        by_image[d["image"]].append(d)
    for image_name, dets in by_image.items():
        src = config.ANON_DIR / image_name
        if src.exists():
            _draw_boxes(src, dets, config.WEB_ANON_DIR / image_name)

    # One record per reviewed detection. Keep a stable id in the public payload
    # so the map can use deterministic marker keys in live and offline modes.
    records = []
    image_seen: dict[str, int] = defaultdict(int)
    for d in raw:
        image_seen[d["image"]] += 1
        id_seed = f"{d['image']}|{d['category']}|{d['label']}|{d['box']}"
        public_id = str(uuid.uuid5(DETECTION_NAMESPACE, id_seed))
        records.append(
            {
                "id": public_id,
                "lat": round(float(d["lat"]), 6),
                "lng": round(float(d["lng"]), 6),
                "label": d["label"],
                "category": d["category"],
                "score": round(float(d["score"]), 4),
                "image_url": f"/anon/{d['image']}",
                "address": d.get("address", ""),
                "severity": _confidence(float(d["score"])),
                "captured_at": processed_at,
            }
        )

    _jitter_colocated(records)

    payload = json.dumps(records, ensure_ascii=False, indent=2)
    for sink in (config.BACKEND_EMBED_JSON, config.WEB_PUBLIC_JSON, config.PROCESSED_JSON):
        sink.write_text(payload, encoding="utf-8")
        print(f"wrote {len(records)} detection(s) -> {sink}")

    by_cat: dict[str, int] = {}
    for r in records:
        by_cat[r["label"]] = by_cat.get(r["label"], 0) + 1
    print(f"by category: {by_cat}")
    print("\nDONE. Rebuild backend (embed) or set DETECTIONS_PATH to serve the new data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
