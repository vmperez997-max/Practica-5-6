# Traspasos entre roles · checklist propuesto

Los roles son simulados; esta tabla define entregables y criterios, no certifica que personas reales hayan aceptado responsabilidades.

| Origen → destino | Paquete de evidencia | Criterio de aceptación | Si falla |
|---|---|---|---|
| Data Engineer → Data Scientist | CSV, hash, contrato y partición | Sin identificadores; categorías válidas; fechas sin solapamiento | STOP, corregir origen |
| Data Scientist → Validation Lead | Modelos, umbral elegido en validación y alternativas | Mismos cortes; métricas globales y desagregadas; costo | REVIEW; repetir evaluación |
| Validation Lead → Institutional Owner | Incertidumbre, soporte y decisión | Ninguna puerta desconocida oculta; documentar trade-offs | REVIEW; no aprobar |
| Institutional Owner → Operations Lead | Alcance, política y apelación | Autorización humana explícita y capacidad real evaluada | No operar; laboratorio no posee autorización |
| ML Engineer → Operations Lead | App, versión, rollback y runbook | Arranca sin entrenar; rollback impide score | MANUAL_ONLY |
| Operations Lead → Privacy Officer / Owner | Incidente y preservación con hold | Evidencia íntegra; comunicación aprobada; no datos extra | Mantener contención |

Un A y al menos un R por actividad se validan por software; `;` separa responsables. La persona/rol Accountable es única. El traspaso operativo no se ha realizado: la decisión de entrega limita el sistema a simulación.
