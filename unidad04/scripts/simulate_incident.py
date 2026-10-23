"""Executable tabletop drill: injected alarm, real policy evaluation, no external communication."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from inf8239_u04.data import load_data
from inf8239_u04.governance import deployment_decision, load_config
from inf8239_u04.pipeline import recommend, sha

root = Path(__file__).resolve().parents[1]
out = root / "reports/lab13"
observed = json.loads((out / "deployment_decision.json").read_text(encoding="utf-8"))
cfg = load_config()
now = datetime.now(UTC)
injected = {"recall_gap": 0.40, "fpr_gap": 0.10}
decision = deployment_decision(
    {"recall": 0.8},
    injected,
    {"latency_ms": 1, "model_kb": 4, "training_seconds": 0.01},
    cfg["gates"],
    support_ok=True,
)
assert decision["status"] == "REVIEW" and "recall_gap" in decision["failed"]
events = [
    (
        "detección",
        "ML Engineer",
        "Inyectar brecha .40: alarma simulada, no medición real",
    ),
    (
        "contención",
        "Operations Lead",
        "Bloquear recomendación de despliegue; cola humana completa, sin exclusión por score",
    ),
    (
        "preservación",
        "Validation Lead",
        "Calcular hashes de política, datos y evidencias antes de intervenir",
    ),
    (
        "comunicación",
        "Institutional Owner",
        "Redactar mensaje simulado; no se envían correos ni avisos externos",
    ),
    (
        "rollback",
        "ML Engineer",
        "Cambiar estado de simulación a MANUAL_ONLY; todos los casos conservan revisión",
    ),
    (
        "postmortem",
        "Institutional Owner",
        "Diagnosticar soporte, proxies y labels; revalidar antes de reactivar",
    ),
]
log = [
    {
        "sequence": i,
        "event": event,
        "role": role,
        "action": action,
        "executed_at_utc": datetime.now(UTC).isoformat(),
    }
    for i, (event, role, action) in enumerate(events, 1)
]
evidence = {
    str(p.relative_to(root)): sha(p)
    for p in [
        root / "configs/governance.yml",
        root / "data/territorial_risk_synthetic.csv",
        out / "deployment_decision.json",
    ]
}
record = {
    "incident_id": "SIM-U04-001",
    "simulation": True,
    "injected_metrics": injected,
    "decision": decision,
    "previous_status": observed["decision"]["status"],
    "events": log,
    "preserved_evidence_sha256": evidence,
    "rollback_state": "MANUAL_ONLY",
    "real_communication_sent": False,
    "communication_draft": "SIMULACRO: revisión requerida por brecha inyectada; mantener cola humana y no tomar decisiones automáticas.",
    "action_due_proposed": (now + timedelta(days=7)).date().isoformat(),
    "closure": "Tabletop mechanics verified; organizational actions are simulated, not real approvals.",
}
(out / "incident_log.json").write_text(
    json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
)
(out / "rollback_state.json").write_text(
    json.dumps(
        {"mode": "MANUAL_ONLY", "case_exclusion_allowed": False, "simulation": True},
        indent=2,
    ),
    encoding="utf-8",
)
after = recommend(load_data().tail(5))
assert all(
    row["probability"] is None and row["priority"] == "cola_manual_completa"
    for row in after
)
(out / "recommendations_after_rollback.json").write_text(
    json.dumps(after, indent=2, ensure_ascii=False), encoding="utf-8"
)
text = "# Simulacro y postmortem SIM-U04-001\n\nAlarma inyectada .40: no se confunde con métricas observadas. Las seis etapas se registran en incident_log.json.\n\n"
text += "\n".join(f"- {event}: {role}. {action}." for event, role, action in events)
text += (
    "\n\nCausa simulada: cambio de distribución o error de datos; no se atribuye causa real. La prueba valida REVIEW. Rollback a cola manual completa, sin reutilizar predictor inseguro. La verificación interseccional ya exigía REVIEW antes del simulacro.\n\nAcciones propuestas: Data Engineer revisa contrato y fecha; Data Scientist investiga proxies/etiquetas; Validation Lead obtiene soporte y revalida; Institutional Owner debe aceptar evidencia antes de reactivar. Plazo de revisión propuesto: "
    + record["action_due_proposed"]
    + ". No se realizó comunicación externa ni aprobación institucional.\n"
)
(out / "INCIDENT_POSTMORTEM.md").write_text(text, encoding="utf-8")
print("Incident simulation: REVIEW -> MANUAL_ONLY; no external messages.")
