# Runbook · DSS u04-v1

Alcance: laboratorio sintético. No hay servicio de emergencia, automatización de intervención ni comunicaciones a afectados reales. Responsable final: Institutional Owner (rol simulado), con RACI en `student_inputs/raci.csv`.

| Señal | Estado y acción | Responsable | Evidencia |
|---|---|---|---|
| Identificador directo, esquema inválido o artefacto desactualizado | STOP; no transformar ni puntuar; preservar motivo sin copiar datos personales | Data Engineer / Privacy Officer | Rechazo del contrato, hash y control_tests.json |
| Recall <.68 o brecha soportada >.16 | REVIEW; mantener cola humana; revisar labels, proxies y umbral en validación | Data Scientist / Validation Lead | comparison.csv y tablas de grupos |
| Soporte interseccional insuficiente o denominador cero | REVIEW por incertidumbre; no reemplazar por brecha cero | Validation Lead | Conteos, clase positiva/negativa y supported |
| Latencia batch normalizada >500ms, tamaño >1024KiB, fit >30s | REVIEW; revisar causa y comparar opción suficiente | ML Engineer | Métricas de costo y versión |
| Diferencia absoluta de media exposure >.1 | Investigar deriva; confirmar otras variables y esperar labels si faltan | Data Engineer / Data Scientist | monitoring.json; umbral propuesto |
| Uso real, emergencia o elegibilidad | STOP / retiro de alcance; informar al responsable por canal aprobado | Institutional Owner | Registro de uso fuera de alcance |

Los umbrales son política didáctica, no mandatos legales. Una puerta verde no autoriza operación real; una puerta desconocida no debe convertirse en verde. No reactivar por cambiar límites después de ver prueba.

## Secuencia de incidente

1. **Detectar:** registrar si la señal es observada o inyectada, ventana, denominadores y reloj UTC. No atribuir una causa sin investigación.
2. **Contener:** pasar a REVIEW/STOP según señal y congelar automatización de score; conservar revisión humana de todos los casos.
3. **Preservar:** hashes de dataset, configuración, modelo y decisión; acceso mínimo. Un hold impide la revisión automática de eliminación hasta resolverlo.
4. **Comunicar:** Institutional Owner revisa borrador, destinatarios y mecanismo de apelación; el laboratorio no envía correos ni mensajes reales.
5. **Rollback:** escribir `MANUAL_ONLY`, mantener cola completa y comprobar que no se carga joblib ni se devuelve probabilidad. No volver a un predictor que falle las mismas puertas.
6. **Postmortem:** separar causa supuesta de comprobada; asignar acciones, responsable y fecha propuesta. Validation Lead repite contrato, soporte, equidad y pruebas.
7. **Reactivación:** requiere autorización humana documentada y nueva evidencia independiente; no está implementada como botón ni se ejecuta en esta entrega. El estado MANUAL_ONLY se conserva al repetir pipelines para evitar reactivación silenciosa.

El simulacro ejecutable es `scripts/simulate_incident.py`, con evidencias en `incident_log.json`, `rollback_state.json`, `recommendations_after_rollback.json` y `INCIDENT_POSTMORTEM.md`. Sus timestamps registran ejecución del software; no representan tiempos de respuesta de personas o instituciones.

## Retención, apelación y traspaso

Inventario en `student_inputs/data_inventory.csv`. Propuestas: entradas 30 días, auditoría 90 e incidente 180, sujetas a finalidad y revisión jurídica antes de datos reales; no son plazos de la Ley 172-13. El fixture público sintético y evidencia académica se conservan para reproducibilidad. `retention_plan` produce un dry-run, respeta hold y no borra archivos.

Apelación: revisión de segundo operador y responsable final, con registro de case_id ficticio, evidencia, motivo y corrección. El canal es una propuesta de proceso, no un servicio público ya implantado. Traspasos y criterios de aceptación en `docs/HANDOFF.md`; no se inventan firmas ni aceptaciones reales.
