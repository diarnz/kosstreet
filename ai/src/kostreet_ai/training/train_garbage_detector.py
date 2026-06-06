"""
Fine-tune YOLOv8-nano on the exported garbage dataset and copy weights to models/.

Run from ai/:

    pip install -e ".[models]"
    python -m kostreet_ai.training.export_yolo_dataset
    python -m kostreet_ai.training.train_garbage_detector --epochs 40
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[3]
DATASET_YAML = AI_ROOT / "data" / "processed" / "yolo_garbage" / "dataset.yaml"
MODELS_DIR = AI_ROOT / "models"
DEFAULT_OUTPUT = MODELS_DIR / "garbage_yolov8n.pt"


def train(
    *,
    epochs: int = 40,
    image_size: int = 640,
    batch_size: int = 8,
    output_path: Path = DEFAULT_OUTPUT,
    export_first: bool = True,
) -> Path:
    if export_first or not DATASET_YAML.exists():
        from kostreet_ai.training.export_yolo_dataset import export_dataset

        export_dataset()

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError('Install model extras first: pip install -e ".[models]"') from exc

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model = YOLO("yolov8n.pt")
    results = model.train(
        data=str(DATASET_YAML),
        epochs=epochs,
        imgsz=image_size,
        batch=batch_size,
        project=str(AI_ROOT / "data" / "processed" / "yolo_runs"),
        name="garbage_detector",
        exist_ok=True,
        verbose=True,
    )

    best_weights = Path(results.save_dir) / "weights" / "best.pt"
    if not best_weights.exists():
        raise FileNotFoundError(f"Training finished without best.pt at {best_weights}")

    shutil.copy2(best_weights, output_path)
    print(f"\nSaved garbage detector to {output_path}")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train local garbage YOLO detector")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Reuse existing data/processed/yolo_garbage dataset",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train(
        epochs=args.epochs,
        image_size=args.imgsz,
        batch_size=args.batch,
        output_path=args.output,
        export_first=not args.skip_export,
    )


if __name__ == "__main__":
    main()
