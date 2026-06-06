"""Generate a dense grid of scan points over Başakşehir and write points.json.

fetch.py calls the FREE Street View metadata endpoint per point and skips the
ones with no imagery, so it's fine to over-generate here. Bump DENSITY (smaller
STEP) for an even denser map.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Bounding box around Başakşehir, İstanbul.
LAT_MIN, LAT_MAX = 41.075, 41.115
LNG_MIN, LNG_MAX = 28.780, 28.832
STEP = 0.0045  # ~360 m grid spacing
HEADINGS = [90, 0, 270, 180]  # vary the look direction across the grid


def neighborhood(lat: float, lng: float) -> str:
    if lat >= 41.103:
        base = "Kayaşehir Mah."
    elif lat >= 41.097:
        base = "Kayabaşı Mah."
    elif lng < 28.792:
        base = "Şahintepe Mah." if lat < 41.088 else "Güvercintepe Mah."
    elif lng < 28.806:
        base = "Başak Mah." if lat >= 41.090 else "Ziya Gökalp Mah."
    else:
        base = "Başak Mah."
    return f"{base}, Başakşehir/İstanbul"


def main() -> int:
    points = []
    i = 0
    lat = LAT_MIN
    while lat <= LAT_MAX + 1e-9:
        lng = LNG_MIN
        while lng <= LNG_MAX + 1e-9:
            points.append(
                {
                    "lat": round(lat, 5),
                    "lng": round(lng, 5),
                    "heading": HEADINGS[i % len(HEADINGS)],
                    "address": neighborhood(lat, lng),
                }
            )
            i += 1
            lng += STEP
        lat += STEP

    out = ROOT / "ml" / "points.json"
    out.write_text(json.dumps(points, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(points)} candidate points -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
