"""Chronological fit/validation/test; thresholds selected without test access."""

import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .data import features, load_data, temporal_split
from .fairness import intersectional, supported_audit
from .governance import deployment_decision, load_config
from .model import build_model, fit_measure

ROOT = Path(__file__).resolve().parents[2]


def clean_json(value):
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        return None
    if isinstance(value, np.generic):
        return value.item()
    return value


def evaluate(model, frame, threshold):
    probability = model.predict_proba(features(frame))[:, list(model.classes_).index(1)]
    pred = (probability >= threshold).astype(int)
    return pred, probability


def audit_frame(frame, pred, config):
    overall, group, gaps = supported_audit(
        frame.target, pred, frame.protected_group, **config["support"]
    )
    _, inter, inter_gaps = supported_audit(
        frame.target, pred, intersectional(frame), **config["support"]
    )
    return overall, group, inter, gaps, inter_gaps


def run_experiments():
    config = load_config()
    data = load_data()
    train, test = temporal_split(data)
    fit, validation = temporal_split(train, test_fraction=0.2)
    folder = ROOT / "reports/lab12"
    folder.mkdir(parents=True, exist_ok=True)
    candidates = []
    models = {}
    resources = {}
    for kind in ["dummy", "logistic", "tree"]:
        model = build_model(kind)
        resources[kind] = fit_measure(
            model, features(fit), fit.target, ROOT / f"models/{kind}.joblib"
        )
        models[kind] = model
        for threshold in [0.5] if kind == "dummy" else [0.3, 0.4, 0.5, 0.6, 0.7]:
            pred, _ = evaluate(model, validation, threshold)
            overall, g, inter, gaps, ig = audit_frame(validation, pred, config)
            candidates.append(
                {
                    "model": kind,
                    "threshold": threshold,
                    **{k: float(v) for k, v in overall.items()},
                    "recall_gap": gaps["recall"],
                    "fpr_gap": gaps["fpr"],
                    "selection_rule_eligible": bool(
                        overall["recall"] >= config["gates"]["min_recall"]
                        and gaps["recall"] <= config["gates"]["max_recall_gap"]
                        and gaps["fpr"] <= config["gates"]["max_fpr_gap"]
                    ),
                    **resources[kind],
                }
            )
    choices = pd.DataFrame(candidates)
    choices.to_csv(folder / "validation_candidates.csv", index=False)
    # User prioritized omissions: among nondummy candidates passing main-group point gates,
    # maximize recall, then minimize FPR, time, model bytes. Support remains a final gate.
    eligible = choices[(choices.model != "dummy") & choices.selection_rule_eligible]
    pool = eligible if not eligible.empty else choices[choices.model != "dummy"]
    chosen = pool.sort_values(
        ["recall", "fpr", "training_seconds", "model_kb"],
        ascending=[False, True, True, True],
    ).iloc[0]
    selected = {
        "model": chosen.model,
        "threshold": float(chosen.threshold),
        "selected_on": "validation_only",
        "rule": "recall first; FPR, training time and serialized size as tie breakers; dummy is a reference, not an operational choice",
        "no_eligible_candidate": eligible.empty,
    }
    selected_path = folder / "selection.json"
    selected_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")
    results = []
    # Freeze choice before computing any test metrics. Evaluate all alternatives for comparison only.
    alternatives = [
        ("dummy", 0.5),
        ("logistic", 0.5),
        ("tree", 0.5),
        (chosen.model, float(chosen.threshold)),
    ]
    for index, (kind, threshold) in enumerate(alternatives):
        label = f"{kind}_t{threshold:.1f}" + ("_selected" if index == 3 else "")
        model = models[kind]
        start = time.perf_counter()
        pred, prob = evaluate(model, test, threshold)
        latency = (time.perf_counter() - start) * 1000 / len(test)
        overall, g, inter, gaps, ig = audit_frame(test, pred, config)
        out = folder / label
        out.mkdir(exist_ok=True)
        g.to_csv(out / "fairness_by_group.csv")
        inter.to_csv(out / "fairness_intersectional.csv")
        combined = {
            "recall_gap": max(gaps["recall"], ig["recall"])
            if np.isfinite(ig["recall"])
            else float("nan"),
            "fpr_gap": max(gaps["fpr"], ig["fpr"])
            if np.isfinite(ig["fpr"])
            else float("nan"),
        }
        costs = {**resources[kind], "latency_ms": latency}
        support_ok = bool(g.supported.all() and inter.supported.all())
        decision = deployment_decision(
            overall,
            combined,
            costs,
            config["gates"],
            privacy_ok=True,
            support_ok=support_ok,
        )
        row = {
            "label": label,
            "model": kind,
            "threshold": threshold,
            "split": "test",
            **{k: float(v) for k, v in overall.items()},
            "recall_gap": gaps["recall"],
            "fpr_gap": gaps["fpr"],
            "intersection_recall_gap_supported": ig["recall"],
            "intersection_fpr_gap_supported": ig["fpr"],
            "supported_intersections": int(inter.supported.sum()),
            "total_intersections": len(inter),
            "support_ok": support_ok,
            **costs,
            "status": decision["status"],
        }
        results.append(row)
        (out / "global_metrics.json").write_text(
            json.dumps(
                clean_json({"result": row, "decision": decision}),
                indent=2,
                allow_nan=False,
            ),
            encoding="utf-8",
        )
        if index == 3:
            (folder / "global_metrics.json").write_bytes(
                (out / "global_metrics.json").read_bytes()
            )
            pd.DataFrame(
                {
                    "case_id": test.case_id,
                    "received_date": test.received_date.astype(str),
                    "probability": prob,
                    "predicted_review": pred,
                }
            ).to_csv(folder / "selected_predictions.csv", index=False)
            (folder / "selected_decision.json").write_text(
                json.dumps(decision, indent=2), encoding="utf-8"
            )
            g.to_csv(folder / "fairness_by_group.csv")
            inter.to_csv(folder / "fairness_intersectional.csv")
    pd.DataFrame(results).to_csv(folder / "comparison.csv", index=False)
    split = {
        "fit_n": len(fit),
        "validation_n": len(validation),
        "test_n": len(test),
        "fit_end": str(fit.received_date.max()),
        "validation_start": str(validation.received_date.min()),
        "validation_end": str(validation.received_date.max()),
        "test_start": str(test.received_date.min()),
        "dataset_sha256": hashlib.sha256(
            (ROOT / "data/territorial_risk_synthetic.csv").read_bytes()
        ).hexdigest(),
        "excluded_predictors": [
            "case_id",
            "received_date",
            "target",
            "protected_group",
            "age_band",
        ],
        "features": list(features(fit).columns),
        "dates_are_synthetic": True,
        "target_counts": data.target.value_counts().to_dict(),
        "groups": data.protected_group.value_counts().to_dict(),
    }
    (folder / "data_audit.json").write_text(
        json.dumps(split, indent=2), encoding="utf-8"
    )
    print(pd.DataFrame(results).to_string(index=False))
    return selected, results
