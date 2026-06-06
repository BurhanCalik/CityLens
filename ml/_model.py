"""Shared, cached Grounding DINO loader + a version-tolerant detect helper.

Grounding DINO is a zero-shot (open-vocabulary) detector: it finds whatever the
text prompt describes, so the same model powers both anonymization (faces/plates)
and target detection without any training.
"""

from __future__ import annotations

import functools
from typing import Any

import config


@functools.lru_cache(maxsize=1)
def load_grounding_dino():
    """Loads the processor + model once and caches them for the process."""
    import torch
    from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[model] loading Grounding DINO from {config.GROUNDING_DINO_MODEL} on {device} ...")
    processor = AutoProcessor.from_pretrained(config.GROUNDING_DINO_MODEL)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(
        config.GROUNDING_DINO_MODEL,
        # Pure-PyTorch path: avoids the optional CUDA deformable-attention kernel
        # which is not available on CPU / fresh installs.
        disable_custom_kernels=True,
    ).to(device)
    model.eval()
    return processor, model, device


def detect(image, prompt: str, box_threshold: float, text_threshold: float) -> dict[str, Any]:
    """Runs zero-shot detection and returns {'scores', 'boxes', 'labels'}.

    Tolerant to the transformers API change in post_process_grounded_object_detection
    (older: box_threshold=...; newer: threshold=...).
    """
    import torch

    processor, model, device = load_grounding_dino()
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs)

    target_sizes = [image.size[::-1]]  # (height, width)
    try:
        results = processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            box_threshold=box_threshold,
            text_threshold=text_threshold,
            target_sizes=target_sizes,
        )[0]
    except TypeError:
        results = processor.post_process_grounded_object_detection(
            outputs,
            threshold=box_threshold,
            text_threshold=text_threshold,
            target_sizes=target_sizes,
        )[0]

    # Normalize label key across versions.
    labels = results.get("text_labels", results.get("labels", []))
    return {
        "scores": [float(s) for s in results["scores"]],
        "boxes": [[float(v) for v in box] for box in results["boxes"]],
        "labels": [str(l) for l in labels],
    }
