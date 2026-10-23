"""Report layout based on the student's Unidad 02 / Ejercicio 03 reference."""

from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def render_report(root, summary, content, audit, manifest, stability, selected):
    font_dir = Path("C:/Windows/Fonts")
    if (font_dir / "calibri.ttf").exists():
        for name, filename in [
            ("Calibri", "calibri.ttf"),
            ("Calibri-Bold", "calibrib.ttf"),
            ("Calibri-Italic", "calibrii.ttf"),
        ]:
            pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))
        pdfmetrics.registerFontFamily(
            "Calibri",
            normal="Calibri",
            bold="Calibri-Bold",
            italic="Calibri-Italic",
            boldItalic="Calibri-Bold",
        )
        normal, bold, italic = "Calibri", "Calibri-Bold", "Calibri-Italic"
    else:
        normal, bold, italic = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
    styles = {
        "body": ParagraphStyle(
            "body",
            fontName=normal,
            fontSize=10.5,
            leading=14,
            spaceAfter=7,
            textColor=colors.HexColor("#222222"),
        ),
        "title": ParagraphStyle(
            "title",
            fontName=bold,
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#17365d"),
            spaceAfter=7,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName=italic,
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#555555"),
            spaceAfter=9,
        ),
        "section": ParagraphStyle(
            "section",
            fontName=bold,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#2471bf"),
            spaceBefore=10,
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "small",
            fontName=normal,
            fontSize=9,
            leading=12,
            spaceAfter=6,
            textColor=colors.HexColor("#555555"),
        ),
        "table": ParagraphStyle("table", fontName=normal, fontSize=8.5, leading=11),
        "tablehead": ParagraphStyle(
            "tablehead", fontName=bold, fontSize=8.5, leading=11
        ),
        "meta": ParagraphStyle(
            "meta", fontName=normal, fontSize=10, leading=13, spaceAfter=4
        ),
    }
    story = []

    def p(text, style="body"):
        story.append(Paragraph(text, styles[style]))

    def section(number, text):
        p(f"{number}. {text}", "section")

    def table(data, widths):
        rows = [
            [
                Paragraph(
                    escape(str(value)), styles["tablehead" if i == 0 else "table"]
                )
                for value in row
            ]
            for i, row in enumerate(data)
        ]
        t = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f3f6")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d9e0e8")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 9))

    pop = summary.query("method == 'popularity'").iloc[0]
    cf = summary.query("method == 'collaborative' and factors == 20").iloc[0]
    hybrid = summary.query(
        "method == 'hybrid' and factors == 20 and alpha == 0.75"
    ).iloc[0]
    low = summary.query("method == 'hybrid' and factors == 20 and alpha == 0.25").iloc[
        0
    ]

    p("U03 · Sistemas recomendadores", "title")
    story.append(
        HRFlowable(
            width="100%", thickness=0.7, color=colors.HexColor("#4472c4"), spaceAfter=9
        )
    )
    p("LAB08 y LAB09 · Evidencias del Ejercicio 05", "subtitle")
    p("Victor Manuel Perez Padilla | Matrícula: 100801946", "meta")
    p("Unidad 03 · Algoritmos y características generativas", "meta")
    p("Guía docente: Edwin Ramón José Nolasco", "meta")
    p(
        '<link href="https://github.com/vmperez997-max/Practica-5-6" color="#0563c1">Repositorio del proyecto</link>',
        "meta",
    )
    section(1, "Objetivo y estado de la entrega")
    p(
        "Comparar popularidad, contenido, factorización e híbrido con datos reproducibles, evaluación temporal y análisis de costo. Se reutilizó el proyecto base del curso y un único entorno Python 3.12 con uv. La entrega incluye notebook ejecutado, código, pruebas, reportes, tarjetas y declaración de IA; el repositorio está publicado en GitHub."
    )
    section(2, "Fuente, descarga y auditoría")
    p(
        "MovieLens Latest Small, GroupLens Research, University of Minnesota. Es una edición de desarrollo que puede cambiar; no debe presentarse como benchmark archivado. Contiene ratings explícitos de 0.5 a 5 y usuarios anónimos con al menos 20 valoraciones. No incluye demografía."
    )
    table(
        [
            ["Indicador", "Resultado"],
            ["Usuarios / películas / valoraciones", "610 / 9,742 / 100,836"],
            ["Películas con ratings / densidad", "9,724 / 1.6968%"],
            ["Periodo observado (UTC)", "29-03-1996 a 24-09-2018"],
            ["Entrenamiento / prueba", "100,226 / 610 interacciones"],
            [
                "Objetivos no vistos en entrenamiento",
                "23; se conservan en el denominador",
            ],
            ["Empates temporales en el límite", "94 usuarios; desempate por movieId"],
        ],
        [235, 233],
    )
    p(
        "Se validaron columnas, nulos, claves, duplicados usuario-película, rango e incrementos de ratings y timestamps numéricos no negativos. Los originales no se modifican ni se redistribuyen. Condiciones: uso de investigación, reconocimiento obligatorio y permiso previo para uso comercial.",
        "small",
    )
    p("SHA-256 del ZIP original:", "small")
    p(manifest["sha256_zip"], "small")
    p(
        "Fecha de descarga UTC: "
        + manifest["downloaded_utc"]
        + ". Fuente: reports/download_manifest.json y reports/audit.json.",
        "small",
    )

    story.append(PageBreak())
    section(3, "Partición, modelos y métricas")
    p(
        "Se retiene la última valoración de cada usuario elegible, ordenando por usuario, timestamp y movieId. Todos los métodos evalúan los mismos 610 usuarios sobre las 9,742 películas, excluyendo vistas. Medias, perfiles y factores usan entrenamiento; los metadatos de géneros se conocen para todo el catálogo."
    )
    p(
        "Popularidad combina media del ítem y media global, con evidencia mínima igual al percentil 80 del conteo. Contenido usa TF-IDF y coseno; el perfil pondera ratings mediante max(rating-2.5, 0.1). MF aprende vectores latentes mediante SGD. El híbrido combina scores min-max: alpha·CF + (1-alpha)·contenido, sin prefiltrar candidatos por MF."
    )
    p(
        "Se comparan 8 factores/4 épocas y 20/12, con semillas 17, 42 y 83 y alpha 0.25 y 0.75. MF usa learning rate .01 y regularización .05. Las dimensiones latentes no tienen significado humano garantizado.",
        "small",
    )
    section(4, "Tabla principal de resultados")
    data = [
        [
            "Modelo / f / épocas / alpha",
            "RMSE*",
            "HR@10 %",
            "P@10 %",
            "Cob. %",
            "Seg.",
            "MB",
        ]
    ]
    for r in summary.itertuples():
        label = {
            "popularity": "Popularidad",
            "content": "Contenido",
            "collaborative": "MF",
            "hybrid": "Híbrido",
        }[r.method]
        if r.factors:
            label += f" {r.factors}/{r.epochs}"
        if r.method == "hybrid":
            label += f" / {r.alpha}"
        data.append(
            [
                label,
                "-" if pd.isna(r.rmse) else f"{r.rmse:.4f}",
                f"{r.hit_rate_at_10 * 100:.2f}",
                f"{r.precision_at_10 * 100:.3f}",
                f"{r.coverage * 100:.2f}",
                f"{r.total_seconds:.2f}",
                f"{r.model_bytes / 1e6:.2f}",
            ]
        )
    table(data, [146, 55, 57, 57, 53, 48, 52])
    p(
        "Fuente: reports/metrics.csv y reports/pareto.csv. Media de tres semillas para métodos estocásticos; deterministas una vez. HR mide recuperar la última interacción, incluso con rating bajo; con un único objetivo P@10=HR/10. Cobertura = unión de Top-10 / catálogo.",
        "small",
    )
    p(
        "* El RMSE de popularidad usa media global, no su score de ranking. El del híbrido corresponde al componente MF: la mezcla normalizada no predice estrellas. Ítems desconocidos usan media global. No se mide RMSE de contenido.",
        "small",
    )
    p(
        f"MF 20/12 reduce RMSE a {cf.rmse:.4f} y obtiene HR {cf.hit_rate_at_10:.2%}. Para los 363 objetivos con rating >=4, HR es {pop.positive_hit_rate_at_10:.2%} en popularidad, {cf.positive_hit_rate_at_10:.2%} en MF y {hybrid.positive_hit_rate_at_10:.2%} en híbrido .75. Aproximar ratings y acertar rankings son tareas distintas."
    )
    section(5, "Tres consultas por contenido")
    data = [["Película consultada", "Primera recomendación / géneros"]]
    for query, g in content.groupby("query", sort=False):
        r = g.iloc[0]
        data.append([query, f"{r.title} / {r.genres}"])
    table(data, [183, 285])
    p(
        "Ninguna consulta aparece en su Top-10. Géneros idénticos generan vectores y scores iguales. Repetir Crime/Drama en Shawshank ilustra sobre-especialización: similitud de metadatos no garantiza agrado. La interfaz muestra fuente, método y limitación.",
        "small",
    )

    story.append(PageBreak())
    section(6, "Perfiles, cold start y estabilidad")
    p(
        "Se seleccionan máximo y mínimo historial de entrenamiento, además del usuario sintético -1. Las listas excluyen vistos. El historial mínimo observado aún tiene 19 ratings: no representa un usuario con una o dos interacciones. El nuevo recibe popularidad no personalizada; no existe un objetivo observado para medir su precisión."
    )
    data = [
        ["Perfil / usuario / historial", "Primeras tres recomendaciones", "Jaccard"]
    ]
    for s in stability:
        group = selected[
            (selected.profile == s["profile"]) & (selected.seed == 42)
        ].sort_values("rank")
        data.append(
            [
                f"{s['profile']} / {s['userId']} / {s['history_size']}",
                "; ".join(group.title.head(3)),
                f"{s['mean_jaccard_seeds']:.3f}",
            ]
        )
    table(data, [125, 287, 56])
    p(
        "Ejemplo: híbrido 20/12, alpha .75, semilla 42. Jaccard compara los conjuntos Top-10 entre las tres parejas de semillas. Fuente: profile_recommendations.csv y profile_stability.csv. La menor estabilidad del perfil pequeño evidencia dependencia del ajuste; el fallback nuevo es compartido y estable.",
        "small",
    )
    p(
        "Un ítem sin ratings de entrenamiento carece de vector aprendido: MF usa media global. Contenido puede usar sus géneros, si están disponibles. Esta política evita excluir los 23 objetivos nuevos y reportar métricas artificialmente favorables."
    )
    section(7, "Híbrido, Pareto y costo computacional")
    p(
        f"Con 20/12, alpha .75 obtiene HR {hybrid.hit_rate_at_10:.2%} frente a {low.hit_rate_at_10:.2%} con .25. El mayor peso colaborativo aumenta aciertos, pero reduce cobertura de {low.coverage:.2%} a {hybrid.coverage:.2%}. Entre híbridos se elige .75 por ese intercambio observado; no se afirma superioridad universal."
    )
    p(
        f"Popularidad tarda {pop.total_seconds:.2f} s y ocupa {pop.model_bytes / 1e6:.2f} MB; híbrido .75 tarda {hybrid.total_seconds:.2f} s y ocupa {hybrid.model_bytes / 1e6:.2f} MB. Su ganancia media es {(hybrid.hit_rate_at_10 - pop.hit_rate_at_10) * 100:.3f} puntos porcentuales de HR, con {hybrid.total_seconds / pop.total_seconds:.1f} veces el tiempo; la cobertura pasa de {pop.coverage:.2%} a {hybrid.coverage:.2%}."
    )
    p(
        "Pareto maximiza HR y cobertura y minimiza segundos y bytes. Una configuración está dominada si otra no empeora ninguno de esos objetivos y mejora al menos uno. Se usan medias entre semillas; pareto.csv y pareto.png registran la frontera. Híbrido 8/4/.75 queda dominado; varias alternativas permanecen en la frontera."
    )
    p(
        "Tiempo = entrenamiento MF + ranking de 610 usuarios; excluye descarga, carga, TF-IDF compartido e I/O. Tamaño = estado serializado por método (ids, popularidad y contenido/MF cuando aplica), sin historial ni entorno. No se publican los objetos ni se miden energía o emisiones. Los tiempos tienen ruido local.",
        "small",
    )
    p(
        "Decisión Green AI: mantener popularidad como referencia económica inicial; conservar el híbrido 20/12/.75 para estudiar personalización y exposición. La complejidad adicional necesita justificar su mejora marginal. Cobertura no equivale a diversidad individual ni satisfacción."
    )

    story.append(PageBreak())
    section(8, "Pruebas, entorno y publicación")
    p(
        "Entorno verificado: Python 3.12.14, uv y un único .venv. El notebook se ejecutó sin celdas con error. Las 16 pruebas locales incluyen contratos, errores, corte, exclusión de vistos, fallback, extremos del híbrido, métricas, Pareto y tres consultas Streamlit. GitHub Actions verifica el código sin redistribuir el dataset."
    )
    p(
        "uv sync --locked<br/>uv run python scripts/download_data.py<br/>uv run python scripts/build_notebook.py<br/>uv run python scripts/build_report.py<br/>uv run streamlit run app/streamlit_app.py",
        "small",
    )
    p(
        "README y requirements.txt documentan instalación y ejecución. Se usan rutas relativas; .venv, credenciales, temporales y datos quedan fuera de Git. El repositorio contiene src, tests, reports, notebook ejecutado, Dataset Card, System Card e informe. La plataforma local necesita acceso HTTPS a GroupLens."
    )
    section(9, "Límites, riesgos y cierre interpretativo")
    p(
        "Resultado principal: MF mejora aproximación de ratings y ranking frente a su versión pequeña, mientras el híbrido intercambia acierto y cobertura. Popularidad mantiene una utilidad cercana con mucho menor costo. El usuario frío recibe una lista útil como referencia, sin presentarla como personalizada."
    )
    p(
        "Límites: 94 empates no permiten reconstruir el orden real; el corte por usuario admite futuro de otros usuarios y no controla disponibilidad temporal del catálogo. La comparación usa la misma prueba para elegir alpha, sin validación independiente. Las tres semillas comparten usuarios y partición: no demuestran significancia estadística."
    )
    p(
        "Riesgos: concentración popular, repetición de géneros, sesgo de selección y retroalimentación de futuras recomendaciones. Sin demografía no pueden afirmarse resultados por grupos. Mitigación: medir exposición, novedad y diversidad por usuario; probar reranking diversificado y vigilar concentración."
    )
    p(
        "Siguiente experimento: corte global estricto con disponibilidad de ítems, validación separada y prueba final intacta, múltiples positivos retenidos y evaluación de diversidad. La decisión actual es exploratoria; un Top-10 no es una verdad universal ni garantiza satisfacción."
    )
    section(10, "Uso de IA y referencias")
    p(
        "Codex apoyó implementación, depuración, experimentos, pruebas y redacción. docs/AI_USAGE.md registra el prompt, verificaciones y correcciones. El estudiante debe revisar, reproducir y explicar la entrega antes de presentarla. El formato de este informe sigue el documento personal de Unidad 02, Ejercicio 03.",
        "small",
    )
    p(
        'GroupLens. MovieLens Latest Small: <link href="https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html" color="#0563c1">README y condiciones oficiales</link>. Harper, F. M. y Konstan, J. A. (2015). The MovieLens Datasets: History and Context. ACM TiiS 5(4), artículo 19. <link href="https://doi.org/10.1145/2827872" color="#0563c1">doi:10.1145/2827872</link>.',
        "small",
    )

    out = root / "output/pdf/Informe_Recomendadores.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    def header_footer(canvas, doc):
        canvas.setFont(normal, 9)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(
            72, 748, "INF-8239 · Ciencia de Datos II | U03 · Ejercicio 05"
        )
        canvas.drawRightString(540, 39, f"Victor Manuel Perez Padilla · {doc.page}")

    SimpleDocTemplate(
        str(out),
        pagesize=(612, 792),
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=62,
        title="Unidad 03. Ejercicio 05 - Victor Perez",
        author="Victor Manuel Perez Padilla",
    ).build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(out)
