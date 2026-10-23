"""Build a brief, evidence-linked report from executed experiment artifacts."""

import json
from itertools import combinations
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

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

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="TitleCustom",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=25,
        textColor=colors.HexColor("#14364b"),
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="Deck",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#496471"),
        spaceAfter=12,
    )
)
styles["BodyText"].fontSize = 9
styles["BodyText"].leading = 12
styles["BodyText"].spaceAfter = 7
styles["Heading2"].textColor = colors.HexColor("#14364b")
styles["Heading2"].fontSize = 13
styles["Heading2"].leading = 16
styles.add(ParagraphStyle(name="Tiny", fontSize=7.5, leading=10, spaceAfter=6))
story = []


def p(text, style="BodyText"):
    story.append(Paragraph(text, styles[style]))


def title(k, text):
    p(f"INF-8239 / EVIDENCIA {k}", "Deck")
    p(text, "TitleCustom")


def table(data, widths):
    cells = [[Paragraph(escape(str(x)), styles["Tiny"]) for x in row] for row in data]
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e1edf1")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f4f7f8")],
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 9))


title("01", "Recomendar con evidencia")
p("LAB08 + LAB09 · Ciencia de Datos II · Victor Perez · 23 de octubre de 2026", "Deck")
p(
    'Repositorio: <link href="https://github.com/vmperez997-max/Practica-5-6">github.com/vmperez997-max/Practica-5-6</link>'
)
p(
    "<b>Decisión.</b> Mantener popularidad como opción de menor costo. El híbrido 20/12 con alpha 0.75 es una alternativa para ampliar exposición: mejora poco el acierto y aumenta la cobertura. La elección es exploratoria, sin validación independiente."
)
p("Datos y protocolo", "Heading2")
p(
    f"MovieLens Latest Small: {audit['ratings']:,} ratings, {audit['users']} usuarios y {audit['movies']:,} películas; densidad {audit['density']:.2%}. Se reserva la última valoración por usuario: 100,226 registros de entrenamiento y 610 de prueba. Tres semillas (17, 42, 83), dos tamaños (8/4 y 20/12) y dos pesos híbridos. Todas las políticas usan el mismo catálogo y excluyen vistos."
)
p("Tabla principal · medias entre semillas", "Heading2")
data = [
    [
        "Método / f / épocas / alpha",
        "RMSE",
        "HR@10 %",
        "P@10 %",
        "Cob. %",
        "Seg.",
        "MB",
        "Pareto",
    ]
]
for row in summary.itertuples():
    label = {
        "popularity": "Popularidad",
        "content": "Contenido",
        "collaborative": "MF",
        "hybrid": "Híbrido",
    }[row.method]
    if row.factors:
        label += f" {row.factors}/{row.epochs}"
    if row.method == "hybrid":
        label += f" a={row.alpha}"
    data.append(
        [
            label,
            "-" if pd.isna(row.rmse) else f"{row.rmse:.3f}",
            f"{row.hit_rate_at_10 * 100:.2f}",
            f"{row.precision_at_10 * 100:.3f}",
            f"{row.coverage * 100:.2f}",
            f"{row.total_seconds:.2f}",
            f"{row.model_bytes / 1e6:.2f}",
            "Sí" if row.pareto else "No",
        ]
    )
table(
    data,
    [4.4 * cm, 1.2 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.2 * cm, 1.1 * cm, 1.2 * cm],
)
p(
    "HR principal cuenta la última interacción, incluso si el rating es bajo. Con un solo objetivo, P@10=HR@10/10. El RMSE del híbrido corresponde a MF; popularidad usa media global para RMSE, no el score de ranking. Contenido no predice estrellas. Cobertura usa las 9,742 películas. Los modelos deterministas se ejecutan una vez.",
    "Tiny",
)
p("Procedencia verificable", "Heading2")
p(
    "GroupLens Research, University of Minnesota. Datos anónimos, usuarios con al menos 20 valoraciones y sin demografía. Condiciones académicas/de investigación; el repositorio no redistribuye MovieLens. La auditoría valida columnas, claves, nulos, ratings y timestamps."
)
p("SHA-256 del ZIP: " + manifest["sha256_zip"], "Tiny")
p(
    "Descarga UTC: "
    + manifest["downloaded_utc"]
    + ". Hashes CSV y distribución: reports/audit.json.",
    "Tiny",
)
story.append(PageBreak())
title("02", "Contenido y usuarios fríos")
p("Cómo leer las recomendaciones", "Heading2")
p(
    "Popularidad suaviza la media de cada película con la media global y usa evidencia mínima (percentil 80 del conteo). Contenido usa TF-IDF de géneros y coseno. MF aprende vectores mediante SGD sobre ratings explícitos. Híbrido combina scores normalizados: alpha·CF + (1-alpha)·contenido, sobre todos los candidatos sin vistos."
)
data = [["Consulta", "Primera recomendación", "Géneros / score"]]
for query, group in content.groupby("query", sort=False):
    row = group.iloc[0]
    data.append([query, row.title, f"{row.genres} / {row.content_score:.3f}"])
table(data, [4.5 * cm, 5.3 * cm, 5.8 * cm])
p(
    "La consulta no aparece en su propio Top-10. Vectores de géneros idénticos producen empates, aunque las películas sean diferentes. En Shawshank, la repetición de Crime/Drama ejemplifica sobre-especialización: no se considera trama ni experiencia individual. Las tres listas completas están en content_recommendations.csv; la interfaz muestra fuente, método y limitación."
)
p("Tres perfiles · híbrido 20/12, alpha 0.75, semilla 42", "Heading2")
data = [
    [
        "Perfil / usuario / historial",
        "Primeras tres recomendaciones",
        "Estabilidad entre semillas",
    ]
]
for s in stability:
    g = selected[
        (selected.profile == s["profile"]) & (selected.seed == 42)
    ].sort_values("rank")
    data.append(
        [
            f"{s['profile']} / {s['userId']} / {s['history_size']}",
            "; ".join(g.title.head(3)),
            f"Jaccard medio {s['mean_jaccard_seeds']:.3f}",
        ]
    )
table(data, [3.5 * cm, 9.2 * cm, 2.9 * cm])
p(
    "El usuario amplio y el pequeño excluyen todo su historial. El menor historial sigue teniendo 19 ratings: no prueba rendimiento con 1-2 ratings. El usuario nuevo (-1) es sintético; recibe popularidad no personalizada y estable entre semillas. No se inventa precisión para él porque no existe un ítem objetivo observado."
)
p("Cold start de ítems y calidad del ranking", "Heading2")
p(
    "23 objetivos no aparecen en entrenamiento; MF usa media global para su rating, y el ranking conserva esos usuarios en el denominador. El contenido puede usar sus géneros. La evaluación también informa HR restringido a 363 ratings positivos (>=4): popularidad "
    + f"{pop.positive_hit_rate_at_10:.2%}"
    + ", MF 20/12 "
    + f"{cf.positive_hit_rate_at_10:.2%}"
    + ", híbrido .75 "
    + f"{hybrid.positive_hit_rate_at_10:.2%}"
    + ". Ninguna métrica offline garantiza satisfacción."
)
p(
    "Evidencias: profile_recommendations.csv contiene los Top-10 por configuración; profile_stability.csv compara conjuntos mediante Jaccard; tests/test_app.py verifica las tres consultas en Streamlit.",
    "Tiny",
)
story.append(PageBreak())
title("03", "Costo, límites y decisión")
p("Pareto y Green AI", "Heading2")
p(
    f"Pareto maximiza HR y cobertura y minimiza tiempo y tamaño. Popularidad tarda {pop.total_seconds:.2f} s y ocupa {pop.model_bytes / 1e6:.2f} MB. Híbrido 20/12, alpha .75 tarda {hybrid.total_seconds:.2f} s y ocupa {hybrid.model_bytes / 1e6:.2f} MB: {hybrid.total_seconds / pop.total_seconds:.1f} veces el tiempo por {(hybrid.hit_rate_at_10 - pop.hit_rate_at_10) * 100:.3f} puntos porcentuales extra de HR. La cobertura pasa de {pop.coverage:.2%} a {hybrid.coverage:.2%}."
)
p(
    f"Entre híbridos 20/12, alpha .75 obtiene HR {hybrid.hit_rate_at_10:.2%} frente a {low.hit_rate_at_10:.2%} con .25, pero reduce cobertura de {low.coverage:.2%} a {hybrid.coverage:.2%}. El MF puro obtiene HR {cf.hit_rate_at_10:.2%}. No hay un ganador universal; la preferencia por menor costo justifica popularidad como política inicial y conservar el híbrido como experimento de exposición."
)
p(
    "Segundos = entrenamiento MF + ranking de todos los usuarios; se excluyen descarga, carga, TF-IDF compartido e I/O. MB = estado serializado por método, sin historial, datos originales ni runtime. Los tiempos son una medición local con ruido; no se midieron energía ni emisiones. Las desviaciones entre semillas figuran en pareto.csv."
)
p("Límites y siguiente experimento", "Heading2")
p(
    "El corte ordena por usuario, timestamp y movieId; 94 usuarios tienen empates en el límite, sin orden real conocido. Interacciones posteriores de otros usuarios pueden entrar en entrenamiento. La disponibilidad histórica del catálogo tampoco se restringe. La selección de alpha consulta esta misma prueba y no confirma generalización. Tres semillas comparten usuarios y partición; no prueban significancia estadística."
)
p(
    "Siguiente paso: partición global estricta con validación y test separados, disponibilidad temporal de películas, más de un positivo retenido y métricas de diversidad por usuario. Monitorear popularidad dominante y bucles de retroalimentación; probar reranking diversificado. Sin demografía no se pueden afirmar resultados por grupos poblacionales."
)
p("Reproducción y uso de IA", "Heading2")
p(
    "Ejecutar uv sync, descargar con scripts/download_data.py y ejecutar scripts/build_notebook.py. El notebook entrena, evalúa y ejecuta las pruebas; scripts/build_report.py reconstruye este informe. README documenta la app y requirements.txt permite instalación con pip. El proyecto reutiliza la base docente de Edwin Ramón José Nolasco."
)
p(
    "Codex apoyó código, depuración, experimentos, pruebas y redacción. docs/AI_USAGE.md registra el prompt, correcciones y verificaciones. El estudiante debe revisar y poder explicar los resultados antes de entregar; no se afirma que su defensa ya haya ocurrido."
)
p("Referencias", "Heading2")
p(
    'GroupLens. MovieLens Latest Small, README y condiciones: <link href="https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html">README oficial</link>. Harper, F. M. y Konstan, J. A. (2015). The MovieLens Datasets: History and Context. ACM TiiS 5(4), artículo 19. <link href="https://doi.org/10.1145/2827872">doi:10.1145/2827872</link>.',
    "Tiny",
)

out = ROOT / "output/pdf"
out.mkdir(parents=True, exist_ok=True)


def footer(canvas, doc):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#496471"))
    canvas.drawString(1.8 * cm, 1.1 * cm, "INF-8239 · LAB08 + LAB09 · Victor Perez")
    canvas.drawRightString(19.2 * cm, 1.1 * cm, str(doc.page))


SimpleDocTemplate(
    str(out / "Informe_Recomendadores.pdf"),
    pagesize=(21 * cm, 29.7 * cm),
    rightMargin=1.8 * cm,
    leftMargin=1.8 * cm,
    topMargin=1.5 * cm,
    bottomMargin=1.7 * cm,
    title="Sistemas recomendadores: evidencia y decisión",
    author="Victor Perez",
).build(story, onFirstPage=footer, onLaterPages=footer)
print(out / "Informe_Recomendadores.pdf")
