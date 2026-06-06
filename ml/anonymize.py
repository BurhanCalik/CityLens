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


def _deface_batch(raw_files: list) -> set:
    """Runs deface ONCE over all raw files (the model loads a single time, which
    is far faster for large batches). deface writes '<stem>_anonymized<ext>'
    next to each input. Returns the set of stems it successfully produced."""
    if not raw_files:
        return set()
    args = [str(f) for f in raw_files]
    for base in (["deface"], [sys.executable, "-m", "deface"]):
        try:
            subprocess.run([*base, "--thresh", "0.2", *args], capture_output=True, text=True, timeout=3600)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        done = {f.stem for f in raw_files if f.with_name(f.stem + "_anonymized" + f.suffix).exists()}
        if done:
            return done
    return set()


def _blur_regions(path) -> int:
    """Blurs faces + plates detected by Grounding DINO. Returns region count."""
    image = Image.open(path).convert("RGB")
    result = detect(image, config.ANON_PROMPT, config.ANON_BOX_THRESHOLD, config.ANON_BOX_THRESHOLD)
    img_area = image.width * image.height
    blurred = 0
    for x0, y0, x1, y1 in result["boxes"]:
        box = (int(max(0, x0)), int(max(0, y0)), int(min(image.width, x1)), int(min(image.height, y1)))
        if box[2] <= box[0] or box[3] <= box[1]:
            continue
        bw, bh = box[2] - box[0], box[3] - box[1]
        # Real faces/plates are small. Skip oversized false positives so we don't
        # paint giant gray rectangles over the scene. (Google Street View already
        # blurs faces/plates at source; this pass is defense-in-depth.)
        if bw * bh > 0.16 * img_area or bw > 0.6 * image.width or bh > 0.6 * image.height:
            continue
        region = image.crop(box)
        # Strong but bounded irreversible blur.
        radius = min(30, max(10, int(min(bw, bh) * 0.5)))
        region = region.filter(ImageFilter.GaussianBlur(radius=radius))
        image.paste(region, box)
        blurred += 1
    image.save(path, quality=92)
    return blurred


def main() -> int:
    config.ensure_dirs()

    raw_images = sorted(p for p in config.RAW_DIR.glob("*.jpg") if not p.stem.endswith("_anonymized"))
    raw_images += sorted(p for p in config.RAW_DIR.glob("*.png") if not p.stem.endswith("_anonymized"))
    if not raw_images:
        print(f"No raw images in {config.RAW_DIR}. Run fetch.py first.", file=sys.stderr)
        return 1

    print(f"deface (batch) on {len(raw_images)} image(s)...")
    defaced = _deface_batch(raw_images)

    for src in raw_images:
        dst = config.ANON_DIR / src.name
        defaced_path = src.with_name(src.stem + "_anonymized" + src.suffix)
        if defaced_path.exists():
            shutil.move(str(defaced_path), str(dst))
        else:
            shutil.copyfile(src, dst)  # deface missing -> rely on GD blur pass
        regions = _blur_regions(dst)
        print(f"[{src.name}] deface={'ok' if src.stem in defaced else 'no'} gd_blur_regions={regions}")

    # Clean up any stray deface outputs left in the raw dir.
    for leftover in config.RAW_DIR.glob("*_anonymized.*"):
        leftover.unlink()

    print(f"\nAnonymized {len(raw_images)} image(s) -> {config.ANON_DIR}")
    if len(defaced) < len(raw_images):
        print("WARN: deface didn't cover every image; the Grounding DINO blur pass still applied.")
    print(">> Faces & plates blurred. Detection may now read data/anon/ only (KVKK).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
