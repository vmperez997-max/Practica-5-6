import json
from pathlib import Path

import pandas as pd

from inf8239_u04.data import features, load_data, validate_schema
from inf8239_u04.experiment import clean_json
from inf8239_u04.governance import deployment_decision, load_config, validate_raci
from inf8239_u04.pipeline import recommend, sha

root = Path(__file__).resolve().parents[1]
out = root / "reports/lab13"
out.mkdir(parents=True, exist_ok=True)


def execute():
    cfg = load_config()
    validate_raci(pd.read_csv(root / "student_inputs/raci.csv"))
    df = load_data()
    comparison = pd.read_csv(root / "reports/lab12/comparison.csv")
    row = comparison[comparison.label.str.endswith("_selected")].iloc[0]
    gaps = {
        "recall_gap": row.intersection_recall_gap_supported,
        "fpr_gap": row.intersection_fpr_gap_supported,
    }
    group = pd.read_csv(root / "reports/lab12/fairness_by_group.csv", index_col=0)
    for metric in ["recall", "fpr"]:
        gaps[metric + "_gap"] = (
            max(
                float(group[metric].max() - group[metric].min()),
                float(gaps[metric + "_gap"]),
            )
            if pd.notna(gaps[metric + "_gap"])
            else float("nan")
        )
    decision = deployment_decision(
        {"recall": row.recall},
        gaps,
        row.to_dict(),
        cfg["gates"],
        privacy_ok=True,
        support_ok=bool(row.support_ok),
    )
    payload = {
        "decision": decision,
        "selected": row.to_dict(),
        "policy_version": cfg["policy_version"],
        "policy_sha256": sha(root / "configs/governance.yml"),
        "model_sha256": sha(root / f"models/{row.model}.joblib"),
        "dataset_sha256": sha(root / "data/territorial_risk_synthetic.csv"),
        "human_owner": "Institutional Owner (rol simulado)",
        "student_priority": "No omitir zonas que necesitan revisión humana; elección explícita",
        "evidence": [
            "reports/lab12/comparison.csv",
            "reports/lab12/fairness_intersectional.csv",
            "student_inputs/raci.csv",
        ],
    }
    (out / "deployment_decision.json").write_text(
        json.dumps(clean_json(payload), indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    controls = {}
    for forbidden in cfg["direct_identifiers"]:
        try:
            validate_schema(df.assign(**{forbidden: "SYNTHETIC_TEST"}))
        except ValueError:
            controls[forbidden] = "REJECTED_BEFORE_PREDICTION"
        else:
            raise AssertionError("Forbidden column accepted")
    controls["sensitive_excluded"] = not bool(
        set(cfg["sensitive_features"]) & set(features(df).columns)
    )
    (out / "control_tests.json").write_text(
        json.dumps(controls, indent=2), encoding="utf-8"
    )
    records = recommend(df.tail(5))
    (out / "recommendations.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    # Observed drift across validation and test, not a claim of causal or future drift.
    audit = json.loads(
        (root / "reports/lab12/data_audit.json").read_text(encoding="utf-8")
    )
    validation = df[
        (df.received_date >= pd.Timestamp(audit["validation_start"]))
        & (df.received_date <= pd.Timestamp(audit["validation_end"]))
    ]
    test = df[df.received_date >= pd.Timestamp(audit["test_start"])]
    monitor = {
        "baseline_window": "validation",
        "current_window": "test",
        "labels_available": True,
        "scope": "observed synthetic retrospective comparison",
        "exposure_mean_baseline": float(validation.exposure.mean()),
        "exposure_mean_current": float(test.exposure.mean()),
        "absolute_exposure_shift": float(
            abs(validation.exposure.mean() - test.exposure.mean())
        ),
        "proposed_drift_threshold": 0.1,
        "status": "REVIEW"
        if abs(validation.exposure.mean() - test.exposure.mean()) > 0.1
        else "NO_EXPOSURE_MEAN_ALERT",
        "limitation": "One marginal mean check is not a complete drift detector; delayed labels prevent immediate recall monitoring.",
    }
    (out / "monitoring.json").write_text(
        json.dumps(monitor, indent=2), encoding="utf-8"
    )
    print(json.dumps(decision, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        execute()
    except (ValueError, FileNotFoundError, KeyError) as exc:
        (out / "deployment_decision.json").write_text(
            json.dumps(
                {
                    "decision": {"status": "STOP", "failed": ["invalid_prerequisite"]},
                    "reason": str(exc),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        raise
