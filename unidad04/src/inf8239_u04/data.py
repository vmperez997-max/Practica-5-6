from pathlib import Path

import pandas as pd

REQUIRED = {
    "case_id",
    "received_date",
    "zone",
    "protected_group",
    "age_band",
    "previous_incidents",
    "infrastructure_score",
    "exposure",
    "target",
}
PROHIBITED = {"name", "document_number", "email", "phone"}
FEATURES = ["zone", "previous_incidents", "infrastructure_score", "exposure"]


def load_data(path=None):
    if path is None:
        path = (
            Path(__file__).resolve().parents[2] / "data/territorial_risk_synthetic.csv"
        )
    df = pd.read_csv(Path(path), parse_dates=["received_date"])
    validate_schema(df)
    return df.sort_values("received_date").reset_index(drop=True)


def validate_schema(df):
    missing = REQUIRED - set(df.columns)
    forbidden = PROHIBITED & {str(c).lower() for c in df.columns}
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if forbidden:
        raise ValueError(f"Direct identifiers prohibited: {sorted(forbidden)}")
    if set(df.columns) - REQUIRED:
        raise ValueError("Unexpected columns: minimization allowlist")
    if df.empty or df.isna().any().any():
        raise ValueError("Empty or missing values")
    if not df.case_id.is_unique:
        raise ValueError("Duplicate case_id")
    if not df.case_id.astype(str).str.fullmatch(r"CASE-\d{4}").all():
        raise ValueError("Expected synthetic case_id format")
    if pd.to_datetime(df.received_date, errors="coerce", format="ISO8601").isna().any():
        raise ValueError("Invalid received_date")
    for col in ["infrastructure_score", "exposure"]:
        if not pd.to_numeric(df[col], errors="coerce").between(0, 1).all():
            raise ValueError("Invalid numeric range")
    incidents = pd.to_numeric(df.previous_incidents, errors="coerce")
    if not (incidents.ge(0) & incidents.mod(1).eq(0)).all():
        raise ValueError("Invalid incidents")
    if not df.protected_group.isin(["G1", "G2"]).all():
        raise ValueError("Unknown protected group")
    if (
        not df.age_band.isin(["18-29", "30-44", "45-59", "60+"]).all()
        or not df.zone.isin(["Norte", "Sur", "Este", "Oeste"]).all()
    ):
        raise ValueError("Unknown synthetic category")
    if not set(df.target.unique()).issubset({0, 1}):
        raise ValueError("target must be binary")


def temporal_split(df, test_fraction=0.25):
    if not 0 < test_fraction < 1:
        raise ValueError("Invalid test_fraction")
    df = df.sort_values(["received_date", "case_id"], kind="stable")
    cut = int(len(df) * (1 - test_fraction))
    boundary = df.iloc[cut].received_date
    train, test = df[df.received_date < boundary], df[df.received_date >= boundary]
    if train.empty or test.empty:
        raise ValueError("Insufficient distinct dates")
    return train.copy(), test.copy()


def features(df):
    validate_schema(df)
    return df[FEATURES]
