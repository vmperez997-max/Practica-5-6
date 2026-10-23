# Registro de decisión · LAB11–12

Decisión: **LIMITAR a evaluación sintética; REVIEW para despliegue.** No hay autorización para operar sobre personas o territorios reales. El estudiante eligió explícitamente priorizar no omitir zonas que necesitan revisión humana. La alternativa no predictiva es revisar todos los casos por orden de recepción y lista de comprobación, sin descartar por score.

Tres riesgos prioritarios: R01 (omisiones), R02 (incertidumbre interseccional), prioridad ordinal 12 cada uno; R06 (sobrecarga por falsos positivos), 9. Son juicios cualitativos propuestos, no probabilidades empíricas de daño ni valores confirmados por una institución. R01 y R02 requieren Data Scientist y Validation Lead; R06, Operations Lead, bajo un Accountable institucional simulado. Riesgo residual alto impide dar por resuelto el problema.

Evidencia: logística .3 elegida solo en validación obtiene recall 0.9348 frente a 0.7283 a .5, pero FPR 0.5294 frente a 0.2794. Se reducen falsos negativos de 25 a 6, a costa de subir falsos positivos de 19 a 36; el volumen de revisión pasa de 86 a 122 de 160. No se evaluó capacidad operativa real. Dummy tiene recall 1 y FPR 1; no es una solución justa por tener brecha cero.

Incertidumbre: solo 1/8 intersecciones satisface soporte propuesto30/10. Brechas interseccionales no estimables no se sustituyen por cero ni prueban discriminación causal. Wilson 95% no corrige dependencia temporal ni múltiples comparaciones. Dataset sintético, sin población real ni aprobación jurídica. Las brechas G1/G2 son descriptivas, no inferencia sobre RD.

Control y condición de retiro: STOP ante identificadores/contrato inválido o uso fuera de alcance; REVIEW ante incumplimiento o evidencia insuficiente; rollback a cola humana completa. El simulacro deja MANUAL_ONLY. Antes de considerar un nuevo uso: revisar propósito y base jurídica si hay datos personales, participación efectiva de afectados, capacidad de revisión, soporte, labels y nueva prueba independiente. Un resultado técnico GO no autoriza despliegue.

Estado de responsabilidad: el estudiante debe revisar el expediente y los supuestos propuestos; no se inventan firmas, aprobación institucional ni ejecución de participación real. RACI, runbook y evidencia de pruebas permiten revisar quién debe actuar, sin afirmar aceptación de roles reales.
