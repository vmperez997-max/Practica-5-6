import numpy as np


def reconstruction_metrics(x, predicted):
    if x.shape != predicted.shape:
        raise ValueError("Shape mismatch")
    p = np.clip(predicted, 1e-7, 1 - 1e-7)
    return {
        "mse": float(np.mean((x - predicted) ** 2)),
        "bce_per_pixel": float(np.mean(-(x * np.log(p) + (1 - x) * np.log(1 - p)))),
    }


def diversity(samples):
    x = np.asarray(samples).reshape(len(samples), -1)
    if len(x) < 2:
        raise ValueError("At least two samples required")
    # Mean squared distance between distinct pairs, no N^2 x 784 allocation.
    pair_mse = float(2 * len(x) / (len(x) - 1) * np.mean(np.var(x, axis=0)))
    return {
        "mean_pairwise_mse": pair_mse,
        "mean_pixel_std": float(np.std(x, axis=0).mean()),
    }
