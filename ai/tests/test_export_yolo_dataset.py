from __future__ import annotations

import io
import json
from pathlib import Path

from PIL import Image

from kostreet_ai.training.export_yolo_dataset import export_dataset


def test_export_dataset_writes_yaml_and_splits(tmp_path: Path, monkeypatch) -> None:
    eval_dir = tmp_path / "eval"
    images_dir = eval_dir / "images" / "garbage"
    images_dir.mkdir(parents=True)
    image_path = images_dir / "garbage_01.jpg"
    buffer = io.BytesIO()
    Image.new("RGB", (64, 64), color=(90, 120, 60)).save(buffer, format="JPEG")
    image_path.write_bytes(buffer.getvalue())

    manifest = [
        {
            "id": "garbage_01",
            "filename": "images/garbage/garbage_01.jpg",
            "expected_category": "garbage",
            "expected_civic": True,
        }
    ]
    eval_dir.mkdir(exist_ok=True)
    (eval_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    output_dir = tmp_path / "processed" / "yolo_garbage"
    monkeypatch.setattr("kostreet_ai.training.export_yolo_dataset.EVAL_DIR", eval_dir)
    monkeypatch.setattr("kostreet_ai.training.export_yolo_dataset.MANIFEST_FILE", eval_dir / "manifest.json")
    monkeypatch.setattr("kostreet_ai.training.export_yolo_dataset.OUTPUT_DIR", output_dir)
    monkeypatch.setattr("kostreet_ai.training.export_yolo_dataset.DATASET_YAML", output_dir / "dataset.yaml")

    yaml_path = export_dataset(augment_multiplier=1, val_ratio=0.5, seed=1)
    assert yaml_path.exists()
    assert (output_dir / "train" / "images").exists()
    assert (output_dir / "val" / "images").exists()
    assert any((output_dir / "train" / "labels").glob("*.txt"))
