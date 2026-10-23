# Model Card · DSS territorial sintético · u04-v1

**Autor:** Victor Manuel Perez Padilla, matrícula 100801946. Guía docente: Edwin Ramón José Nolasco. Finalidad: apoyar estudio de priorización de revisión humana. El usuario confirmó como daño prioritario «No omitir zonas que necesitan revisión humana». No se declara emergencia, elegibilidad, culpabilidad ni intervención automática.

## Autoridad y alternativa

Usuarios y responsables son roles simulados. Toda recomendación exige revisión humana y derecho a anular. Alternativa no predictiva: revisar todos los casos por orden de recepción con una lista de comprobación, sin descartar por score. Tras el simulacro, la app queda en `MANUAL_ONLY`, no carga el predictor ni devuelve probabilidad actual. El score histórico se conserva como evidencia, no como orden operativa. No existe aprobación institucional real ni despliegue operativo.

## Modelos y validación

Dummy mayoritario, regresión logística (balanced, max_iter=1200, seed42) y árbol (profundidad 5, balanced, seed42). Preprocesamiento aprendido solo en fit: OneHot zona y StandardScaler de tres variables numéricas. Atributos sensibles `protected_group` y `age_band` excluidos; zona puede actuar como proxy. `target` es una etiqueta artificial, no evaluación humana de necesidad real.

384 fit / 96 validación / 160 prueba con fechas estrictamente separadas, sin romper empates. Para modelos no dummy se comparan umbrales .3,.4,.5,.6,.7 en validación; entre candidatos que cumplen recall y brechas de grupos principales se prioriza recall, después FPR, tiempo y tamaño. Si ninguno cumple, se conserva una alternativa para análisis, sin autorización. La elección no usa prueba, pero los futuros ajustes tras verla requerirán otra prueba final. No se hace selección por umbral de grupos ni se utiliza el atributo sensible al inferir.

## Resultados de prueba

| Alternativa | Accuracy | Recall | FPR | Selección | Brecha recall G1/G2 | Brecha FPR G1/G2 |
|---|---:|---:|---:|---:|---:|---:|
| Dummy .5 | .5750 | 1.0000 | 1.0000 | 1.0000 | .0000 | .0000 |
| Logística .5 | .7250 | .7283 | .2794 | .5375 | .1172 | .1250 |
| Árbol .5 | .7063 | .7609 | .3676 | .5938 | .0123 | .2548 |
| Logística .3 elegida en validación | .7375 | .9348 | .5294 | .7625 | .0085 | .0433 |

Fuente ejecutada: `reports/lab12/comparison.csv`. Dummy predice todos positivos porque esa es la clase mayoritaria de fit; no debe confundirse con el procedimiento humano completo, que este clasificador no simula. Demuestra por qué recall alto y brecha cero no bastan: todos los negativos reciben alerta. La mitigación de umbral reduce omisiones a costa de carga humana. De 92 positivos test, logística .5 omite 25 y .3 omite 6; falsos positivos suben de 19 a 36 entre 68 negativos.

G1 tiene 101 casos (49 positivos, 52 negativos), G2 59 (43/16). Con .3, recall G1=.9388 y G2=.9302; FPR .5192 y .5625. La diferencia de tasas no identifica causas ni equivale a discriminación legal. No se afirma justicia porque una métrica quede cerca.

Intersecciones: 1/8 cumple soporte n>=30, positivos>=10 y negativos>=10. Las otras se muestran y no se interpretan como conclusiones robustas. Brechas interseccionales admiten `null`/NaN, nunca cero imputado. Wilson 95% ignora dependencia temporal y no es inferencia causal ni ajuste por múltiples comparaciones. No se han validado estabilidad en varias semillas, calibración, capacidad real de atención o efectos de intervenciones.

## Costo y Green AI

Tiempos, KiB joblib y latencia media por registro están en comparison.csv. Son mediciones locales con ruido, sin energía ni CO2. Latencia divide tiempo de todo el batch por 160; no es percentil de latencia de una petición individual. El árbol es mayor y no mejora suficientemente la combinación de utilidad/brechas para justificarlo aquí. La alternativa logística es una elección de validación, no un permiso de despliegue.

No se cambia un umbral solo para poner puertas en verde. Recall>=.68, brechas<=.16, latencia<=500ms y tamaño<=1024KiB proceden de la base docente; entrenamiento<=30s y soporte30/10 son propuestas académicas. No son derechos, estándares legales ni tolerancias aprobadas por afectados reales.

## Gobernanza y límites

`deployment_decision.json` queda **REVIEW**: soporte incompleto y brechas interseccionales no estimables, no una brecha excesiva medida. Privacidad rechaza identificadores antes de predecir; la política y los hashes de datos/modelo se verifican para no usar evidencia obsoleta. Configuración o artefactos inválidos bloquean, no autorizan. RACI garantiza un A y al menos un R por actividad; asignación no equivale a aceptación institucional real.

Simulacro SIM-U04-001: brecha .40 inyectada, evaluación real de puerta, bloqueo y rollback a cola manual completa. Se prueban probabilidad nula y no carga del modelo tras rollback. Ningún mensaje externo se envió. Las métricas observadas y la alarma ficticia permanecen separadas. Monitoreo retrospectivo de media exposure: diferencia .01473 frente a umbral propuesto .1, sin alerta marginal; no demuestra ausencia de deriva en otras variables, modelo o grupos. Recall requiere etiquetas, que podrían llegar con demora en una operación real.

Uso permitido: enseñanza y revisión del expediente. **No uso operativo** con estos datos y validación. No extrapolar métricas a República Dominicana ni sustituir criterio humano. Los joblib son artefactos propios confiables; no se deben cargar archivos de terceros sin confianza, porque pickle puede ejecutar código.
