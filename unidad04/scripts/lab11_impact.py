import json
from pathlib import Path

import pandas as pd
import yaml

from inf8239_u04.impact import score_risks, validate_impact

root = Path(__file__).resolve().parents[1]
out = root / "reports/lab11"
out.mkdir(parents=True, exist_ok=True)
impact = yaml.safe_load(
    (root / "student_inputs/lab11_impact.yml").read_text(encoding="utf-8")
)
validate_impact(impact)
stake = pd.read_csv(root / "student_inputs/stakeholders.csv")
if (
    stake.isna().any().any()
    or stake.astype(str).apply(lambda s: s.str.contains("REPLACE")).any().any()
):
    raise ValueError("Complete stakeholders")
risks = score_risks(pd.read_csv(root / "student_inputs/risk_register.csv"))
if len(risks) < 8:
    raise ValueError("At least eight risks required")
risks.to_csv(out / "risk_register_scored.csv", index=False)
stake.to_csv(out / "stakeholders.csv", index=False)
summary = {
    "GOVERN": {
        "evidence": ["student_inputs/raci.csv", "configs/governance.yml"],
        "status": "roles y alcance documentados; no aprobación de uso real",
    },
    "MAP": {
        "evidence": [
            "student_inputs/lab11_impact.yml",
            "student_inputs/risk_register.csv",
        ],
        "status": f"{len(risks)} escenarios; puntuaciones ordinales propuestas, no probabilidades observadas",
    },
    "MEASURE": {
        "evidence": ["reports/lab12/comparison.csv", "reports/tests.txt"],
        "status": "verificar resultados ejecutados; archivo existente no equivale a control eficaz",
    },
    "MANAGE": {
        "evidence": [
            "reports/lab13/deployment_decision.json",
            "reports/lab13/INCIDENT_POSTMORTEM.md",
        ],
        "status": "bloqueo y simulacro verificables; controles organizativos propuestos",
    },
}
(out / "rmf_summary.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
)
# Preserve the authored decision record on reruns.
record = out / "DECISION_RECORD.md"
if not record.exists():
    record.write_text(
        "# Registro de decisión\n\nREVIEW: continuar solo evaluación sintética. No se autoriza uso real. Prioridad de daño elegida por el estudiante: evitar omisiones.\n",
        encoding="utf-8",
    )
print(risks[["id", "priority", "owner"]].head(3).to_string(index=False))
