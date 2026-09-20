from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BLUE = colors.HexColor("#0B5CAD")
LIGHT_BLUE = colors.HexColor("#EAF2F8")
GRAY = colors.HexColor("#5E6D78")


def safe_text(value):
    if value in (None, ""):
        return "—"

    return escape(str(value))


def money(value):
    try:
        amount = float(value)
        return f"${amount:,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "$0"


def create_table(rows, widths=None, font_size=7):
    table = Table(
        rows,
        colWidths=widths,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    BLUE,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    font_size,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#AAB7C2"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, LIGHT_BLUE],
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return table


def build_pdf(data):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Borrador de antecedentes FUAS",
        author="Aplicación Borrador FUAS",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "FUASTitle",
        parent=styles["Title"],
        textColor=BLUE,
        fontSize=18,
        leading=22,
    )

    section_style = ParagraphStyle(
        "FUASSection",
        parent=styles["Heading2"],
        textColor=BLUE,
        fontSize=12,
        leading=15,
        spaceBefore=9,
        spaceAfter=6,
    )

    note_style = ParagraphStyle(
        "FUASNote",
        parent=styles["Normal"],
        textColor=GRAY,
        fontSize=8,
        leading=11,
    )

    warning_style = ParagraphStyle(
        "FUASWarning",
        parent=styles["Normal"],
        textColor=colors.HexColor("#7A4B00"),
        backColor=colors.HexColor("#FFF4CC"),
        borderColor=colors.HexColor("#E3A008"),
        borderWidth=1,
        borderPadding=8,
        fontSize=9,
        leading=12,
        spaceAfter=8,
    )

    story = [
        Paragraph(
            "BORRADOR DE ANTECEDENTES FUAS",
            title_style,
        ),
        Paragraph(
            "<b>DOCUMENTO NO OFICIAL:</b> no constituye una "
            "postulación ni un comprobante del Ministerio de Educación.",
            warning_style,
        ),
        Spacer(1, 3 * mm),
    ]

    # -----------------------------------------------------
    # 1. POSTULANTE
    # -----------------------------------------------------

    postulante = data.get("postulante", {})

    story.append(
        Paragraph(
            "1. Antecedentes de la persona postulante",
            section_style,
        )
    )

    personal_rows = [
        [
            "Nombre completo",
            "Cédula de identidad",
            "Estado civil",
        ],
        [
            safe_text(postulante.get("nombre")),
            safe_text(postulante.get("rut")),
            safe_text(postulante.get("estado_civil")),
        ],
        [
            "Nacionalidad",
            "Pueblo originario",
            "Nivel de estudio",
        ],
        [
            safe_text(postulante.get("nacionalidad")),
            safe_text(postulante.get("pueblo")),
            safe_text(postulante.get("nivel")),
        ],
        [
            "Actividad",
            "Correo electrónico",
            "Celular",
        ],
        [
            safe_text(postulante.get("actividad")),
            safe_text(postulante.get("correo")),
            safe_text(postulante.get("celular")),
        ],
        [
            "Dirección",
            "Comuna",
            "Región",
        ],
        [
            safe_text(postulante.get("direccion")),
            safe_text(postulante.get("comuna")),
            safe_text(postulante.get("region")),
        ],
    ]

    story.append(
        create_table(
            personal_rows,
            widths=[87 * mm, 87 * mm, 87 * mm],
            font_size=8,
        )
    )

    # -----------------------------------------------------
    # 2. ANTECEDENTES ACADÉMICOS
    # -----------------------------------------------------

    academicos = data.get("academicos", {})

    story.append(
        Paragraph(
            "2. Antecedentes académicos",
            section_style,
        )
    )

    academic_rows = [
        [
            "Establecimiento de egreso",
            "Promedio NEM",
            "Enseñanza media cursada en Chile",
        ],
        [
            safe_text(
                academicos.get("tipo_establecimiento")
            ),
            safe_text(academicos.get("nem")),
            safe_text(academicos.get("media_chile")),
        ],
        [
            "Institución de educación superior",
            "Último año de matrícula",
            "Cuenta de ahorro para educación",
        ],
        [
            safe_text(academicos.get("institucion")),
            safe_text(academicos.get("ultimo_ano")),
            safe_text(academicos.get("cuenta_ahorro")),
        ],
    ]

    story.append(
        create_table(
            academic_rows,
            widths=[87 * mm, 87 * mm, 87 * mm],
            font_size=8,
        )
    )

    # -----------------------------------------------------
    # 3. GRUPO FAMILIAR
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "3. Integrantes del grupo familiar",
            section_style,
        )
    )

    family_rows = [
        [
            "N.º",
            "Cédula",
            "Nombre completo",
            "Edad",
            "Estado civil",
            "Parentesco",
            "Actividad",
            "Nivel de estudios",
        ]
    ]

    for number, member in enumerate(
        data.get("familia", []),
        start=1,
    ):
        family_rows.append(
            [
                number,
                safe_text(member.get("RUT")),
                safe_text(member.get("Nombre completo")),
                safe_text(member.get("Edad")),
                safe_text(member.get("Estado civil")),
                safe_text(member.get("Parentesco")),
                safe_text(member.get("Actividad")),
                safe_text(member.get("Nivel de estudios")),
            ]
        )

    if len(family_rows) == 1:
        family_rows.append(["—"] * 8)

    story.append(
        create_table(
            family_rows,
            widths=[
                10 * mm,
                27 * mm,
                43 * mm,
                13 * mm,
                28 * mm,
                31 * mm,
                48 * mm,
                61 * mm,
            ],
            font_size=6.5,
        )
    )

    # -----------------------------------------------------
    # 4. SALUD
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "4. Encuesta preparatoria de condición de salud",
            section_style,
        )
    )

    story.append(
        Paragraph(
            "Esta sección es únicamente una ayuda para organizar "
            "antecedentes. Las preguntas y documentos exigidos deben "
            "confirmarse en el portal oficial.",
            note_style,
        )
    )

    story.append(Spacer(1, 2 * mm))

    health_records = data.get("salud", [])

    health_rows = [
        [
            "Persona",
            "Parentesco",
            "Condición prolongada",
            "Discapacidad",
            "Tipo de condición",
            "Duración",
            "Tratamiento",
            "Gasto mensual",
            "Observaciones",
        ]
    ]

    for record in health_records:
        gasto = "No"

        if record.get("gastos_mensuales") == "Sí":
            gasto = money(record.get("monto_gasto", 0))

        health_rows.append(
            [
                safe_text(record.get("persona")),
                safe_text(record.get("parentesco")),
                safe_text(
                    record.get("condicion_larga_duracion")
                ),
                safe_text(record.get("discapacidad")),
                safe_text(record.get("tipo_condicion")),
                safe_text(record.get("duracion")),
                safe_text(
                    record.get("tratamiento_permanente")
                ),
                gasto,
                safe_text(record.get("observaciones")),
            ]
        )

    if len(health_rows) == 1:
        health_rows.append(
            [
                "Sin respuestas registradas",
                "—",
                "—",
                "—",
                "—",
                "—",
                "—",
                "—",
                "—",
            ]
        )

    story.append(
        create_table(
            health_rows,
            widths=[
                35 * mm,
                25 * mm,
                25 * mm,
                22 * mm,
                35 * mm,
                22 * mm,
                23 * mm,
                25 * mm,
                49 * mm,
            ],
            font_size=6,
        )
    )

    # -----------------------------------------------------
    # 5. INGRESOS
    # -----------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "5. Promedio mensual de ingresos del grupo familiar",
            section_style,
        )
    )

    income_types = data.get("income_types", [])
    income_rows = [
        ["Integrante", "Año"]
        + income_types
        + ["Total mensual"]
    ]

    for income_row in data.get("ingresos", []):
        income_rows.append(
            [
                safe_text(income_row.get("Nombre")),
                safe_text(income_row.get("Año")),
            ]
            + [
                money(income_row.get(income_type, 0))
                for income_type in income_types
            ]
            + [money(income_row.get("Total", 0))]
        )

    if len(income_rows) == 1:
        income_rows.append(
            ["Sin ingresos registrados", "—"]
            + ["$0"] * len(income_types)
            + ["$0"]
        )

    available_width = 273 * mm
    fixed_width = 56 * mm
    variable_width = (
        available_width - fixed_width
    ) / max(len(income_types), 1)

    income_widths = (
        [32 * mm, 12 * mm]
        + [variable_width] * len(income_types)
        + [12 * mm]
    )

    story.append(
        create_table(
            income_rows,
            widths=income_widths,
            font_size=5.2,
        )
    )

    years = data.get("years", [])

    if len(years) >= 2:
        years_text = f"{years[0]} y {years[1]}"
    else:
        years_text = "los años solicitados"

    story.extend(
        [
            Spacer(1, 6 * mm),
            Paragraph(
                f"Los montos corresponden a promedios mensuales de "
                f"{years_text}. Confirma los periodos y criterios en "
                f"el instructivo FUAS 2027 definitivo.",
                note_style,
            ),
            Spacer(1, 4 * mm),
            Paragraph(
                "<b>IMPORTANTE:</b> este archivo es solamente un "
                "borrador de apoyo. Debes realizar y finalizar la "
                "postulación exclusivamente en fuas.cl para obtener "
                "un comprobante válido.",
                warning_style,
            ),
        ]
    )

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
