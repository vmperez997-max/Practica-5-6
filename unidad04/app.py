import json
from pathlib import Path

import pandas as pd
import streamlit as st

from inf8239_u04.data import load_data
from inf8239_u04.pipeline import recommend

root = Path(__file__).resolve().parent
st.set_page_config(page_title="DSS gobernado · U04", layout="wide")
st.title("DSS territorial sintético · Gobernanza y Green AI")
st.warning(
    "Caso sintético educativo: no representa personas, territorios ni estadísticas reales de República Dominicana. Prohibidas decisiones o intervenciones automáticas."
)
path = root / "reports/lab13/deployment_decision.json"
if not path.exists():
    st.error(
        "Ejecute los laboratorios antes de iniciar la app. No se entrena durante la visita."
    )
    st.stop()
payload = json.loads(path.read_text(encoding="utf-8"))
st.subheader("Propósito y autoridad")
st.write(
    "Priorizar evidencia para revisión humana; ningún score elimina un caso de la cola. Responsable: Institutional Owner, rol simulado."
)
st.write(
    "Prioridad del estudiante: no omitir zonas que necesitan revisión humana. Apelación: segundo operador y responsable institucional."
)
comparison = pd.read_csv(root / "reports/lab12/comparison.csv")
st.subheader("Alternativas y costo")
st.dataframe(comparison, hide_index=True)
st.subheader("Grupos e intersecciones")
st.dataframe(pd.read_csv(root / "reports/lab12/fairness_by_group.csv"))
st.dataframe(pd.read_csv(root / "reports/lab12/fairness_intersectional.csv"))
st.caption(
    "Soporte mínimo propuesto: n>=30, positivos>=10 y negativos>=10. Intervalos Wilson 95%, no ajuste por comparaciones ni dependencia temporal. No interpretar grupos sin soporte como evidencia robusta."
)
st.subheader("Puertas y recomendación")
st.json(payload)
st.metric("Estado técnico", payload["decision"]["status"])
st.info(
    "Acción humana: revisar evidencia, documentar decisión y no desplegar con puertas fallidas. Un GO solo sería técnico y sintético, nunca permiso operativo."
)
data = load_data()
case = st.selectbox("Caso ficticio para inspección", data.case_id.tolist())
st.json(recommend(data[data.case_id.eq(case)])[0])
with st.expander("Evidencia histórica de prueba, no orden operativa"):
    predictions = pd.read_csv(root / "reports/lab12/selected_predictions.csv")
    st.dataframe(predictions[predictions.case_id.eq(case)])
    st.caption(
        "El simulacro puede desactivar el score actual; esta tabla preserva la inferencia histórica con su umbral."
    )
rollback = root / "reports/lab13/rollback_state.json"
if rollback.exists():
    st.write("Simulacro:", json.loads(rollback.read_text(encoding="utf-8")))
st.caption(
    "Retención y roles: ver inventario, RACI y runbook. Este tablero no recoge datos personales ni registra decisiones humanas reales."
)
