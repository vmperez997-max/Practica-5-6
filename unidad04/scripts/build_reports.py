"""Two brief student-format PDFs, built only from executed U04 evidence."""

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
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
comparison = pd.read_csv(ROOT / "reports/lab12/comparison.csv")
groups = pd.read_csv(ROOT / "reports/lab12/fairness_by_group.csv", index_col=0)
inter = pd.read_csv(ROOT / "reports/lab12/fairness_intersectional.csv", index_col=0)
risks = pd.read_csv(ROOT / "reports/lab11/risk_register_scored.csv")
decision = json.loads(
    (ROOT / "reports/lab13/deployment_decision.json").read_text(encoding="utf-8")
)
incident = json.loads(
    (ROOT / "reports/lab13/incident_log.json").read_text(encoding="utf-8")
)
provenance = json.loads(
    (ROOT / "reports/lab13/provenance.json").read_text(encoding="utf-8")
)
test_summary = (ROOT / "reports/tests.txt").read_text(encoding="utf-8").splitlines()
test_summary = next(line for line in reversed(test_summary) if "passed" in line)
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
        "body", fontName=normal, fontSize=10, leading=13, spaceAfter=7
    ),
    "small": ParagraphStyle(
        "small",
        fontName=normal,
        fontSize=8.5,
        leading=11,
        spaceAfter=6,
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
        fontSize=21,
        leading=25,
        spaceAfter=8,
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
    "cell": ParagraphStyle("cell", fontName=normal, fontSize=8.5, leading=11),
    "head": ParagraphStyle("head", fontName=bold, fontSize=8.5, leading=11),
}


class Report:
    def __init__(self, exercise, title, subtitle):
        self.exercise = exercise
        self.story = []
        self.p(title, "title")
        self.story.append(
            HRFlowable(
                width="100%",
                thickness=0.7,
                color=colors.HexColor("#4472c4"),
                spaceAfter=8,
            )
        )
        self.p(subtitle, "subtitle")
        self.p("Victor Manuel Perez Padilla | Matrícula: 100801946")
        self.p(
            "INF-8239 · Unidad 04 · Ética y roles en Ciencia de Datos<br/>Guía docente: Edwin Ramón José Nolasco",
            "small",
        )
        self.p(
            '<link href="https://github.com/vmperez997-max/Practica-5-6/tree/main/unidad04" color="#0563c1">Repositorio del proyecto · carpeta unidad04</link>'
        )

    def p(self, text, style="body"):
        self.story.append(Paragraph(text, styles[style]))

    def section(self, n, text):
        self.p(f"{n}. {text}", "section")

    def page(self):
        self.story.append(PageBreak())

    def table(self, data, widths):
        rows = [
            [
                Paragraph(escape(str(c)), styles["head" if i == 0 else "cell"])
                for c in row
            ]
            for i, row in enumerate(data)
        ]
        table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(
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
        self.story.extend([table, Spacer(1, 7)])

    def save(self):
        path = ROOT / f"output/pdf/Unidad_04_Ejercicio_{self.exercise}_Victor_Perez.pdf"
        path.parent.mkdir(parents=True, exist_ok=True)

        def header_footer(canvas, doc):
            canvas.setFont(normal, 9)
            canvas.setFillColor(colors.HexColor("#777777"))
            canvas.drawString(
                72,
                748,
                f"INF-8239 · Ciencia de Datos II | U04 · Ejercicio {self.exercise}",
            )
            canvas.drawRightString(540, 39, f"Victor Manuel Perez Padilla · {doc.page}")

        SimpleDocTemplate(
            str(path),
            pagesize=(612, 792),
            leftMargin=72,
            rightMargin=72,
            topMargin=72,
            bottomMargin=62,
            title=f"Unidad 04. Ejercicio {self.exercise} - Victor Perez",
            author="Victor Manuel Perez Padilla",
        ).build(self.story, onFirstPage=header_footer, onLaterPages=header_footer)
        print(path)


e = Report(
    "07", "U04 · Impacto y equidad", "LAB11 y LAB12 · Evidencias del Ejercicio 07"
)
e.section(1, "Finalidad, interesados y proporcionalidad")
e.p(
    "Ensayar un DSS que prioriza evidencia para revisión humana, sin declarar emergencias, elegibilidad o intervenciones. El estudiante eligió como daño prioritario no omitir zonas que necesitan revisión. El caso es totalmente sintético: no representa personas, territorios ni estadísticas reales de República Dominicana."
)
e.p(
    "Alternativa menos invasiva: revisar todos los casos por orden de recepción y lista de comprobación. El score no elimina casos. No se ha acreditado que el modelo sea necesario o proporcional para un uso real: se limita al laboratorio, con segundo operador para apelación y facultad humana de anular."
)
e.table(
    [
        ["Interesado ficticio", "Beneficio / daño y participación propuesta"],
        [
            "Actor afectado",
            "Acceso a revisión / omisión o estigma; apelación y segundo revisor",
        ],
        [
            "Operador",
            "Evidencia / sobrecarga y automatización acrítica; registrar override",
        ],
        [
            "Responsable institucional",
            "Trazabilidad / uso no autorizado; aprobar alcance o detener",
        ],
        [
            "Datos y privacidad",
            "Contratos / proxies o identificadores; auditar y bloquear",
        ],
    ],
    [130, 338],
)
e.section(2, "Riesgos y NIST AI RMF")
e.table(
    [
        ["Riesgo prioritario", "Prioridad*", "Responsable y evidencia"],
        [
            "R01: omitir positivos",
            "12",
            "Data Scientist; comparación de recall y falsos negativos",
        ],
        [
            "R02: ocultar incertidumbre interseccional",
            "12",
            "Validation Lead; conteos, soporte e intervalos",
        ],
        [
            "R06: sobrecarga por falsos positivos",
            "9",
            "Operations Lead; FPR y tasa de selección",
        ],
    ],
    [197, 52, 219],
)
e.p(
    "*Escala ordinal propuesta 1–4 de probabilidad e impacto, producto del esquema docente; no es una probabilidad observada de daño. Se documentan 12 riesgos completos y residual alto en los prioritarios. La prioridad de daño fue confirmada por el estudiante; los restantes puntajes requieren su revisión, sin aprobación institucional ficticia.",
    "small",
)
e.p(
    "GOVERN: propósito, RACI y límites. MAP: interesados y escenarios. MEASURE: auditoría y pruebas. MANAGE: puertas, apelación y rollback. El resumen identifica artefactos, sin equiparar su existencia con eficacia de controles organizativos.",
    "small",
)

e.page()
e.section(3, "Datos, corte temporal y comparación")
e.p(
    "Fixture docente de 640 casos: 353 positivos, 287 negativos; G1=396 y G2=244. Fechas inventadas de 2026, algunas futuras respecto de la entrega. Se conservan bytes y hash. Fit384 / validación96 / prueba160; los días empatados no se separan. El modelo y umbral se eligen en validación, no en prueba."
)
e.p(
    "Predictores: zona, incidentes previos, infraestructura y exposición. Se excluyen id, fecha, target, protected_group y age_band. Se corrigió que age_band aparecía en los predictores de la base. Excluir sensibles no elimina proxies; zona permanece como riesgo."
)
rows = [["Modelo / umbral", "Accuracy", "Recall", "FPR", "Selección"]]
for label, row in zip(
    ["Dummy .5", "Logística .5", "Árbol .5", "Logística .3 elegida"],
    comparison.itertuples(),
):
    rows.append(
        [
            label,
            f"{row.accuracy:.4f}",
            f"{row.recall:.4f}",
            f"{row.fpr:.4f}",
            f"{row.selection_rate:.4f}",
        ]
    )
e.table(rows, [152, 79, 79, 79, 79])
e.section(4, "Grupos e intersecciones con soporte")
rows = [
    [
        "Grupo",
        "n / positivos / negativos",
        "Recall (IC Wilson95%)",
        "FPR (IC Wilson95%)",
    ]
]
for group, row in groups.iterrows():
    rows.append(
        [
            group,
            f"{int(row['count'])} / {int(row.positive_count)} / {int(row.negative_count)}",
            f"{row.recall:.3f} [{row.recall_ci_low:.3f}, {row.recall_ci_high:.3f}]",
            f"{row.fpr:.3f} [{row.fpr_ci_low:.3f}, {row.fpr_ci_high:.3f}]",
        ]
    )
e.table(rows, [48, 132, 144, 144])
rows = [["Intersección", "n", "Pos. / neg.", "Soporte propuesto"]]
for label, row in inter.iterrows():
    rows.append(
        [
            label,
            int(row["count"]),
            f"{int(row.positive_count)} / {int(row.negative_count)}",
            "Sí" if row.supported else "Insuficiente",
        ]
    )
e.table(rows, [146, 48, 90, 184])
e.p(
    "Soporte: n>=30 y >=10 por clase, propuesta académica. Solo 1/8 cumple; no se calcula brecha robusta entre una sola intersección. Se muestra toda la evidencia, sin convertir desconocidos en cero. Wilson supone observaciones independientes, sin ajuste por múltiples comparaciones o tiempo.",
    "small",
)

e.page()
e.section(5, "Mitigación, trade-offs y Green AI")
e.p(
    "Logística .3 fue elegida en validación al priorizar recall. En prueba reduce falsos negativos de 25 a 6 entre 92 positivos, pero aumenta falsos positivos de 19 a 36 entre 68 negativos; la revisión pasa de 86 a 122 de 160 casos. No se midió capacidad real de atención. El Dummy alerta todo: recall1 y brecha0 no equivalen a justicia."
)
rows = [["Alternativa", "Fit (s)", "KiB joblib", "ms/registro*"]]
for label, row in zip(
    ["Dummy", "Logística .5", "Árbol .5", "Logística .3"], comparison.itertuples()
):
    rows.append(
        [
            label,
            f"{row.training_seconds:.5f}",
            f"{row.model_kb:.3f}",
            f"{row.latency_ms:.4f}",
        ]
    )
e.table(rows, [156, 104, 104, 104])
e.p(
    "*Tiempo batch dividido por 160, no latencia p95 de una petición. Tiempos pequeños y locales con ruido; no se midió energía ni CO2. El árbol es mayor y su brecha FPR .2548 a .5 supera .16; su complejidad no resuelve el problema. No se justifica el modelo más grande por tamaño.",
    "small",
)
e.section(6, "Decisión, límites y condición de retiro")
e.p(
    "LIMITAR al laboratorio y mantener REVIEW para despliegue. Los grupos principales con logística .3 tienen brechas recall .0085 y FPR .0433, pero la evidencia interseccional es insuficiente. Las puertas no fallan por una brecha interseccional excesiva medida, sino porque no puede estimarse con soporte suficiente. Diferencias de tasas no prueban discriminación causal."
)
e.p(
    "STOP ante identificadores, contrato inválido o uso fuera de alcance; no descartar casos por score. El simulacro deja MANUAL_ONLY. Antes de otro uso: revisar finalidad y base jurídica si hay datos personales, participación real, capacidad de revisión, soporte y etiquetas; obtener nueva prueba si se ajusta el modelo. Responsable final: Institutional Owner, rol simulado."
)
e.section(7, "Normativa, pruebas y uso de IA")
e.p(
    "Ley172-13: obligación jurídica a analizar para datos personales según alcance; este fixture no trata titulares reales. NIST AI RMF1.0 y principios OCDE: marcos de orientación, no leyes dominicanas ni fuente de tolerancias numéricas. Revisión humana, soporte y retención: propuestas éticas y políticas del laboratorio, no plazos legales. No se certifica cumplimiento por pasar tests.",
    "small",
)
e.p(
    "Pruebas ejecutadas: "
    + escape(test_summary)
    + ". Python "
    + provenance["python"]
    + ", Fairlearn "
    + provenance["fairlearn"]
    + ". Codex apoyó código y redacción; el estudiante debe revisar valores propuestos y defender conclusiones. No se inventan firmas ni participación. Fuentes y prompts: NORMATIVE_FRAMEWORK.md y AI_USE_DECLARATION.md.",
    "small",
)
e.p(
    'Referencias: <link href="https://doi.org/10.6028/NIST.AI.100-1" color="#0563c1">NIST AI RMF1.0</link>; <link href="https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0449" color="#0563c1">OCDE IA</link>; <link href="https://fairlearn.org/v0.12/user_guide/assessment/perform_fairness_assessment.html" color="#0563c1">Fairlearn</link>; <link href="https://transparencia.poderjudicial.gob.do/documentos/PDF/leyes_transparencia/LT_ley_ley_172_13_(1).pdf" color="#0563c1">Ley172-13, fuente oficial</link>.',
    "small",
)
e.save()

e = Report("08", "U04 · Gobernanza y simulacro", "LAB13 · Evidencias del Ejercicio 08")
e.section(1, "Inventario, minimización y alcance")
e.p(
    "DSS académico a partir de la base local de Unidad04. Solo organiza evidencia sintética y revisión humana; no representa territorios reales ni autoriza intervención, emergencia o elegibilidad. La decisión técnica es REVIEW; el simulacro conserva MANUAL_ONLY. No hay despliegue operativo ni datos personales de titulares reales."
)
e.table(
    [
        ["Activo", "Finalidad / minimización", "Retención y responsable"],
        [
            "Fixture de 640 casos",
            "Contrato de 9 columnas; id ficticio; sin campos adicionales",
            "Fixture académico versionado; Data Engineer",
        ],
        [
            "Sensibles ficticios",
            "G1/G2 y edad solo para auditoría; excluidos de predicción",
            "Propuesta operativa90 días; Privacy Officer",
        ],
        [
            "Recomendaciones",
            "Id ficticio, score, versión y acción humana; sin contactos",
            "Propuesta30 días; Operations Lead",
        ],
        [
            "Incidentes y evidencia",
            "Roles, señal inyectada y hashes; preservar hold",
            "Propuesta180 días; Institutional Owner",
        ],
        [
            "Modelos y política",
            "Parámetros, versiones y límites; no secretos",
            "Conservar junto a evaluación; ML Engineer",
        ],
    ],
    [116, 200, 152],
)
e.p(
    "Los plazos30/90/180 son propuestas académicas, no plazos de la Ley172-13. El dry-run distingue KEEP, HOLD y REVIEW_FOR_DELETION; no borra evidencia ni simula eliminación de datos personales reales. El fixture público sintético se conserva para reproducibilidad.",
    "small",
)
e.section(2, "Datasheet y Model Card trazables")
e.p(
    "Datos: 384 fit, 96 validación y 160 prueba. Hash del CSV "
    + provenance["data_sha256"]
    + ". Sus fechas de 2026 son inventadas, no eventos observados. DATASET_CARD explica procedencia, diccionario, exclusiones y ausencia de semilla generadora documentada; no se inventa un valor."
)
e.p(
    "MODEL_CARD conecta propósito, alternativas, elección de umbral, soporte1/8 y límites. Los hashes de datos, modelo y política impiden usar evidencia obsoleta para inferir. Modelos propios joblib, de origen confiable; no cargar archivos externos no confiables.",
    "small",
)

e.page()
e.section(3, "RACI y traspasos")
raci = pd.read_csv(ROOT / "student_inputs/raci.csv")
rows = [["Actividad", "Responsible", "Accountable único"]]
for row in raci.itertuples():
    rows.append([row.activity, row.R, row.A])
e.table(rows, [146, 190, 132])
e.p(
    "El validador exige un A y al menos un R; “;” separa roles responsables. Son roles simulados, no firmas ni aceptaciones reales. C e I se conservan en el CSV. HANDOFF.md define paquetes y criterios de aceptación: datos → ciencia → validación → responsable → operación, con devolución ante fallas."
)
e.section(4, "Puertas y límite de autoridad")
e.table(
    [
        ["Puerta", "Política", "Resultado técnico"],
        [
            "Privacidad",
            "Contrato y sin identificadores directos",
            "Pasa: rechaza name/document_number/email/phone antes de predecir",
        ],
        ["Desempeño", "Recall >=.68", "Pasa: .9348 en prueba sintética"],
        [
            "Equidad principal",
            "Brechas TPR/FPR <=.16",
            "Grupos principales pasan; no prueba justicia",
        ],
        [
            "Soporte interseccional",
            "n>=30 y >=10 por clase",
            "REVIEW: solo1/8, brechas no estimables",
        ],
        [
            "Latencia / tamaño",
            "<=500ms por registro batch / <=1024KiB",
            "Pasa; no es SLA de servicio real",
        ],
        ["Costo de entrenamiento", "<=30s, propuesta", "Pasa; sin medición de energía"],
    ],
    [117, 152, 199],
)
e.p(
    "Los límites de recall/brechas/latencia/tamaño proceden de la base; tiempo y soporte son propuestas explícitas. REVIEW no se oculta ni se transforma en GO ajustando tolerancias después de prueba. Un GO técnico solo valdría para simulación, nunca como autorización institucional.",
    "small",
)

e.page()
e.section(5, "Monitoreo y simulacro ejecutado")
e.p(
    "Monitoreo retrospectivo de exposure en ventanas sintéticas: media .50310 en validación y .51783 en prueba, diferencia .01473 frente a umbral propuesto .1. No se activa esa alerta marginal; no demuestra ausencia de deriva en otras variables, grupos o labels. Recall necesita etiquetas y puede monitorearse con demora."
)
rows = [["Etapa", "Rol y evidencia del simulacro"]]
for row in incident["events"]:
    rows.append([row["event"], row["role"] + ": " + row["action"]])
e.table(rows, [95, 373])
e.p(
    "SIM-U04-001 inyecta brecha .40, distinta de las métricas observadas. La función real de puerta devuelve REVIEW. Timestamps registran ejecución del software, no tiempos de respuesta de personas. Se preservan hashes y borrador de comunicación; no se envía ningún mensaje externo.",
    "small",
)
e.section(6, "Rollback, respuesta humana y decisión final")
e.p(
    "Rollback efectivo: MANUAL_ONLY; no se carga el predictor y la probabilidad actual es null. Todos los casos quedan en cola manual completa. La app muestra propósito, límites, grupos, puertas y autoridad; conserva score histórico como evidencia separada. Reejecutar el pipeline no reactiva silenciosamente el sistema."
)
e.p(
    "Decisión: LIMITAR al laboratorio y no utilizar operativamente. Antes de reactivar se requiere evidencia suficiente, revisión independiente y autorización humana registrada. Acciones propuestas y fecha figuran en postmortem; no se atribuyen a responsables reales aceptaciones que no ocurrieron."
)
e.section(7, "Calidad, normativa y responsabilidad")
e.p(
    "Pruebas: "
    + escape(test_summary)
    + ". Incluyen contrato, privacidad antes de cargar modelo, Fairlearn, soporte, RACI, puertas, retención dry-run, rollback y Streamlit. Git conserva la base y commits de implementación; etiqueta de entrega u04-lab13. README documenta uv, requisitos y ejecución.",
    "small",
)
e.p(
    "Ley172-13: evaluar obligaciones si se incorporan datos personales; no se certifica cumplimiento. NIST/OCDE: orientación voluntaria. Retención, revisión humana y tolerancias: propuestas del caso, sin convertirlas en normas legales. Codex apoyó código y redacción; el estudiante debe revisar y defender el expediente.",
    "small",
)
e.p(
    'Referencias: <link href="https://doi.org/10.6028/NIST.AI.100-1" color="#0563c1">NIST AI RMF</link>; Mitchell et al., <link href="https://doi.org/10.1145/3287560.3287596" color="#0563c1">Model Cards</link>; Gebru et al., <link href="https://doi.org/10.1145/3458723" color="#0563c1">Datasheets</link>; <link href="https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest" color="#0563c1">Streamlit AppTest</link>. Ver matriz normativa y declaración de IA.',
    "small",
)
e.save()
