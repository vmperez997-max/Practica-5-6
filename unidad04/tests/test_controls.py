from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from inf8239_u04.data import features, load_data, temporal_split, validate_schema
from inf8239_u04.fairness import gap, supported_audit
from inf8239_u04.governance import deployment_decision, load_config, validate_raci
from inf8239_u04.impact import score_risks
from inf8239_u04.pipeline import recommend


def test_sensitive_columns_do_not_enter_transformer():
    assert not {
        "protected_group",
        "age_band",
        "case_id",
        "target",
        "received_date",
    } & set(features(load_data()).columns)


@pytest.mark.parametrize(
    "fault", ["null", "duplicate", "range", "unexpected", "bad_date"]
)
def test_contract_rejects_bad_inputs(fault):
    df = load_data()
    if fault == "null":
        df.loc[0, "zone"] = None
    elif fault == "duplicate":
        df.loc[0, "case_id"] = df.loc[1, "case_id"]
    elif fault == "range":
        df.loc[0, "exposure"] = 2
    elif fault == "unexpected":
        df["extra_data"] = "x"
    else:
        df["received_date"] = df.received_date.astype(str)
        df.loc[0, "received_date"] = "bad-date"
    with pytest.raises(ValueError):
        validate_schema(df)


def test_temporal_split_is_strict_and_keeps_tied_dates_together():
    df = load_data().sample(frac=1, random_state=9)
    tr, te = temporal_split(df)
    fit, val = temporal_split(tr, 0.2)
    assert fit.received_date.max() < val.received_date.min() < te.received_date.min()
    assert len(fit) + len(val) + len(te) == len(df)


def test_zero_denominator_is_unknown_and_unsupported_is_not_a_zero_gap():
    _, table, gaps = supported_audit(
        np.array([0, 0, 1]), np.array([0, 1, 1]), ["a", "a", "b"]
    )
    assert table.supported.sum() == 0
    assert np.isnan(gaps["recall"]) and np.isnan(table.loc["a", "recall"])
    assert np.isnan(gap(table.iloc[:1], "recall"))


def test_privacy_failure_stops_and_unknown_gap_never_goes_green():
    cfg = load_config()["gates"]
    cost = {"latency_ms": 1, "model_kb": 1, "training_seconds": 0.1}
    assert (
        deployment_decision(
            {"recall": 1}, {"recall_gap": 0, "fpr_gap": 0}, cost, cfg, privacy_ok=False
        )["status"]
        == "STOP"
    )
    assert (
        deployment_decision(
            {"recall": 1}, {"recall_gap": np.nan, "fpr_gap": 0}, cost, cfg
        )["status"]
        == "REVIEW"
    )
    assert (
        deployment_decision(
            {"recall": 1}, {"recall_gap": 0, "fpr_gap": 0}, cost, cfg, support_ok=False
        )["status"]
        == "REVIEW"
    )


def test_exactly_one_accountable():
    df = pd.DataFrame(
        [{"activity": "deploy", "R": "ML", "A": "A;B", "C": "DS", "I": "Users"}]
    )
    with pytest.raises(ValueError):
        validate_raci(df)


def test_invalid_risk_scores_rejected():
    root = Path(__file__).resolve().parents[1]
    data = pd.read_csv(root / "student_inputs/risk_register.csv")
    data.loc[0, "likelihood_1_4"] = 5
    with pytest.raises(ValueError):
        score_risks(data)


def test_privacy_rejected_before_loading_model(monkeypatch):
    monkeypatch.setattr(
        "inf8239_u04.pipeline.joblib.load",
        lambda *_: pytest.fail("Must not load before schema validation"),
    )
    with pytest.raises(ValueError):
        recommend(load_data().head(1).assign(email="synthetic@example.invalid"))


def test_rollback_blocks_model_loading_and_removes_probability(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    if not (root / "reports/lab13/rollback_state.json").exists():
        pytest.skip("Run full laboratory first")
    monkeypatch.setattr(
        "inf8239_u04.pipeline.joblib.load",
        lambda *_: pytest.fail("Rollback must stop scoring"),
    )
    records = recommend(load_data().head(2))
    assert all(
        r["probability"] is None and r["priority"] == "cola_manual_completa"
        for r in records
    )
    assert all(
        r["policy_version"] and r["model_version"] and r["evidence"] for r in records
    )
