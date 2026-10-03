"""Verify exported paper-grade state dictionaries and their metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch

import cloud_ris_adapter_lightning as base


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights-dir", type=Path, default=Path("weights/v1.0.3"))
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    args = parser.parse_args()
    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA requested but unavailable")
    root = args.weights_dir
    metadata_path = root / "weights_manifest.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("schema") != "ris-adaptation-weights/1.0":
        raise SystemExit("unsupported weight manifest schema")
    checked = 0
    for entry in metadata["entries"]:
        path = root / entry["file"]
        if digest(path) != entry["sha256"]:
            raise SystemExit(f"sha256 mismatch: {path}")
        state = torch.load(path, map_location=args.device, weights_only=True)
        if entry["model_type"] == "source_estimator":
            model = base.SourceEstimator().to(args.device)
            expected = 115328
            sample = torch.zeros(2, 2 * base.N_SUBCARRIERS * base.PILOT_COUNT, device=args.device)
        elif entry["model_type"] == "canonical_adapter_final_state":
            model = base.LightweightAdapter().to(args.device)
            expected = 16576
            sample = torch.zeros(2, 2 * base.N_SUBCARRIERS * base.N_TX, device=args.device)
        else:
            raise SystemExit(f"unknown model type: {entry['model_type']}")
        model.load_state_dict(state, strict=True)
        model.eval()
        output = model(sample)
        if not torch.isfinite(output).all():
            raise SystemExit(f"non-finite output: {path}")
        parameter_count = sum(parameter.numel() for parameter in model.parameters())
        if parameter_count != expected or entry["parameter_count"] != expected:
            raise SystemExit(f"parameter count mismatch: {path}")
        checked += 1
    print(json.dumps({"verified_entries": checked, "status": "pass"}, indent=2))


if __name__ == "__main__":
    main()
