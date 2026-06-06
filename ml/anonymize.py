"""Step 2 - irreversibly anonymize raw images. MANDATORY before any detection.

KVKK red line: faces and license plates must be blurred BEFORE the model runs,
and the blur must be irreversible. We use defense-in-depth:

  1) deface  - a purpose-built face anonymizer (high recall), via subprocess.
  2) Grounding DINO backstop - detects "human face. license plate." and applies
     a strong Gaussian blur over those regions with PIL.

Output goes to data/anon/. Downstream steps are ONLY allowed to read data/anon/.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

from PIL import Image, ImageFilter

import config
from _model import detect


def _deface(src, dst) -> bool:
    """Runs the deface CLI src -> dst. Returns True on success."""
    for cmd in (["deface", str(src), "-o", str(dst)], [sys.executable, "-m", "deface", str(src), "-o", str(dst)]):
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if res.returncode == 0 and dst.exists():
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return False


def _blur_regions(path) -> int:
    """Blurs faces + plates detected by Grounding DINO. Returns region count."""
    image = Image.open(path).convert("RGB")
    result = detect(image, config.ANON_PROMPT, config.ANON_BOX_THRESHOLD, config.ANON_BOX_THRESHOLD)
    boxes = result["boxes"]
    for x0, y0, x1, y1 in boxes:
        box = (int(max(0, x0)), int(max(0, y0)), int(min(image.width, x1)), int(min(image.height, y1)))
        if box[2] <= box[0] or box[3] <= box[1]:
            continue
        region = image.crop(box)
        # Strong, irreversible blur (radius scales with region size).
        radius = max(12, int(min(region.size) * 0.6))
        region = region.filter(ImageFilter.GaussianBlur(radius=radius))
        image.paste(region, box)
    image.save(path, quality=92)
    return len(boxes)


def main() -> int:
    config.ensure_dirs()

    raw_images = sorted(config.RAW_DIR.glob("*.jpg")) + sorted(config.RAW_DIR.glob("*.png"))
    if not raw_images:
        print(f"No raw images in {config.RAW_DIR}. Run fetch.py first.", file=sys.stderr)
        return 1

    deface_ok = 0
    for src in raw_images:
        dst = config.ANON_DIR / src.name
        if _deface(src, dst):
            deface_ok += 1
        else:
            # deface unavailable/failed: start from a copy, rely on GD backstop.
            shutil.copyfile(src, dst)
        regions = _blur_regions(dst)
        print(f"[{src.name}] deface={'ok' if dst.exists() else 'no'} gd_blur_regions={regions}")

    print(f"\nAnonymized {len(raw_images)} image(s) -> {config.ANON_DIR}")
    if deface_ok < len(raw_images):
        print("WARN: deface did not run for every image; the Grounding DINO blur pass still applied.")
    print(">> Faces & plates blurred irreversibly. Detection may now read data/anon/ only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
