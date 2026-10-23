# Dataset Card / Datasheet · Caso territorial sintético

**Procedencia:** CSV incluido en la carpeta local `INF8239_U04_Gobernanza_DSS_Proyecto_Base_uv`, material docente de Edwin Ramón José Nolasco, INF-8239, UASD. Se conservó una copia de trabajo acumulativa en `unidad04/`. No se obtuvo por scraping ni contiene observaciones de personas o estadísticas oficiales. La base lo describe como generado con semilla educativa, pero no incluye generador ni valor de esa semilla: no se inventa. La reproducibilidad disponible se basa en el fixture versionado y su hash.

**Archivo:** `data/territorial_risk_synthetic.csv`, 640 registros y 9 columnas. SHA-256: `2af1858fe874f3914b0f9bfe068fd876cb716186694a6ece9a16e8c929128a01`. Se preservan sus bytes CRLF mediante `.gitattributes`; el hash coincide entre plataformas. El archivo original no fue corregido para mejorar resultados.

| Columna | Significado sintético | Uso |
|---|---|---|
| case_id | Identificador ficticio único CASE-xxxx | Trazabilidad; excluido del predictor |
| received_date | Fecha artificial de recepción | Partición temporal; excluida |
| zone | Categoría Norte/Sur/Este/Oeste, sin referente territorial real | Predictor categórico; proxy potencial |
| protected_group | G1/G2 ficticios, sin identidad demográfica real | Auditoría únicamente |
| age_band | 18-29, 30-44, 45-59, 60+, ficticios | Auditoría interseccional únicamente |
| previous_incidents | Conteo artificial no negativo | Predictor numérico |
| infrastructure_score | Índice artificial [0,1] | Predictor numérico |
| exposure | Intensidad artificial [0,1] | Predictor numérico |
| target | Etiqueta didáctica 0/1 de necesidad de revisión | Objetivo; no mide daño real |

Distribución: 353 positivos y 287 negativos; G1=396 y G2=244. No es prevalencia de necesidad real. Las fechas abarcan 2026-01-01 a 2026-12-27; algunas son posteriores a la fecha de esta entrega. **Son fechas inventadas, no eventos observados ni datos disponibles del futuro.** No hay población de referencia ni evidencia de representatividad de República Dominicana.

Contrato: columnas obligatorias y allowlist sin campos extra; rechazo de name, document_number, email y phone, id no ficticio, duplicados, nulos, fechas inválidas, categorías desconocidas, conteos no enteros/negativos y números fuera de rango. Quitar identificadores o atributos sensibles no garantiza anonimato ni elimina proxies. En este fixture la ausencia de personas reales procede de su carácter sintético declarado; no de una técnica de anonimización.

## Partición y exclusiones

Orden por fecha y case_id, manteniendo días empatados juntos. 384 fit (hasta 2026-08-03), 96 validación (2026-08-04 a 2026-09-24), 160 prueba (desde 2026-09-25). `reports/lab12/data_audit.json` conserva cortes y hash. Se ajustan modelo y umbral en validación; la prueba compara resultados tras congelar la elección. Ninguna transformación se aprende sobre validación o prueba. Los dos sensibles, id, fecha y target no son predictores. La base usaba age_band y se corrigió esa contradicción.

## Soporte, incertidumbre y acceso

Soporte propuesto: n>=30 y al menos 10 positivos y 10 negativos. Se publican todos los grupos y denominadores, aun los insuficientes, con `supported=False`. Solo 1/8 intersecciones tiene soporte en prueba; las brechas interseccionales no se estiman como cero. Wilson 95% para proporciones, sin corrección por comparación múltiple ni correlación temporal. No permiten concluir discriminación causal ni justicia del sistema.

El fixture sintético y agregados se publican como evidencia académica del material suministrado; la base no aporta una licencia explícita para otros usos. No se atribuye licencia abierta inexistente ni autorización comercial. No hay secretos ni datos personales de titulares reales; el nombre/matrícula de autor se usan como identificación académica solicitada para el informe. No se redistribuye MovieLens.

Retención y acceso futuros se proponen en `student_inputs/data_inventory.csv`; no son plazos legales ni controles de producción ya implantados. La copia sintética versionada es evidencia reproducible permanente. Cualquier sustitución por datos reales requiere nueva evaluación de propósito, origen, base jurídica, acceso, participación y retención.
