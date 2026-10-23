import numpy as np
import pandas as pd
from fairlearn.metrics import MetricFrame, count, selection_rate
from sklearn.metrics import accuracy_score, precision_score


def rate(y, p, positive=True):
    y, p = np.asarray(y), np.asarray(p)
    mask = y == (1 if positive else 0)
    return float(p[mask].mean()) if mask.any() else np.nan


METRICS = {
    "count": count,
    "accuracy": accuracy_score,
    "selection_rate": selection_rate,
    "recall": rate,
    "precision": lambda y, p: precision_score(y, p, zero_division=0),
    "fpr": lambda y, p: rate(y, p, False),
}


def audit(y_true, y_pred, sensitive):
    mf = MetricFrame(
        metrics=METRICS, y_true=y_true, y_pred=y_pred, sensitive_features=sensitive
    )
    return mf.overall, mf.by_group, mf.difference(method="between_groups")


def intersectional(df):
    return df[["protected_group", "age_band"]].astype(str).agg(" | ".join, axis=1)


def gap(by_group, metric):
    values = pd.to_numeric(by_group[metric], errors="coerce").dropna()
    return float(values.max() - values.min()) if len(values) >= 2 else float("nan")


def wilson(successes, n):
    if n == 0:
        return np.nan, np.nan
    z = 1.96
    p = successes / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0, centre - half), min(1, centre + half)


def supported_audit(y, p, groups, min_count=30, min_class=10):
    overall, table, _ = audit(y, p, groups)
    work = pd.DataFrame(
        {"y": np.asarray(y), "p": np.asarray(p), "group": np.asarray(groups)}
    )
    for group, part in work.groupby("group"):
        pos = part.y.eq(1)
        neg = ~pos
        table.loc[group, "positive_count"] = int(pos.sum())
        table.loc[group, "negative_count"] = int(neg.sum())
        table.loc[group, "supported"] = bool(
            len(part) >= min_count and pos.sum() >= min_class and neg.sum() >= min_class
        )
        for metric, mask in [
            ("recall", pos),
            ("fpr", neg),
            ("selection_rate", np.ones(len(part), dtype=bool)),
        ]:
            lo, hi = wilson(int(part.loc[mask, "p"].sum()), int(np.sum(mask)))
            table.loc[group, metric + "_ci_low"] = lo
            table.loc[group, metric + "_ci_high"] = hi
    table["supported"] = table["supported"].astype(bool)
    eligible = table.loc[table.supported]
    return (
        overall,
        table,
        {
            metric: gap(eligible, metric)
            for metric in ["recall", "fpr", "selection_rate"]
        },
    )
