"""Create the student-format brief report from measured LAB10 artifacts."""

import json
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
reports = ROOT / "reports"
metrics = pd.read_csv(reports / "metrics.csv")
diagnostics = json.loads((reports / "diagnostics.json").read_text())
runtime = json.loads((reports / "runtime.json").read_text())
manifest = json.loads((reports / "download_manifest.json").read_text())
ae = metrics.query("model=='AE'").iloc[0]
vae = metrics.query("model=='VAE'").iloc[0]

conclusion = f"""# Cierre interpretativo · LAB10

Resultado de reconstrucción: AE logra MSE {ae.mse:.6f}, VAE con media posterior {vae.mse:.6f}; ambos mejoran el baseline .086641. AE pierde estampados y detalles; VAE confunde el bolso #797 con una prenda superior. Bag es la clase de mayor MSE; no se interpreta como error de clasificación.

Resultado de generación: VAE produce prendas superiores, pantalones y calzado con bordes borrosos y formas ambiguas. El AE con el mismo prior N(0,I) produce imágenes oscuras y poco variadas; ese prior no está calibrado para su latente. No se concluye que todas las estrategias generativas AE fallen.

Evidencia de diversidad: MSE medio entre pares VAE {diagnostics["vae_generated"]["mean_pairwise_mse"]:.5f}, AE-prior {diagnostics["ae_arbitrary_prior"]["mean_pairwise_mse"]:.5f}; los 16 originales dan {diagnostics["heldout_16"]["mean_pairwise_mse"]:.5f}. Son distancias de píxel, no realismo ni diversidad semántica certificados, con referencia de distinto tamaño. Las clases de vecinos son diagnósticos indirectos y desbalanceados.

Comportamiento del latente: interpolaciones graduales en píxeles, con formas intermedias ambiguas. El VAE contiene medias en escala más cercana al prior; los ejes no tienen significado garantizado. KL de prueba {diagnostics["vae_kl_nats"]:.4f} nats; no se observa colapso total a una única salida, pero no se descarta cobertura parcial. AE usa coordenadas de escala mayor.

Costo computacional: CPU, AE {ae.fit_seconds:.2f} s / 6 épocas y VAE {vae.fit_seconds:.2f} s / 8 épocas, incluyendo validación y trazado. No es una comparación a igual presupuesto. Tamaños .keras {ae.model_bytes / 1e6:.3f} y {vae.model_bytes / 1e6:.3f} MB. No se midieron energía ni pico de RAM. Inferencia 10,000: {ae.inference_seconds:.3f} s AE y {vae.inference_seconds:.3f} s VAE, en este equipo.

Riesgo o limitación: una semilla, latente de solo 2 dimensiones, intensidades de baja resolución, métrica no perceptual y vecinos sin auditoría formal de privacidad. Los 256 outputs tienen MSE medio a fit {diagnostics["vae_nn_mse_mean"]:.5f} y mínimo {diagnostics["vae_nn_mse_min"]:.5f}, sin distancia cero detectada; no demuestra originalidad ni ausencia de memorización. El dato puede ser semejante por ser un prototipo suavizado.

Decisión sobre uso previsto: AE para enseñar reconstrucción y VAE para muestreo probabilístico. No usar como catálogo comercial ni afirmar privacidad o novedad. Siguiente paso: mayor latente y redes convolucionales, igual presupuesto, varias semillas, métricas perceptuales y de diversidad adecuadas; otra prueba independiente al ajustar configuraciones. GAN y transferencia solo se comparan conceptualmente, sin entrenamiento en esta entrega.
"""
(ROOT / "docs/CONCLUSION.md").write_text(conclusion, encoding="utf-8")
fonts = Path("C:/Windows/Fonts")
if (fonts / "calibri.ttf").exists():
    for name, file in [
        ("C", "calibri.ttf"),
        ("CB", "calibrib.ttf"),
        ("CI", "calibrii.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / file)))
    pdfmetrics.registerFontFamily(
        "C", normal="C", bold="CB", italic="CI", boldItalic="CB"
    )
    normal, bold, italic = "C", "CB", "CI"
else:
    normal, bold, italic = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
styles = {
    "body": ParagraphStyle(
        "body", fontName=normal, fontSize=10, leading=13, spaceAfter=6
    ),
    "small": ParagraphStyle(
        "small",
        fontName=normal,
        fontSize=8.5,
        leading=11,
        spaceAfter=5,
        textColor=colors.HexColor("#555555"),
    ),
    "section": ParagraphStyle(
        "section",
        fontName=bold,
        fontSize=14,
        leading=17,
        spaceBefore=8,
        spaceAfter=6,
        textColor=colors.HexColor("#2471bf"),
    ),
    "title": ParagraphStyle(
        "title",
        fontName=bold,
        fontSize=22,
        leading=26,
        spaceAfter=7,
        textColor=colors.HexColor("#17365d"),
    ),
    "subtitle": ParagraphStyle(
        "subtitle",
        fontName=italic,
        fontSize=11,
        leading=14,
        spaceAfter=8,
        textColor=colors.HexColor("#555555"),
    ),
    "cell": ParagraphStyle("cell", fontName=normal, fontSize=8, leading=10),
    "head": ParagraphStyle("head", fontName=bold, fontSize=8, leading=10),
}
story = []


def p(text, style="body"):
    story.append(Paragraph(text, styles[style]))


def section(n, text):
    p(f"{n}. {text}", "section")


def img(filename, width=468):
    picture = Image(str(reports / filename))
    picture.drawHeight = picture.imageHeight * width / picture.imageWidth
    picture.drawWidth = width
    story.append(picture)
    story.append(Spacer(1, 6))


def table(data, widths):
    rows = [
        [Paragraph(escape(str(c)), styles["head" if i == 0 else "cell"]) for c in row]
        for i, row in enumerate(data)
    ]
    t = Table(rows, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f3f6")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d9e0e8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 7))


p("U03 · Autoencoder y VAE", "title")
story.append(
    HRFlowable(
        width="100%", thickness=0.7, color=colors.HexColor("#4472c4"), spaceAfter=8
    )
)
p("LAB10 · Evidencias del Ejercicio 06", "subtitle")
p("Victor Manuel Perez Padilla | Matrícula: 100801946")
p(
    "Unidad 03 · Algoritmos y características generativas<br/>Guía docente: Edwin Ramón José Nolasco",
    "small",
)
p(
    '<link href="https://github.com/vmperez997-max/Practica-5-6/tree/main/generativos" color="#0563c1">Repositorio del proyecto · carpeta generativos</link>'
)
section(1, "Objetivo y estado de la entrega")
p(
    "Comparar compresión y reconstrucción con generación probabilística, examinando fidelidad, diversidad, latente y costo. TensorFlow está aislado del recomendador. El ZIP docente devolvió HTTP 403: se implementó el proyecto siguiendo la guía, sin afirmar que sea la base oficial. Se entregan modelos, notebook ejecutado, pruebas y app de inferencia."
)
section(2, "Datos y protocolo reproducible")
p(
    "Fashion-MNIST, Zalando Research, licencia MIT: 60,000 imágenes de entrenamiento y 10,000 de prueba, 28×28 en gris. Se separan 50,000 fit y 10,000 validación estratificada, semilla 42; prueba se evalúa tras elegir checkpoints por validación. Normalización float32 / 255. Las etiquetas no condicionan los modelos."
)
p(
    "Fuente fijada por commit "
    + manifest["upstream_commit"]
    + ". SHA-256 y fechas de los cuatro archivos: reports/download_manifest.json. Aviso MIT conservado; no se redistribuye la descarga completa ni MovieLens.",
    "small",
)
section(3, "Modelos y tabla principal de resultados")
p(
    "Redes densas 784 → 256 → 128 → latente 2; decoder 128 → 256 → 784 sigmoid. AE minimiza BCE sumada; VAE usa reparametrización y suma KL con beta=1. Adam .001, batch 256. Se restaura la época 6 AE y 8 VAE por menor pérdida de validación."
)
table(
    [
        ["Modelo", "MSE prueba", "BCE/píxel", "Épocas", "Fit (s)", "Modelo MB"],
        ["Imagen media", "0.086641", "0.491094", "0", "No medido", "0.0031*"],
        [
            "AE",
            f"{ae.mse:.6f}",
            f"{ae.bce_per_pixel:.6f}",
            "6",
            f"{ae.fit_seconds:.2f}",
            f"{ae.model_bytes / 1e6:.3f}",
        ],
        [
            "VAE (media)",
            f"{vae.mse:.6f}",
            f"{vae.bce_per_pixel:.6f}",
            "8",
            f"{vae.fit_seconds:.2f}",
            f"{vae.model_bytes / 1e6:.3f}",
        ],
    ],
    [90, 78, 78, 58, 78, 86],
)
p(
    "*Baseline: 784 float32 sin contenedor. Otros: tamaño real .keras sin optimizador. CPU, Python "
    + runtime["python"]
    + ", TensorFlow "
    + runtime["tensorflow"]
    + ". Tiempo incluye fit, validación y trazado; excluye descarga, figuras y serialización. No se midieron energía ni pico de RAM. Presupuestos de épocas distintos; una semilla de entrenamiento.",
    "small",
)

story.append(PageBreak())
section(4, "Reconstrucción: panel no seleccionado")
p(
    "16 ejemplos uniformes sin reemplazo, semilla 2026; índices en panel_indices.json. Cada bloque contiene originales, AE y VAE con media posterior. Los mismos ejemplos se muestran completos, sin escoger los mejores."
)
img("reconstructions.png")
p(
    "Se pierden estampados de camiseta #263 y detalles del vestido #3702. Las sandalias #3547/#9049 quedan ambiguas y el VAE reconstruye el bolso #797 como prenda superior. Bag tiene mayor MSE: AE .03760 y VAE .05003; Sneaker el menor: .01943 y .01938. No son errores de clasificación.",
    "small",
)
img("curves.png")
p(
    "Las curvas de validación mejoran en el presupuesto probado; no demuestran ausencia de sobreajuste futuro. KL medio de prueba: 6.0725 nats. Además de reconstruir la media, una muestra posterior fija obtiene MSE .030705. Error bajo no prueba capacidad generativa.",
    "small",
)

story.append(PageBreak())
section(5, "Muestreo, diversidad y limitaciones")
p(
    "Primeras 16 de 256 muestras N(0,I), semilla 2026. Izquierda: VAE; derecha: AE con el mismo prior arbitrario. El AE no aprendió a ajustar su latente a esa distribución. La comparación no descarta otras estrategias de generación AE."
)
left = Image(str(reports / "samples_vae.png"), width=222, height=222)
right = Image(str(reports / "samples_ae.png"), width=222, height=222)
story.append(Table([[left, right]], colWidths=[234, 234]))
story.append(Spacer(1, 7))
p(
    "VAE produce prendas superiores, pantalones y calzado, pero con bordes borrosos y formas ambiguas. AE-prior produce salidas oscuras y parecidas. La diversidad numérica no mide realismo ni demuestra cobertura semántica."
)
table(
    [
        ["Diagnóstico", "VAE / AE-prior / referencia"],
        ["MSE medio entre pares", "0.08777 / 0.00628 / 0.21547"],
        ["Desviación media por píxel", "0.19015 / 0.04816 / 0.29231"],
    ],
    [213, 255],
)
p(
    "256 muestras por modelo frente a referencia de solo 16 originales; tamaños distintos. No se calculó FID ni una métrica perceptual validada en este dominio. Clases de vecinos son indicadores indirectos, no etiquetas certificadas de los sintéticos.",
    "small",
)
section(6, "Interpolación y espacio latente")
img("interpolation.png")
p(
    "Arriba: AE entre los dos primeros ejemplos del panel (bolso/abrigo); abajo: VAE entre los dos primeros puntos del prior. Los extremos se fijaron por semilla, sin escoger por estética. Hay transición gradual en píxeles, con formas intermedias ambiguas.",
    "small",
)
p(
    "El scatter de 2,000 ejemplos y la cuadrícula [-2,2]² están en notebook y reports. AE muestra escalas mayores; VAE concentra coordenadas más cerca del prior. KL>0 y muestras distintas no sugieren colapso total, pero no descartan colapso parcial. Los ejes no tienen significado semántico garantizado.",
    "small",
)

story.append(PageBreak())
section(7, "Vecinos cercanos y posible memorización")
p(
    "Cada una de 256 muestras se compara con los 50,000 ejemplos fit. Panel: primeras 16 muestras VAE y su vecino más cercano por MSE. Los índices originales y distancias se conservan en nearest_neighbors.csv."
)
img("nearest_neighbors.png")
p(
    "MSE al vecino: media .01021, mínimo .00248; los 16 originales de prueba dan media .02284. No hubo distancia cero. Las salidas suavizadas pueden parecer prototipos; estos resultados no prueban copia ni garantizan privacidad, originalidad o ausencia de memorización.",
    "small",
)
section(8, "Costo, pruebas y decisión de uso")
p(
    f"AE usa {ae.fit_seconds:.2f} s y VAE {vae.fit_seconds:.2f} s en este equipo; la comparación no iguala épocas. Inferencia de 10,000: .246 s AE y .243 s VAE. Decoder para app: .963 MB. El notebook verifica hashes, recarga modelos y recalcula MSE sobre toda la prueba. Las 9 pruebas pasan, incluida Streamlit; la app solo hace inferencia y no entrena por visita."
)
p(
    "Decisión: AE para reconstrucción didáctica y VAE para estudiar muestreo regularizado. No usar como catálogo comercial ni afirmar garantías de privacidad. Próximo experimento: igual presupuesto, varias semillas, mayor latente y convoluciones; evaluar diversidad y calidad perceptual y reservar una nueva prueba al ajustar modelos."
)
p(
    "GAN enfrenta generador/discriminador y puede colapsar; transferencia reutiliza representaciones y no es por sí sola generativa. Ambos se comparan conceptualmente, sin entrenarlos en esta entrega.",
    "small",
)
section(9, "IA, responsabilidad y referencias")
p(
    "Codex apoyó código, entrenamiento, pruebas y redacción. AI_USE_DECLARATION.md conserva prompt, verificaciones y correcciones; MODEL_CARD.md detalla límites. El estudiante debe revisar, reproducir y explicar la entrega. El formato sigue su documento de Unidad 02, Ejercicio 03.",
    "small",
)
p(
    'Xiao, Rasul y Vollgraf (2017). Fashion-MNIST. <link href="https://arxiv.org/abs/1708.07747" color="#0563c1">arXiv:1708.07747</link>. Kingma y Welling (2013). Auto-Encoding Variational Bayes. <link href="https://arxiv.org/abs/1312.6114" color="#0563c1">arXiv:1312.6114</link>. <link href="https://github.com/zalandoresearch/fashion-mnist" color="#0563c1">Fuente oficial y licencia MIT</link>. <link href="https://www.tensorflow.org/tutorials/generative/cvae" color="#0563c1">Tutorial oficial TensorFlow VAE</link>.',
    "small",
)

out = ROOT / "output/pdf/Unidad_03_Ejercicio_06_Victor_Perez.pdf"
out.parent.mkdir(parents=True, exist_ok=True)


def header_footer(canvas, doc):
    canvas.setFont(normal, 9)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(72, 748, "INF-8239 · Ciencia de Datos II | U03 · Ejercicio 06")
    canvas.drawRightString(540, 39, f"Victor Manuel Perez Padilla · {doc.page}")


SimpleDocTemplate(
    str(out),
    pagesize=(612, 792),
    leftMargin=72,
    rightMargin=72,
    topMargin=72,
    bottomMargin=62,
    title="Unidad 03. Ejercicio 06 - Victor Perez",
    author="Victor Manuel Perez Padilla",
).build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(out)
