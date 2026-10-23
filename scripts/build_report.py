"""Build a brief, evidence-linked report from executed experiment artifacts."""

import json
from itertools import combinations
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
reports = ROOT / "reports"
summary = pd.read_csv(reports / "pareto.csv")
profiles = pd.read_csv(reports / "profile_recommendations.csv")
content = pd.read_csv(reports / "content_recommendations.csv")
audit = json.loads((reports / "audit.json").read_text())
manifest = json.loads((reports / "download_manifest.json").read_text())
pop = summary.query("method == 'popularity'").iloc[0]
hybrid = summary.query("method == 'hybrid' and factors == 20 and alpha == 0.75").iloc[0]
low = summary.query("method == 'hybrid' and factors == 20 and alpha == 0.25").iloc[0]
cf = summary.query("method == 'collaborative' and factors == 20").iloc[0]
selected = profiles.query("method == 'hybrid' and factors == 20 and alpha == 0.75")
stability = []
for label, table in selected.groupby("profile", sort=False):
    sets = [set(group.movieId) for _, group in table.groupby("seed")]
    stability.append(
        {
            "profile": label,
            "userId": int(table.userId.iloc[0]),
            "history_size": int(table.history_size.iloc[0]),
            "mean_jaccard_seeds": sum(
                len(a & b) / len(a | b) for a, b in combinations(sets, 2)
            )
            / 3,
        }
    )
pd.DataFrame(stability).to_csv(reports / "profile_stability.csv", index=False)

conclusion = f"""# Conclusión interpretativa

## LAB08

Resultado principal: popularidad suavizada proporciona una referencia económica. LAB08 describe el dataset completo; la evaluación comparativa calcula las señales solo con entrenamiento. El suavizado combina media del ítem y media global, con m igual al percentil 80 de los conteos, y solo admite en el ranking de popularidad ítems con conteo >= m. Ítems fuera de ese grupo reciben media global en el motor de ranking completo.

Evidencia utilizada: `popular_top10.csv`, `content_recommendations.csv`, manifiesto y auditoría. Las consultas son Toy Story (Animation/Adventure/Comedy/Fantasy), The Shawshank Redemption (Crime/Drama) y The Exorcist (Horror/Mystery).

Qué representa la similitud: coseno entre vectores TF-IDF de géneros, no probabilidad de agrado. Películas con idénticos géneros tienen vectores iguales y empatan. Con el tokenizador original, Sci-Fi se separa en tokens; no se interpreta como semántica profunda.

Cold start: el método por contenido puede encontrar similares para una película sin ratings si tiene géneros; un usuario sin historial carece de perfil y recibe popularidad compartida.

Sobre-especialización: The Shawshank Redemption puede producir un Top-10 exclusivamente Crime/Drama; la igualdad de metadatos oculta diferencias de trama, época y calidad. Un siguiente experimento debe diversificar géneros y medir exposición, sin asumir que cobertura equivale a diversidad individual.

## LAB09

Resultado de ratings: MF 20/12 obtiene RMSE medio {cf.rmse:.4f}, frente a {pop.rmse:.4f} del predictor de media global. El RMSE del híbrido es el de su componente MF: la mezcla de scores normalizados no predice estrellas. El baseline de RMSE usa media global y no debe confundirse con la política de ranking por popularidad suavizada.

Resultado de ranking: popularidad HR@10 {pop.hit_rate_at_10:.4%}; colaborativo 20/12 {cf.hit_rate_at_10:.4%}; híbrido 20/12, alpha .75 {hybrid.hit_rate_at_10:.4%}. Híbrido alpha .25 obtiene {low.hit_rate_at_10:.4%}. Con alpha .75 domina la señal colaborativa; .25 favorece contenido. Los scores de ambas señales se normalizan min-max sobre los mismos candidatos antes de mezclarse.

Cobertura: popularidad {pop.coverage:.2%}, colaborativo {cf.coverage:.2%}, híbrido .75 {hybrid.coverage:.2%} e híbrido .25 {low.coverage:.2%} del catálogo de {audit["movies"]:,} películas. Cobertura es la unión de todos los Top-10, no una métrica de satisfacción ni de equidad.

Usuario frío: -1 es sintético y recibe la misma lista de popularidad para todas las configuraciones. Los otros perfiles se eligen por máximo y mínimo historial de entrenamiento; el menor historial observado aún tiene 19 interacciones y no representa cold start extremo. La estabilidad entre semillas se registra en `profile_stability.csv`.

Configuración seleccionada: para un despliegue académico con prioridad al costo, popularidad como referencia por defecto. Está en Pareto y logra casi el mismo HR que el híbrido con menor costo. Para estudiar personalización y exposición, se selecciona entre los híbridos 20 factores, 12 épocas y alpha .75: mejora HR respecto de .25 a costa de cobertura. Es una elección exploratoria: no se usó validación independiente y por tanto no se afirma generalización del valor elegido.

Costo: popularidad {pop.total_seconds:.2f} s y {pop.model_bytes / 1e6:.2f} MB; híbrido elegido {hybrid.total_seconds:.2f} s y {hybrid.model_bytes / 1e6:.2f} MB. Es {hybrid.total_seconds / pop.total_seconds:.1f} veces el tiempo para una ganancia media de {(hybrid.hit_rate_at_10 - pop.hit_rate_at_10) * 100:.3f} puntos porcentuales de HR y {(hybrid.coverage - pop.coverage) * 100:.2f} puntos de cobertura. Los tiempos suman entrenamiento MF y ranking de 610 usuarios; excluyen descarga, carga, TF-IDF compartido e I/O. El tamaño mide pickle del estado por método (ids, popularidad, contenido/MF cuando aplica), sin historial ni runtime. No se publican pickles ni datos. No se midieron energía ni CO2.

Pareto: se maximiza HR y cobertura y se minimizan segundos y bytes, usando medias entre semillas. `pareto.csv` marca dominancia estricta en al menos un objetivo y no peor en los demás. Diferencias pequeñas de tiempo no implican mejoras robustas. Se incluyen los deterministas una vez porque repetir semillas no cambia sus salidas.

Riesgo principal y mitigación: concentración popular y burbuja de filtro. Mantener baseline, medir diversidad por usuario, exposición y novedad; probar reranking diversificado y monitorear retroalimentación. No se pueden afirmar resultados por grupos sin demografía.

Limitaciones: una sola película retenida por usuario; todos los ratings cuentan como interacción relevante para HR principal. P@10 es HR/10 por diseño, no una medida independiente. También se informa HR entre los 363 eventos de rating >=4. Hay 23 ítems desconocidos en entrenamiento, sin exclusión del denominador. Hay 94 empates temporales y posible fuga entre usuarios. Próximo experimento: corte global estricto con disponibilidad del catálogo, validación separada, múltiples positivos y prueba final intacta. Las tres semillas no son tres muestras independientes de usuarios ni permiten afirmar significancia estadística.
"""
(ROOT / "docs/CONCLUSION.md").write_text(conclusion, encoding="utf-8")


from report_layout import render_report

render_report(ROOT, summary, content, audit, manifest, stability, selected)
