"""
Export a single-class YOLO garbage dataset from eval images and optional TACO COCO labels.

Run from ai/:

    python -m kostreet_ai.training.export_yolo_dataset
    python -m kostreet_ai.training.export_yolo_dataset --taco data/raw/taco/annotations.json
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path

from PIL import Image

AI_ROOT = Path(__file__).resolve().parents[3]
EVAL_DIR = AI_ROOT / "data" / "eval"
MANIFEST_FILE = EVAL_DIR / "manifest.json"
OUTPUT_DIR = AI_ROOT / "data" / "processed" / "yolo_garbage"
DATASET_YAML = OUTPUT_DIR / "dataset.yaml"

GARBAGE_CLASS_NAME = "garbage"
DEFAULT_CENTER_BOX = (0.5, 0.5, 0.85, 0.85)


def _write_yolo_label(label_path: Path, boxes: list[tuple[float, float, float, float]]) -> None:
    lines = [f"0 {x:.6f} {y:.6f} {w:.6f} {h:.6f}" for x, y, w, h in boxes]
    label_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _coco_bbox_to_yolo(
    bbox: list[float],
    image_width: int,
    image_height: int,
) -> tuple[float, float, float, float] | None:
    x, y, width, height = bbox
    if width <= 0 or height <= 0 or image_width <= 0 or image_height <= 0:
        return None
    x_center = (x + width / 2) / image_width
    y_center = (y + height / 2) / image_height
    norm_w = width / image_width
    norm_h = height / image_height
    if not (0 < norm_w <= 1 and 0 < norm_h <= 1):
        return None
    return (
        min(max(x_center, 0.0), 1.0),
        min(max(y_center, 0.0), 1.0),
        min(max(norm_w, 0.0), 1.0),
        min(max(norm_h, 0.0), 1.0),
    )


def _export_eval_garbage_samples() -> list[tuple[Path, list[tuple[float, float, float, float]]]]:
    if not MANIFEST_FILE.exists():
        raise FileNotFoundError(f"Eval manifest not found: {MANIFEST_FILE}")

    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    samples: list[tuple[Path, list[tuple[float, float, float, float]]]] = []

    for entry in manifest:
        if entry.get("expected_category") != "garbage" or not entry.get("expected_civic", True):
            continue
        image_path = EVAL_DIR / entry["filename"]
        if not image_path.exists():
            continue
        samples.append((image_path, [DEFAULT_CENTER_BOX]))

    return samples


def _export_taco_samples(
    annotations_path: Path,
    images_root: Path | None = None,
) -> list[tuple[Path, list[tuple[float, float, float, float]]]]:
    taco = json.loads(annotations_path.read_text(encoding="utf-8"))
    images_by_id = {item["id"]: item for item in taco.get("images", [])}
    root = images_root or annotations_path.parent

    samples: list[tuple[Path, list[tuple[float, float, float, float]]]] = []
    boxes_by_image: dict[int, list[tuple[float, float, float, float]]] = {}

    for annotation in taco.get("annotations", []):
        image_info = images_by_id.get(annotation["image_id"])
        if image_info is None:
            continue
        converted = _coco_bbox_to_yolo(
            annotation["bbox"],
            image_info["width"],
            image_info["height"],
        )
        if converted is None:
            continue
        boxes_by_image.setdefault(annotation["image_id"], []).append(converted)

    for image_id, boxes in boxes_by_image.items():
        image_info = images_by_id[image_id]
        image_path = root / image_info["file_name"]
        if image_path.exists():
            samples.append((image_path, boxes))

    return samples


def _augment_samples(
    samples: list[tuple[Path, list[tuple[float, float, float, float]]]],
    *,
    multiplier: int,
    output_dir: Path,
) -> list[tuple[Path, list[tuple[float, float, float, float]]]]:
    if multiplier <= 1:
        return samples

    augmented: list[tuple[Path, list[tuple[float, float, float, float]]]] = list(samples)
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, (image_path, boxes) in enumerate(samples, start=1):
        with Image.open(image_path) as img:
            rgb = img.convert("RGB")
            for variant in range(1, multiplier):
                canvas = rgb.transpose(Image.FLIP_LEFT_RIGHT if variant % 2 else Image.FLIP_TOP_BOTTOM)
                dest = output_dir / f"aug_{index:03d}_{variant}.jpg"
                canvas.save(dest, format="JPEG", quality=90)
                flipped_boxes = []
                for x, y, w, h in boxes:
                    if variant % 2:
                        flipped_boxes.append((1.0 - x, y, w, h))
                    else:
                        flipped_boxes.append((x, 1.0 - y, w, h))
                augmented.append((dest, flipped_boxes))

    return augmented


def _materialize_split(
    samples: list[tuple[Path, list[tuple[float, float, float, float]]]],
    *,
    val_ratio: float,
    seed: int,
) -> tuple[list[tuple[Path, list[tuple[float, float, float, float]]]], list[tuple[Path, list[tuple[float, float, float, float]]]]]:
    rng = random.Random(seed)
    shuffled = list(samples)
    rng.shuffle(shuffled)
    if len(shuffled) < 2:
        return shuffled, shuffled[-1:]
    val_count = max(1, int(len(shuffled) * val_ratio))
    val_samples = shuffled[:val_count]
    train_samples = shuffled[val_count:] or shuffled[:-1]
    return train_samples, val_samples


def _write_split(
    split_name: str,
    samples: list[tuple[Path, list[tuple[float, float, float, float]]]],
) -> int:
    images_dir = OUTPUT_DIR / split_name / "images"
    labels_dir = OUTPUT_DIR / split_name / "labels"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    for index, (image_path, boxes) in enumerate(samples, start=1):
        dest_image = images_dir / f"{split_name}_{index:04d}{image_path.suffix.lower()}"
        dest_label = labels_dir / f"{dest_image.stem}.txt"
        shutil.copy2(image_path, dest_image)
        _write_yolo_label(dest_label, boxes)

    return len(samples)


def write_dataset_yaml() -> None:
    yaml = f"""path: {OUTPUT_DIR.as_posix()}
train: train/images
val: val/images
names:
  0: {GARBAGE_CLASS_NAME}
"""
    DATASET_YAML.write_text(yaml, encoding="utf-8")


def export_dataset(
    *,
    taco_annotations: Path | None = None,
    taco_images_root: Path | None = None,
    augment_multiplier: int = 3,
    val_ratio: float = 0.2,
    seed: int = 42,
) -> Path:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    samples = _export_eval_garbage_samples()
    if taco_annotations is not None:
        samples.extend(_export_taco_samples(taco_annotations, taco_images_root))

    if not samples:
        raise RuntimeError("No garbage training samples found. Run data/eval/bootstrap_dataset.py first.")

    aug_dir = OUTPUT_DIR / "_augmented"
    samples = _augment_samples(samples, multiplier=augment_multiplier, output_dir=aug_dir)
    train_samples, val_samples = _materialize_split(samples, val_ratio=val_ratio, seed=seed)

    train_count = _write_split("train", train_samples)
    val_count = _write_split("val", val_samples)
    write_dataset_yaml()

    if aug_dir.exists():
        shutil.rmtree(aug_dir)

    print(f"YOLO dataset written to {OUTPUT_DIR}")
    print(f"  train images: {train_count}")
    print(f"  val images  : {val_count}")
    print(f"  yaml        : {DATASET_YAML}")
    return DATASET_YAML


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export YOLO garbage dataset")
    parser.add_argument("--taco", type=Path, default=None, help="Optional TACO COCO annotations.json")
    parser.add_argument("--taco-images", type=Path, default=None, help="Root folder for TACO images")
    parser.add_argument("--augment", type=int, default=3, help="Augmentation multiplier per source image")
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Validation split ratio")
    parser.add_argument("--seed", type=int, default=42, help="Shuffle seed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    export_dataset(
        taco_annotations=args.taco,
        taco_images_root=args.taco_images,
        augment_multiplier=args.augment,
        val_ratio=args.val_ratio,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
