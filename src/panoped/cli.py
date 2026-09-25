"""Portable training and inference on frozen detector-query banks.

The model and update rule are the paper's S branch. The third-party detector
and tracker remain separate. The bank adapter must preserve original query
order, boxes, confidences and physical track IDs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from pathlib import Path

import numpy as np
import torch

from .sextant import LocalizationCalibrator, decode_correction, encode_correction


FIELDS = ("query", "base", "confidence")


def _load_bank(path: Path, *, training: bool) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        required = set(FIELDS) | ({"native"} if training else set())
        if not required.issubset(archive.files):
            raise ValueError(f"{path}: missing {sorted(required - set(archive.files))}")
        data = {key: archive[key] for key in archive.files}
    n = len(data["base"])
    if data["query"].shape != (n, 256) or data["base"].shape != (n, 7) or data["confidence"].shape != (n,):
        raise ValueError(f"{path}: expected aligned query[N,256], base[N,7], confidence[N]")
    if training and data["native"].shape != (n, 7):
        raise ValueError(f"{path}: expected native[N,7]")
    for key in required:
        if data[key].dtype != np.float32 or not np.isfinite(data[key]).all():
            raise ValueError(f"{path}: {key} must be finite float32")
    if n == 0:
        raise ValueError(f"{path}: empty bank")
    if np.any((data["confidence"] < 0) | (data["confidence"] > 1)):
        raise ValueError(f"{path}: confidence must be a probability")
    return data


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def train(args: argparse.Namespace) -> None:
    paths = sorted(args.bank_dir.glob("*.npz"))
    if not paths:
        raise ValueError("No per-sequence .npz banks found")
    if args.output.exists():
        raise FileExistsError(args.output)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    generator = np.random.default_rng(args.seed)
    device = torch.device(args.device)
    banks = []
    provenance = {}
    for path in paths:
        item = _load_bank(path, training=True)
        base = torch.from_numpy(item["base"])
        native = torch.from_numpy(item["native"])
        item["target"] = encode_correction(base, native).numpy()
        banks.append({key: torch.from_numpy(item[key]).to(device) for key in (*FIELDS, "target")})
        provenance[path.name] = _sha(path)
    model = LocalizationCalibrator().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    start = time.monotonic()
    for step in range(1, args.steps + 1):
        sequence = int(generator.integers(len(banks)))
        bank = banks[sequence]
        index = torch.from_numpy(generator.integers(len(bank["query"]), size=256)).to(device)
        predicted = model(bank["query"][index], bank["base"][index], bank["confidence"][index])
        loss = torch.nn.functional.smooth_l1_loss(predicted, bank["target"][index], beta=1.0)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        optimizer.step()
        if step % args.log_every == 0 or step == args.steps:
            print(json.dumps({"step": step, "loss": float(loss), "elapsed_s": round(time.monotonic() - start, 2)}), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.cpu().state_dict(), "metadata": {
        "architecture": "LocalizationCalibrator", "seed": args.seed, "steps": args.steps,
        "optimizer": "AdamW", "learning_rate": 3e-4, "weight_decay": 1e-4,
        "batch": 256, "clip_norm": 1.0, "sequence_sampling": "uniform",
        "bank_sha256": provenance, "parameter_count": sum(p.numel() for p in model.parameters()),
    }}, args.output)
    print(json.dumps({"checkpoint": str(args.output), "sha256": _sha(args.output)}))


def apply(args: argparse.Namespace) -> None:
    bank = _load_bank(args.bank, training=False)
    if args.output.exists():
        raise FileExistsError(args.output)
    checkpoint = torch.load(args.model, map_location="cpu", weights_only=True)
    model = LocalizationCalibrator().eval()
    model.load_state_dict(checkpoint["model"], strict=True)
    output = []
    with torch.inference_mode():
        for offset in range(0, len(bank["base"]), args.batch):
            part = slice(offset, offset + args.batch)
            query = torch.from_numpy(bank["query"][part])
            base = torch.from_numpy(bank["base"][part])
            confidence = torch.from_numpy(bank["confidence"][part])
            corrected = decode_correction(base, model(query, base, confidence))
            output.append(corrected.numpy())
    result = {key: value for key, value in bank.items() if key not in FIELDS}
    result["native_parameters"] = np.concatenate(output)
    np.savez_compressed(args.output, **result)
    print(json.dumps({"output": str(args.output), "sha256": _sha(args.output), "rows": len(bank["base"])}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    training = sub.add_parser("train", help="fit the S-native query readout on training banks only")
    training.add_argument("--bank-dir", type=Path, required=True)
    training.add_argument("--output", type=Path, required=True)
    training.add_argument("--seed", type=int, required=True)
    training.add_argument("--steps", type=int, default=25000)
    training.add_argument("--device", default="cuda")
    training.add_argument("--log-every", type=int, default=500)
    training.set_defaults(func=train)
    applying = sub.add_parser("apply", help="adjust localization while preserving identity and output support")
    applying.add_argument("--bank", type=Path, required=True)
    applying.add_argument("--model", type=Path, required=True)
    applying.add_argument("--output", type=Path, required=True)
    applying.add_argument("--batch", type=int, default=4096)
    applying.set_defaults(func=apply)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
