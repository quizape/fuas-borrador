from io import BytesIO
from html import escape

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
    table = Table(rows, colWidths=widths, repeatRows=1)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, LIGHT_BLUE],
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
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
        fontSize=11,
        spaceBefore=8,
        spaceAfter=5,
    )

    note_style = ParagraphStyle(
        "FUASNote",
        parent=styles["Normal"],
        textColor=GRAY,
        fontSize=8,
        leading=11,
    )

    story = [
        Paragraph("BORRADOR DE ANTECEDENTES FUAS", title_style),
        Paragraph(
            "DOCUMENTO NO OFICIAL — NO CONSTITUYE POSTULACIÓN "
            "NI COMPROBANTE DEL MINEDUC",
            note_style,
        ),
        Spacer(1, 6 * mm),
    ]

    postulante = data["postulante"]

    story.append(
        Paragraph(
            "1. Antecedentes de la persona postulante",
            section_style,
        )
    )

    personal_rows = [
        ["Nombre completo", "RUT", "Estado civil"],
        [
            safe_text(postulante.get("nombre")),
            safe_text(postulante.get("rut")),
            safe_text(postulante.get("estado_civil")),
        ],
        ["Nacionalidad", "Pueblo originario", "Salud o discapacidad"],
        [
            safe_text(postulante.get("nacionalidad")),
            safe_text(postulante.get("pueblo")),
            safe_text(postulante.get("salud")),
        ],
        ["Nivel de estudio", "Actividad", "Correo electrónico"],
        [
            safe_text(postulante.get("nivel")),
            safe_text(postulante.get("actividad")),
            safe_text(postulante.get("correo")),
        ],
        ["Celular", "Dirección", "Comuna y región"],
        [
            safe_text(postulante.get("celular")),
            safe_text(postulante.get("direccion")),
            (
                f"{safe_text(postulante.get('comuna'))} / "
                f"{safe_text(postulante.get('region'))}"
            ),
        ],
    ]

    story.append(
        create_table(
            personal_rows,
            widths=[87 * mm, 87 * mm, 87 * mm],
            font_size=8,
        )
    )

    academicos = data["academicos"]

    story.append(Paragraph("2. Antecedentes académicos", section_style))

    academic_rows = [
        [
            "Establecimiento de egreso",
            "Promedio NEM",
            "Enseñanza media cursada en Chile",
        ],
        [
            safe_text(academicos.get("tipo_establecimiento")),
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

    story.append(Paragraph("3. Grupo familiar", section_style))

    family_rows = [
        [
            "RUT",
            "Nombre completo",
            "Edad",
            "Estado civil",
            "Parentesco",
            "Actividad",
            "Nivel de estudios",
        ]
    ]

    for member in data.get("familia", []):
        family_rows.append(
            [
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
        family_rows.append(["—"] * 7)

    story.append(
        create_table(
            family_rows,
            widths=[
                31 * mm,
                48 * mm,
                16 * mm,
                33 * mm,
                35 * mm,
                43 * mm,
                55 * mm,
            ],
            font_size=7,
        )
    )

    story.append(PageBreak())
    story.append(
        Paragraph(
            "4. Promedio mensual de ingresos del grupo familiar",
            section_style,
        )
    )

    income_types = data["income_types"]

    income_rows = [
        ["Integrante", "Año"] + income_types + ["Total mensual"]
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

    income_widths = (
        [32 * mm, 12 * mm]
        + [20 * mm] * len(income_types)
        + [24 * mm]
    )

    story.append(
        create_table(
            income_rows,
            widths=income_widths,
            font_size=5.5,
        )
    )

    years = data["years"]

    story.extend(
        [
            Spacer(1, 6 * mm),
            Paragraph(
                f"Los montos corresponden a promedios mensuales de "
                f"{years[0]} y {years[1]}. Confirma estos años y los "
                f"criterios en el instructivo FUAS 2027 definitivo.",
                note_style,
            ),
            Spacer(1, 3 * mm),
            Paragraph(
                "Este archivo se genera durante la sesión. Debes realizar "
                "y finalizar la postulación exclusivamente en fuas.cl para "
                "obtener un comprobante válido.",
                note_style,
            ),
        ]
    )

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
