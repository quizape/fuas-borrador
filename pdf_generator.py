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
DARK = colors.HexColor("#172B3A")
YELLOW = colors.HexColor("#FFF4CC")


def safe_text(value):
    if value in (None, ""):
        return "—"

    return escape(str(value))


def money(value):
    try:
        return f"${float(value):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "$0"


def create_table(
    rows,
    widths=None,
    font_size=6.5,
    header_rows=1,
    padding=2.5,
):
    table = Table(
        rows,
        colWidths=widths,
        repeatRows=header_rows,
        hAlign="LEFT",
    )

    style = [
        (
            "BACKGROUND",
            (0, 0),
            (-1, header_rows - 1),
            BLUE,
        ),
        (
            "TEXTCOLOR",
            (0, 0),
            (-1, header_rows - 1),
            colors.white,
        ),
        (
            "FONTNAME",
            (0, 0),
            (-1, header_rows - 1),
            "Helvetica-Bold",
        ),
        (
            "TEXTCOLOR",
            (0, header_rows),
            (-1, -1),
            DARK,
        ),
        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            font_size,
        ),
        (
            "LEADING",
            (0, 0),
            (-1, -1),
            font_size + 1.2,
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.3,
            colors.HexColor("#AAB7C2"),
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "MIDDLE",
        ),
        (
            "ROWBACKGROUNDS",
            (0, header_rows),
            (-1, -1),
            [colors.white, LIGHT_BLUE],
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            padding,
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            padding,
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            padding,
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            padding,
        ),
    ]

    table.setStyle(TableStyle(style))

    return table


def draw_page(canvas, document):
    canvas.saveState()

    page_width, _ = landscape(A4)

    canvas.setStrokeColor(colors.HexColor("#C7D2DC"))
    canvas.setLineWidth(0.4)

    canvas.line(
        8 * mm,
        7 * mm,
        page_width - 8 * mm,
        7 * mm,
    )

    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(GRAY)

    canvas.drawString(
        8 * mm,
        3.8 * mm,
        "Borrador FUAS 2027 — Colegio Superior del Maipo",
    )

    canvas.drawRightString(
        page_width - 8 * mm,
        3.8 * mm,
        f"Página {document.page}",
    )

    canvas.restoreState()


def build_pdf(data):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=8 * mm,
        leftMargin=8 * mm,
        topMargin=7 * mm,
        bottomMargin=10 * mm,
        title="Borrador FUAS 2027",
        author="peqz",
        allowSplitting=1,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCompact",
        parent=styles["Title"],
        textColor=BLUE,
        fontSize=14,
        leading=16,
        spaceAfter=2,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleCompact",
        parent=styles["Normal"],
        textColor=DARK,
        fontSize=7.5,
        leading=9,
        alignment=1,
        spaceAfter=3,
    )

    section_style = ParagraphStyle(
        "SectionCompact",
        parent=styles["Heading2"],
        textColor=BLUE,
        fontSize=9,
        leading=10,
        spaceBefore=3,
        spaceAfter=2,
    )

    note_style = ParagraphStyle(
        "NoteCompact",
        parent=styles["Normal"],
        textColor=GRAY,
        fontSize=6.5,
        leading=8,
        spaceAfter=2,
    )

    warning_style = ParagraphStyle(
        "WarningCompact",
        parent=styles["Normal"],
        textColor=colors.HexColor("#6A4300"),
        backColor=YELLOW,
        borderColor=colors.HexColor("#E3A008"),
        borderWidth=0.6,
        borderPadding=4,
        fontSize=7,
        leading=8.5,
        spaceBefore=2,
        spaceAfter=3,
    )

    story = [
        Paragraph(
            "BORRADOR FUAS 2027",
            title_style,
        ),
        Paragraph(
            "Uso exclusivo Colegio Superior del Maipo",
            subtitle_style,
        ),
        Paragraph(
            "<b>DESCARGO DE RESPONSABILIDAD:</b> esta herramienta "
            "no realiza una postulación, no reemplaza a fuas.cl y "
            "no genera un comprobante del Ministerio de Educación.",
            warning_style,
        ),
    ]

    # =====================================================
    # PÁGINA 1
    # =====================================================

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
            "Nacionalidad",
        ],
        [
            safe_text(postulante.get("nombre")),
            safe_text(postulante.get("rut")),
            safe_text(postulante.get("estado_civil")),
            safe_text(postulante.get("nacionalidad")),
        ],
        [
            "Pueblo originario",
            "Nivel de estudio",
            "Actividad",
            "Correo electrónico",
        ],
        [
            safe_text(postulante.get("pueblo")),
            safe_text(postulante.get("nivel")),
            safe_text(postulante.get("actividad")),
            safe_text(postulante.get("correo")),
        ],
        [
            "Celular",
            "Dirección",
            "Comuna",
            "Región",
        ],
        [
            safe_text(postulante.get("celular")),
            safe_text(postulante.get("direccion")),
            safe_text(postulante.get("comuna")),
            safe_text(postulante.get("region")),
        ],
    ]

    story.append(
        create_table(
            personal_rows,
            widths=[
                70 * mm,
                68 * mm,
                68 * mm,
                70 * mm,
            ],
            font_size=6.7,
        )
    )

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
            "Enseñanza media en Chile",
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
            widths=[
                92 * mm,
                92 * mm,
                92 * mm,
            ],
            font_size=6.7,
        )
    )

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
                9 * mm,
                27 * mm,
                46 * mm,
                12 * mm,
                29 * mm,
                31 * mm,
                48 * mm,
                74 * mm,
            ],
            font_size=5.8,
            padding=2,
        )
    )

    story.append(
        Paragraph(
            "4. Antecedentes de salud",
            section_style,
        )
    )

    health_records = data.get("salud", [])

    health_rows = [
        [
            "Persona",
            "Parentesco",
            "Condición prolongada",
            "Discapacidad",
            "Condición / duración",
            "Tratamiento",
            "Gasto mensual",
            "Observaciones",
        ]
    ]

    for record in health_records:
        condition_detail = "—"

        if (
            record.get("tipo_condicion")
            or record.get("duracion")
        ):
            condition_detail = (
                f"{safe_text(record.get('tipo_condicion'))} / "
                f"{safe_text(record.get('duracion'))}"
            )

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
                condition_detail,
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
                "Sin antecedentes registrados",
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
                40 * mm,
                28 * mm,
                27 * mm,
                25 * mm,
                48 * mm,
                27 * mm,
                28 * mm,
                53 * mm,
            ],
            font_size=5.7,
            padding=2,
        )
    )

    story.append(
        Paragraph(
            "La información de salud es preparatoria. Debe "
            "confirmarse en el formulario oficial.",
            note_style,
        )
    )

    # =====================================================
    # PÁGINA 2
    # =====================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "5. Promedio mensual de ingresos del grupo familiar",
            section_style,
        )
    )

    income_types = data.get("income_types", [])

    income_rows = [
        [
            "Integrante",
            "Año",
            *income_types,
            "Total",
        ]
    ]

    for income_row in data.get("ingresos", []):
        income_rows.append(
            [
                safe_text(income_row.get("Nombre")),
                safe_text(income_row.get("Año")),
                *[
                    money(income_row.get(income_type, 0))
                    for income_type in income_types
                ],
                money(income_row.get("Total", 0)),
            ]
        )

    if len(income_rows) == 1:
        income_rows.append(
            [
                "Sin ingresos registrados",
                "—",
                *(["$0"] * len(income_types)),
                "$0",
            ]
        )

    page_width = 276 * mm
    name_width = 35 * mm
    year_width = 12 * mm
    total_width = 21 * mm

    remaining_width = (
        page_width
        - name_width
        - year_width
        - total_width
    )

    category_width = (
        remaining_width / max(len(income_types), 1)
    )

    story.append(
        create_table(
            income_rows,
            widths=[
                name_width,
                year_width,
                *(
                    [category_width]
                    * len(income_types)
                ),
                total_width,
            ],
            font_size=5.1,
            padding=1.7,
        )
    )

    years = data.get("years", [])

    if len(years) >= 2:
        years_text = f"{years[0]} y {years[1]}"
    else:
        years_text = "los años solicitados"

    story.extend(
        [
            Spacer(1, 3 * mm),
            Paragraph(
                f"Los montos corresponden a promedios mensuales "
                f"de {years_text}. Confirma los periodos y métodos "
                f"de cálculo en el instructivo FUAS 2027.",
                note_style,
            ),
            Spacer(1, 2 * mm),
            Paragraph(
                "<b>IMPORTANTE:</b> este PDF es solamente un "
                "borrador de apoyo. La postulación y el comprobante "
                "válido se obtienen exclusivamente en fuas.cl.",
                warning_style,
            ),
            Spacer(1, 2 * mm),
            Paragraph(
                "App desarrollada por peqz",
                note_style,
            ),
        ]
    )

    document.build(
        story,
        onFirstPage=draw_page,
        onLaterPages=draw_page,
    )

    result = buffer.getvalue()
    buffer.close()

    return result
