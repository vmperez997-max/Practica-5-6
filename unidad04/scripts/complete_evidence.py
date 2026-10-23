"""Finalize editable evidence from frozen audit outputs, without retraining."""

import json
import platform
from pathlib import Path

import fairlearn
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import sklearn

from inf8239_u04.pipeline import sha
from inf8239_u04.privacy import retention_plan

root = Path(__file__).resolve().parents[1]
table = pd.read_csv(root / "reports/lab12/comparison.csv")
selected = table[table.label.str.endswith("_selected")].iloc[0]
regular = table[table.label.eq("logistic_t0.5")].iloc[0]
risks = pd.read_csv(root / "reports/lab11/risk_register_scored.csv")
record = f"""# Registro de decisión · LAB11–12

Decisión: **LIMITAR a evaluación sintética; REVIEW para despliegue.** No hay autorización para operar sobre personas o territorios reales. El estudiante eligió explícitamente priorizar no omitir zonas que necesitan revisión humana. La alternativa no predictiva es revisar todos los casos por orden de recepción y lista de comprobación, sin descartar por score.

Tres riesgos prioritarios: R01 (omisiones), R02 (incertidumbre interseccional), prioridad ordinal 12 cada uno; R06 (sobrecarga por falsos positivos), 9. Son juicios cualitativos propuestos, no probabilidades empíricas de daño ni valores confirmados por una institución. R01 y R02 requieren Data Scientist y Validation Lead; R06, Operations Lead, bajo un Accountable institucional simulado. Riesgo residual alto impide dar por resuelto el problema.

Evidencia: logística .3 elegida solo en validación obtiene recall {selected.recall:.4f} frente a {regular.recall:.4f} a .5, pero FPR {selected.fpr:.4f} frente a {regular.fpr:.4f}. Se reducen falsos negativos de 25 a 6, a costa de subir falsos positivos de 19 a 36; el volumen de revisión pasa de 86 a 122 de 160. No se evaluó capacidad operativa real. Dummy tiene recall 1 y FPR 1; no es una solución justa por tener brecha cero.

Incertidumbre: solo {int(selected.supported_intersections)}/{int(selected.total_intersections)} intersecciones satisface soporte propuesto30/10. Brechas interseccionales no estimables no se sustituyen por cero ni prueban discriminación causal. Wilson 95% no corrige dependencia temporal ni múltiples comparaciones. Dataset sintético, sin población real ni aprobación jurídica. Las brechas G1/G2 son descriptivas, no inferencia sobre RD.

Control y condición de retiro: STOP ante identificadores/contrato inválido o uso fuera de alcance; REVIEW ante incumplimiento o evidencia insuficiente; rollback a cola humana completa. El simulacro deja MANUAL_ONLY. Antes de considerar un nuevo uso: revisar propósito y base jurídica si hay datos personales, participación efectiva de afectados, capacidad de revisión, soporte, labels y nueva prueba independiente. Un resultado técnico GO no autoriza despliegue.

Estado de responsabilidad: el estudiante debe revisar el expediente y los supuestos propuestos; no se inventan firmas, aprobación institucional ni ejecución de participación real. RACI, runbook y evidencia de pruebas permiten revisar quién debe actuar, sin afirmar aceptación de roles reales.
"""
(root / "reports/lab11/DECISION_RECORD.md").write_text(record, encoding="utf-8")
model_dir = root / "models"
(model_dir / "manifest.json").write_text(
    json.dumps(
        {
            p.name: {"sha256": sha(p), "bytes": p.stat().st_size}
            for p in model_dir.glob("*.joblib")
        },
        indent=2,
    ),
    encoding="utf-8",
)
provenance = {
    "python": platform.python_version(),
    "sklearn": sklearn.__version__,
    "fairlearn": fairlearn.__version__,
    "model_seed": 42,
    "data_generation_seed": "not provided by teaching base",
    "source_hashes": {
        str(p.relative_to(root)): sha(p) for p in (root / "src").rglob("*.py")
    },
    "data_sha256": sha(root / "data/territorial_risk_synthetic.csv"),
    "policy_sha256": sha(root / "configs/governance.yml"),
    "limitation": "Source hashes identify executed implementation; tests and PDF provide separate evidence. Dataset dates are synthetic.",
}
(root / "reports/lab13/provenance.json").write_text(
    json.dumps(provenance, indent=2), encoding="utf-8"
)
plan = retention_plan(
    [
        {"id": "old_fixture_log", "created_at": "2026-01-01"},
        {"id": "held_evidence", "created_at": "2026-01-01", "hold": True},
        {"id": "recent_fixture_log", "created_at": "2026-10-20"},
    ],
    "2026-10-23",
    30,
)
(root / "reports/lab13/retention_dry_run.json").write_text(
    json.dumps(plan, indent=2), encoding="utf-8"
)
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
labels = ["Dummy", "Logística .5", "Árbol .5", "Logística .3"]
for ax, metric, title in [(axes[0], "recall", "Recall / TPR"), (axes[1], "fpr", "FPR")]:
    ax.bar(labels, table[metric], color=["#999999", "#337ab7", "#6a9e73", "#163a60"])
    ax.set(title=title, ylim=(0, 1.1))
    ax.tick_params(axis="x", rotation=20)
    for i, value in enumerate(table[metric]):
        ax.text(i, value + 0.025, f"{value:.3f}", ha="center", fontsize=9)
fig.suptitle("Prueba sintética: utilidad y carga; no evidencia poblacional")
fig.tight_layout()
fig.savefig(root / "reports/lab12/tradeoffs.png", dpi=160)
plt.close(fig)
groups = pd.read_csv(root / "reports/lab12/fairness_by_group.csv", index_col=0)
fig, ax = plt.subplots(figsize=(7, 3))
for offset, metric in [(-0.1, "recall"), (0.1, "fpr")]:
    x = list(range(len(groups)))
    values = groups[metric].to_numpy()
    ax.errorbar(
        [i + offset for i in x],
        values,
        yerr=[
            values - groups[metric + "_ci_low"],
            groups[metric + "_ci_high"] - values,
        ],
        fmt="o",
        capsize=4,
        label=metric,
    )
ax.set(
    xticks=list(range(len(groups))),
    xticklabels=[f"{g} (n={int(r['count'])})" for g, r in groups.iterrows()],
    ylim=(0, 1.05),
    ylabel="Tasa; Wilson 95%",
    title="Grupos principales · logística .3",
)
ax.legend()
fig.tight_layout()
fig.savefig(root / "reports/lab12/group_intervals.png", dpi=160)
plt.close(fig)
print("Decision record, provenance, retention dry run and figures complete.")
