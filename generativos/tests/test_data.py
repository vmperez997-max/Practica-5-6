import struct

import numpy as np
import pytest

from inf8239_lab10.data import normalize, parse_idx, split_training


def test_idx_magic_and_length_validation():
    image = bytes(784)
    data = struct.pack(">IIII", 2051, 1, 28, 28) + image
    assert parse_idx(data).shape == (1, 28, 28, 1)
    for invalid in [struct.pack(">I", 99), data[:-1]]:
        with pytest.raises(ValueError):
            parse_idx(invalid)


def test_labels_reject_invalid_class():
    with pytest.raises(ValueError):
        parse_idx(struct.pack(">II", 2049, 1) + bytes([10]))


def test_normalization_preserves_shape_and_range():
    raw = np.full((2, 28, 28, 1), 255, dtype=np.uint8)
    out = normalize(raw)
    assert out.dtype == np.float32 and out.shape == raw.shape
    assert out.min() == out.max() == 1
    with pytest.raises(ValueError):
        normalize(out)


def test_split_is_disjoint_reproducible_and_limit_only_affects_fit():
    labels = np.tile(np.arange(10), 1200)
    x = np.zeros((12000, 1))
    fit, val = split_training(x, labels)
    limited, val2 = split_training(x, labels, limit=1000)
    assert not set(fit) & set(val)
    assert len(fit) + len(val) == 12000
    assert np.array_equal(val, val2) and set(limited) <= set(fit)
    assert np.array_equal(fit, split_training(x, labels)[0])
