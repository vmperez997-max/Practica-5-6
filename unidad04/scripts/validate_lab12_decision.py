from pathlib import Path

import yaml

d = yaml.safe_load(
    Path("student_inputs/lab12_decision.yml").read_text(encoding="utf-8")
)
required = {
    "priority_harm",
    "primary_metric",
    "tolerance",
    "evidence",
    "limitation",
    "recommendation",
}
if required - set(d):
    raise ValueError("Decision fields missing")
missing = [k for k, v in d.items() if str(v).strip() in {"", "REPLACE"}]
if missing:
    raise ValueError(f"Complete: {missing}")
print("decision_status: documented")
