import math
from pathlib import Path

import yaml


def load_config(path=None):
    if path is None:
        path = Path(__file__).resolve().parents[2] / "configs/governance.yml"
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def validate_raci(df):
    if {"activity", "R", "A", "C", "I"} - set(df.columns):
        raise ValueError("RACI columns missing")
    if df.activity.duplicated().any():
        raise ValueError("Duplicate RACI activity")
    for row in df.fillna("").itertuples():
        accountable = [v.strip() for v in row.A.split(";") if v.strip()]
        responsible = [v.strip() for v in row.R.split(";") if v.strip()]
        if len(accountable) != 1 or not responsible:
            raise ValueError("Exactly one A and at least one R required")
    return True


def deployment_decision(
    metrics, gaps, resources, gates, privacy_ok=True, support_ok=True
):
    def valid(value):
        return value is not None and math.isfinite(float(value))

    checks = {
        "privacy": bool(privacy_ok),
        "support": bool(support_ok),
        "recall": valid(metrics.get("recall"))
        and metrics["recall"] >= gates["min_recall"],
        "recall_gap": valid(gaps.get("recall_gap"))
        and gaps["recall_gap"] <= gates["max_recall_gap"],
        "fpr_gap": valid(gaps.get("fpr_gap"))
        and gaps["fpr_gap"] <= gates["max_fpr_gap"],
        "latency": valid(resources.get("latency_ms"))
        and resources["latency_ms"] <= gates["max_latency_ms"],
        "model_size": valid(resources.get("model_kb"))
        and resources["model_kb"] <= gates["max_model_kb"],
    }
    if "max_training_seconds" in gates:
        checks["training_cost"] = (
            valid(resources.get("training_seconds"))
            and resources["training_seconds"] <= gates["max_training_seconds"]
        )
    checks = {k: bool(v) for k, v in checks.items()}
    failed = [k for k, v in checks.items() if not v]
    reasons = {k: "criterion_not_met" for k in failed}
    for name in ["recall_gap", "fpr_gap"]:
        if not valid(gaps.get(name)):
            reasons[name] = (
                "not_estimable_with_sufficient_support; not evidence of a measured excessive gap"
            )
    if not support_ok:
        reasons["support"] = (
            "At least one audited intersection lacks minimum count or class denominators"
        )
    return {
        "status": "STOP" if not privacy_ok else "REVIEW" if failed else "GO",
        "checks": checks,
        "failed": failed,
        "failure_reasons": reasons,
        "authority": "synthetic_sandbox_only",
        "human_action": "Revisión humana obligatoria; registrar justificación, apelación y responsable. Ninguna salida autoriza intervención real.",
    }
