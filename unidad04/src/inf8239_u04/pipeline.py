"""Traceable inference; no authority to intervene or to discard cases."""

import hashlib
import json
from pathlib import Path

import joblib

from .data import features, validate_schema

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def recommend(frame):
    validate_schema(frame)  # Must execute before loading a model or predicting.
    decision = json.loads(
        (ROOT / "reports/lab13/deployment_decision.json").read_text(encoding="utf-8")
    )
    selection = json.loads(
        (ROOT / "reports/lab12/selection.json").read_text(encoding="utf-8")
    )
    path = ROOT / f"models/{selection['model']}.joblib"
    if (
        decision["policy_sha256"] != sha(ROOT / "configs/governance.yml")
        or decision["dataset_sha256"]
        != sha(ROOT / "data/territorial_risk_synthetic.csv")
        or decision["model_sha256"] != sha(path)
    ):
        raise ValueError("Stale governance evidence; rerun audit before inference")
    rollback = ROOT / "reports/lab13/rollback_state.json"
    manual_only = (
        rollback.exists()
        and json.loads(rollback.read_text(encoding="utf-8"))["mode"] == "MANUAL_ONLY"
    )
    if manual_only or decision["decision"]["status"] == "STOP":
        probability = [None] * len(frame)
    else:
        model = joblib.load(path)  # Only locally trained, repository-trusted artifacts.
        probability = model.predict_proba(features(frame))[
            :, list(model.classes_).index(1)
        ]
    records = []
    for row, p in zip(frame.itertuples(), probability):
        records.append(
            {
                "case_id": row.case_id,
                "probability": float(p) if p is not None else None,
                "threshold": selection["threshold"],
                "priority": "cola_manual_completa"
                if p is None
                else "revisar_primero"
                if p >= selection["threshold"]
                else "cola_manual_sin_descartar",
                "deployment_status": decision["decision"]["status"],
                "model_version": sha(path)[:16],
                "policy_version": "u04-v1",
                "policy_sha256": sha(ROOT / "configs/governance.yml"),
                "evidence": "reports/lab13/deployment_decision.json",
                "authority": "SOLO_SIMULACION; no intervención, emergencia ni elegibilidad",
                "human_action": "Revisión obligatoria y registro de justificación; opción de anular o apelar.",
            }
        )
    return records
