import math

import numpy as np
import torch

from panoped.cli import _load_bank
from panoped.sextant import LocalizationCalibrator, decode_correction, encode_correction


def sample_base(n=3):
    longitudes = torch.tensor([math.pi - 0.02, -math.pi + 0.01, 0.2][:n])
    latitudes = torch.tensor([0.1, -0.2, 0.0][:n])
    rays = torch.stack((
        latitudes.cos() * longitudes.sin(),
        latitudes.sin(),
        latitudes.cos() * longitudes.cos(),
    ), dim=-1)
    return torch.cat((rays, torch.full((n, 2), -1.0), torch.ones(n, 1), torch.zeros(n, 1)), dim=-1)


def test_parameter_count_and_zero_initialization():
    model = LocalizationCalibrator().eval()
    assert sum(p.numel() for p in model.parameters()) == 34692
    base = sample_base()
    query = torch.randn(len(base), 256)
    with torch.inference_mode():
        delta = model(query, base, torch.full((len(base),), 0.75))
        result = decode_correction(base, delta)
    assert torch.equal(delta, torch.zeros_like(delta))
    assert torch.equal(result, base)


def test_periodic_seam_target_roundtrip():
    base = sample_base(1)
    target = sample_base(2)[1:2].clone()
    residual = encode_correction(base, target)
    decoded = decode_correction(base, residual)
    assert residual[0, 0].abs() < 0.1  # short periodic displacement
    assert torch.allclose(decoded, target, atol=1e-6)


def test_bank_rejects_unmatched_rows(tmp_path):
    path = tmp_path / "wrong.npz"
    np.savez(path, query=np.zeros((2, 256), np.float32),
             base=np.zeros((3, 7), np.float32),
             confidence=np.zeros(3, np.float32))
    try:
        _load_bank(path, training=False)
    except ValueError as error:
        assert "aligned" in str(error)
    else:
        raise AssertionError("Unmatched frozen queries accepted")
