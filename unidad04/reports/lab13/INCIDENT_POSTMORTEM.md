# Simulacro y postmortem SIM-U04-001

Alarma inyectada .40: no se confunde con métricas observadas. Las seis etapas se registran en incident_log.json.

- detección: ML Engineer. Inyectar brecha .40: alarma simulada, no medición real.
- contención: Operations Lead. Bloquear recomendación de despliegue; cola humana completa, sin exclusión por score.
- preservación: Validation Lead. Calcular hashes de política, datos y evidencias antes de intervenir.
- comunicación: Institutional Owner. Redactar mensaje simulado; no se envían correos ni avisos externos.
- rollback: ML Engineer. Cambiar estado de simulación a MANUAL_ONLY; todos los casos conservan revisión.
- postmortem: Institutional Owner. Diagnosticar soporte, proxies y labels; revalidar antes de reactivar.

Causa simulada: cambio de distribución o error de datos; no se atribuye causa real. La prueba valida REVIEW. Rollback a cola manual completa, sin reutilizar predictor inseguro. La verificación interseccional ya exigía REVIEW antes del simulacro.

Acciones propuestas: Data Engineer revisa contrato y fecha; Data Scientist investiga proxies/etiquetas; Validation Lead obtiene soporte y revalida; Institutional Owner debe aceptar evidencia antes de reactivar. Plazo de revisión propuesto: 2026-10-30. No se realizó comunicación externa ni aprobación institucional.
