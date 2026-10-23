REQUIRED_IMPACT = {
    "purpose",
    "assisted_decision",
    "users",
    "affected_population",
    "owner",
    "non_predictive_alternative",
    "out_of_scope_use",
    "withdrawal_condition",
    "appeal_mechanism",
}
REQUIRED_RISK = {
    "id",
    "scenario",
    "affected",
    "likelihood_1_4",
    "impact_1_4",
    "control",
    "owner",
    "evidence",
    "residual",
}


def validate_impact(data):
    missing = REQUIRED_IMPACT - set(data)
    incomplete = [
        k
        for k in REQUIRED_IMPACT
        if data.get(k) is None or str(data.get(k, "")).strip() in {"", "REPLACE"}
    ]
    if missing or incomplete:
        raise ValueError(
            f"Incomplete impact assessment: {sorted(missing | set(incomplete))}"
        )
    return True


def score_risks(df):
    if REQUIRED_RISK - set(df.columns):
        raise ValueError("Risk register columns missing")
    if df.id.duplicated().any():
        raise ValueError("Risk ids must be unique")
    if (
        not df.likelihood_1_4.between(1, 4).all()
        or not df.impact_1_4.between(1, 4).all()
    ):
        raise ValueError("Scores must be 1..4")
    if not df.likelihood_1_4.mod(1).eq(0).all() or not df.impact_1_4.mod(1).eq(0).all():
        raise ValueError("Scores must be integers")
    if not df.residual.isin(["low", "medium", "high"]).all():
        raise ValueError("Residual risk missing")
    text_cols = ["scenario", "affected", "control", "owner", "evidence"]
    text = df[text_cols].fillna("").apply(lambda s: s.astype(str).str.strip())
    if (text.eq("REPLACE") | text.eq("")).any().any():
        raise ValueError("Complete all risk fields")
    out = df.copy()
    out["priority"] = out.likelihood_1_4.astype(int) * out.impact_1_4.astype(int)
    return out.sort_values(["priority", "impact_1_4"], ascending=False)
