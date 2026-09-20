import html

import streamlit as st

from pdf_generator import build_pdf
from validators import format_rut, valid_rut


st.set_page_config(
    page_title="Borrador FUAS 2027",
    page_icon="🎓",
    layout="wide",
)

INCOME_YEARS = [2025, 2026]

INCOME_TYPES = [
    "Sueldos",
    "Pensiones",
    "Honorarios",
    "Retiros",
    "Dividendos",
    "Intereses",
    "Ganancias de capital",
    "Pensión alimenticia/aportes",
    "Actividades independientes",
]

ESTADOS_CIVILES = [
    "Soltero/a",
    "Casado/a",
    "Divorciado/a",
    "Viudo/a",
    "Conviviente civil",
    "Otro",
]

ACTIVIDADES = [
    "Estudiante",
    "Trabajador/a dependiente",
    "Trabajador/a independiente",
    "Cesante",
    "Dueño/a de casa",
    "Jubilado/a",
    "Otra",
]

NIVELES_ESTUDIO = [
    "Sin estudios",
    "Educación básica incompleta",
    "Educación básica completa",
    "Enseñanza media incompleta",
    "Enseñanza media completa",
    "Educación superior incompleta",
    "Educación superior completa",
    "Postgrado",
]

PARENTESCOS = [
    "Madre",
    "Padre",
    "Hermano/a",
    "Cónyuge o pareja",
    "Hijo/a",
    "Abuelo/a",
    "Otro familiar",
    "No familiar",
]

REGIONES = [
    "Arica y Parinacota",
    "Tarapacá",
    "Antofagasta",
    "Atacama",
    "Coquimbo",
    "Valparaíso",
    "Metropolitana",
    "O'Higgins",
    "Maule",
    "Ñuble",
    "Biobío",
    "La Araucanía",
    "Los Ríos",
    "Los Lagos",
    "Aysén",
    "Magallanes",
]


# ---------------------------------------------------------
# ESTILOS
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
    }

    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 14px;
        color: #FFFFFF !important;
        background: linear-gradient(110deg, #063b6f, #0b75c9);
        margin-bottom: 1rem;
    }

    .hero h1,
    .hero p {
        color: #FFFFFF !important;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.1rem;
    }

    .hero p {
        margin: 0.4rem 0 0;
        font-size: 1.1rem;
    }

    .disclaimer {
        border-left: 6px solid #E3A008;
        background-color: #FFF8DF !important;
        color: #172B3A !important;
        padding: 1rem 1.1rem;
        border-radius: 7px;
        margin: 1rem 0;
        font-size: 1.15rem;
        font-weight: 700;
        line-height: 1.5;
    }

    .family-container {
        width: 100%;
        overflow-x: auto;
        margin: 0.8rem 0 1.2rem;
    }

    .member-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #FFFFFF !important;
    }

    .member-table th {
        background-color: #0B5CAD !important;
        color: #FFFFFF !important;
        padding: 10px;
        border: 1px solid #0A4D91;
        text-align: left;
        font-size: 0.9rem;
        white-space: nowrap;
    }

    .member-table td {
        background-color: #FFFFFF !important;
        color: #172B3A !important;
        padding: 10px;
        border: 1px solid #C7D2DC;
        font-size: 0.9rem;
    }

    .member-table tbody tr:nth-child(even) td {
        background-color: #EAF2F8 !important;
        color: #172B3A !important;
    }

    .member-table tbody tr:nth-child(odd) td {
        background-color: #FFFFFF !important;
        color: #172B3A !important;
    }

    .member-table tbody tr td * {
        color: #172B3A !important;
    }

    [data-testid="stMetricValue"] {
        color: #0B5CAD;
    }
    </style>

    <div class="hero" translate="no">
        <h1>Borrador FUAS 2027</h1>
        <p>
            Organiza tus antecedentes antes de completar
            la postulación oficial.
        </p>
    </div>

    <div class="disclaimer" translate="no">
        DOCUMENTO NO OFICIAL: esta herramienta no realiza una
        postulación, no reemplaza a fuas.cl y no genera un
        comprobante del Ministerio de Educación.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Privacidad: los datos permanecen solamente durante esta sesión. "
    "La aplicación no utiliza una base de datos."
)


# ---------------------------------------------------------
# ESTADO
# ---------------------------------------------------------

if "student" not in st.session_state:
    st.session_state.student = None

if "family_members" not in st.session_state:
    st.session_state.family_members = []

if "saved_incomes" not in st.session_state:
    st.session_state.saved_incomes = []

if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None


# ---------------------------------------------------------
# FUNCIONES
# ---------------------------------------------------------

def option_index(options, selected):
    if selected in options:
        return options.index(selected)
    return 0


def clear_income_state():
    st.session_state.saved_incomes = []
    st.session_state.pdf_bytes = None

    keys_to_delete = [
        key
        for key in st.session_state.keys()
        if str(key).startswith("income_")
    ]

    for key in keys_to_delete:
        del st.session_state[key]


def student_as_member(student):
    return {
        "RUT": student["cedula"],
        "Nombre completo": student["nombre"],
        "Edad": student["edad"],
        "Estado civil": student["estado_civil"],
        "Parentesco": "Postulante",
        "Actividad": student["actividad"],
        "Nivel de estudios": student["nivel"],
    }


def show_family_table(members):
    rows = ""

    for position, member in enumerate(members, start=1):
        values = [
            position,
            member["Nombre completo"],
            member["RUT"] or "—",
            member["Edad"],
            member["Estado civil"],
            member["Parentesco"],
            member["Actividad"],
            member["Nivel de estudios"],
        ]

        cells = "".join(
            f"<td>{html.escape(str(value))}</td>"
            for value in values
        )

        rows += f"<tr>{cells}</tr>"

    st.markdown(
        f"""
        <div class="family-container" translate="no">
            <table class="member-table">
                <thead>
                    <tr>
                        <th>N.º</th>
                        <th>Nombre completo</th>
                        <th>Cédula de identidad</th>
                        <th>Edad</th>
                        <th>Estado civil</th>
                        <th>Parentesco</th>
                        <th>Actividad</th>
                        <th>Nivel de estudios</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# 1. ESTUDIANTE
# ---------------------------------------------------------

st.subheader("1. Antecedentes del estudiante")

saved_student = st.session_state.student or {}

with st.form(
    "student_form",
    clear_on_submit=False,
    enter_to_submit=False,
):
    column1, column2, column3, column4 = st.columns(4)

    nombre = column1.text_input(
        "Nombre completo *",
        value=saved_student.get("nombre", ""),
    )

    cedula = column2.text_input(
        "Cédula de identidad *",
        value=saved_student.get("cedula", ""),
        placeholder="12.345.678-5",
    )

    edad = column3.number_input(
        "Edad *",
        min_value=14,
        max_value=120,
        value=int(saved_student.get("edad", 18)),
        step=1,
    )

    estado_civil = column4.selectbox(
        "Estado civil",
        ESTADOS_CIVILES,
        index=option_index(
            ESTADOS_CIVILES,
            saved_student.get("estado_civil", "Soltero/a"),
        ),
    )

    column1, column2, column3 = st.columns(3)

    nacionalidad = column1.selectbox(
        "Nacionalidad",
        ["Chilena", "Extranjera"],
        index=option_index(
            ["Chilena", "Extranjera"],
            saved_student.get("nacionalidad", "Chilena"),
        ),
    )

    pueblo_options = [
        "No pertenece",
        "Mapuche",
        "Aymara",
        "Rapa Nui",
        "Lickanantay",
        "Quechua",
        "Colla",
        "Diaguita",
        "Kawésqar",
        "Yagán",
        "Chango",
        "Selk'nam",
        "Otro",
    ]

    pueblo = column2.selectbox(
        "Pueblo originario",
        pueblo_options,
        index=option_index(
            pueblo_options,
            saved_student.get("pueblo", "No pertenece"),
        ),
    )

    salud_options = [
        "No",
        "Sí, acreditada",
        "Sí, sin acreditar",
        "Revisar en el portal oficial",
    ]

    salud = column3.selectbox(
        "Condición de salud o discapacidad",
        salud_options,
        index=option_index(
            salud_options,
            saved_student.get("salud", "No"),
        ),
    )

    column1, column2, column3 = st.columns(3)

    nivel_options = [
        "4° medio",
        "Egresado/a de enseñanza media",
        "Primer año de educación superior",
        "Curso superior de educación superior",
        "Titulado/a",
        "Otro",
    ]

    nivel = column1.selectbox(
        "Nivel de estudio",
        nivel_options,
        index=option_index(
            nivel_options,
            saved_student.get("nivel", "4° medio"),
        ),
    )

    actividad = column2.selectbox(
        "Actividad",
        ACTIVIDADES,
        index=option_index(
            ACTIVIDADES,
            saved_student.get("actividad", "Estudiante"),
        ),
    )

    correo = column3.text_input(
        "Correo electrónico *",
        value=saved_student.get("correo", ""),
    )

    column1, column2 = st.columns(2)

    celular = column1.text_input(
        "Celular",
        value=saved_student.get("celular", ""),
    )

    direccion = column2.text_input(
        "Dirección del grupo familiar",
        value=saved_student.get("direccion", ""),
    )

    column1, column2 = st.columns(2)

    comuna = column1.text_input(
        "Comuna",
        value=saved_student.get("comuna", ""),
    )

    region = column2.selectbox(
        "Región",
        REGIONES,
        index=option_index(
            REGIONES,
            saved_student.get("region", "Metropolitana"),
        ),
    )

    st.markdown("#### Antecedentes académicos")

    column1, column2, column3 = st.columns(3)

    establishment_options = [
        "Municipal / SLEP",
        "Particular subvencionado",
        "Particular pagado",
        "Administración delegada",
        "Extranjero",
        "Otro",
    ]

    tipo_establecimiento = column1.selectbox(
        "Tipo de establecimiento de egreso",
        establishment_options,
        index=option_index(
            establishment_options,
            saved_student.get(
                "tipo_establecimiento",
                "Municipal / SLEP",
            ),
        ),
    )

    nem = column2.number_input(
        "Promedio NEM",
        min_value=1.0,
        max_value=7.0,
        value=float(saved_student.get("nem", 5.0)),
        step=0.1,
    )

    media_chile = column3.radio(
        "¿Cursaste los cuatro niveles de enseñanza media en Chile?",
        ["Sí", "No"],
        index=option_index(
            ["Sí", "No"],
            saved_student.get("media_chile", "Sí"),
        ),
        horizontal=True,
    )

    column1, column2, column3 = st.columns(3)

    institucion = column1.text_input(
        "Institución de educación superior",
        value=saved_student.get("institucion", ""),
    )

    ultimo_ano = column2.number_input(
        "Último año de matrícula",
        min_value=0,
        max_value=2027,
        value=int(saved_student.get("ultimo_ano", 0)),
        step=1,
        help="Usa 0 si no corresponde.",
    )

    cuenta_ahorro = column3.radio(
        "¿Cuenta de ahorro para educación superior?",
        ["No", "Sí"],
        index=option_index(
            ["No", "Sí"],
            saved_student.get("cuenta_ahorro", "No"),
        ),
        horizontal=True,
    )

    save_student = st.form_submit_button(
        "Guardar estudiante y continuar",
        type="primary",
        use_container_width=True,
    )


if save_student:
    errors = []

    if not nombre.strip():
        errors.append("Falta el nombre completo.")

    if not valid_rut(cedula):
        errors.append(
            "La cédula de identidad ingresada no es válida."
        )

    if "@" not in correo or "." not in correo.split("@")[-1]:
        errors.append(
            "El correo electrónico no parece válido."
        )

    if errors:
        for error in errors:
            st.error(error)

    else:
        new_student = {
            "nombre": nombre.strip(),
            "cedula": format_rut(cedula),
            "edad": int(edad),
            "estado_civil": estado_civil,
            "nacionalidad": nacionalidad,
            "pueblo": pueblo,
            "salud": salud,
            "nivel": nivel,
            "actividad": actividad,
            "correo": correo.strip(),
            "celular": celular.strip(),
            "direccion": direccion.strip(),
            "comuna": comuna.strip(),
            "region": region,
            "tipo_establecimiento": tipo_establecimiento,
            "nem": float(nem),
            "media_chile": media_chile,
            "institucion": institucion.strip(),
            "ultimo_ano": int(ultimo_ano),
            "cuenta_ahorro": cuenta_ahorro,
        }

        if st.session_state.student != new_student:
            clear_income_state()

        st.session_state.student = new_student
        st.success("Datos del estudiante guardados correctamente.")
        st.rerun()


if st.session_state.student is None:
    st.info(
        "Completa y guarda los antecedentes del estudiante "
        "para continuar."
    )
    st.stop()


student = st.session_state.student


# ---------------------------------------------------------
# 2. GRUPO FAMILIAR
# ---------------------------------------------------------

st.subheader("2. Integrantes del grupo familiar")

st.info(
    "El postulante se incorpora automáticamente como integrante 1. "
    "Agrega solamente a las demás personas del grupo familiar."
)

family = [
    student_as_member(student),
    *st.session_state.family_members,
]

# Siempre muestra al postulante como primera fila.
show_family_table(family)

st.markdown("#### Agregar otro integrante")

with st.form(
    "add_family_member_form",
    clear_on_submit=True,
    enter_to_submit=False,
):
    column1, column2, column3 = st.columns(3)

    member_name = column1.text_input(
        "Nombre completo *",
        key="new_member_name",
    )

    member_cedula = column2.text_input(
        "Cédula de identidad",
        placeholder="12.345.678-5",
        key="new_member_cedula",
    )

    member_age = column3.number_input(
        "Edad",
        min_value=0,
        max_value=120,
        value=18,
        step=1,
        key="new_member_age",
    )

    column1, column2, column3, column4 = st.columns(4)

    member_status = column1.selectbox(
        "Estado civil",
        ESTADOS_CIVILES,
        key="new_member_status",
    )

    member_relation = column2.selectbox(
        "Parentesco",
        PARENTESCOS,
        key="new_member_relation",
    )

    member_activity = column3.selectbox(
        "Actividad",
        ACTIVIDADES,
        key="new_member_activity",
    )

    member_studies = column4.selectbox(
        "Nivel de estudios",
        NIVELES_ESTUDIO,
        key="new_member_studies",
    )

    add_member = st.form_submit_button(
        "Agregar integrante",
        type="primary",
        use_container_width=True,
    )


if add_member:
    errors = []

    if not member_name.strip():
        errors.append(
            "Debes escribir el nombre del integrante."
        )

    if member_cedula and not valid_rut(member_cedula):
        errors.append(
            "La cédula de identidad del integrante no es válida."
        )

    if errors:
        for error in errors:
            st.error(error)

    else:
        st.session_state.family_members.append(
            {
                "RUT": (
                    format_rut(member_cedula)
                    if member_cedula
                    else ""
                ),
                "Nombre completo": member_name.strip(),
                "Edad": int(member_age),
                "Estado civil": member_status,
                "Parentesco": member_relation,
                "Actividad": member_activity,
                "Nivel de estudios": member_studies,
            }
        )

        clear_income_state()
        st.rerun()


if st.session_state.family_members:
    st.markdown("#### Eliminar un integrante")

    delete_options = {
        (
            f"{index + 2}. "
            f"{member['Nombre completo']} — "
            f"{member['Parentesco']}"
        ): index
        for index, member
        in enumerate(st.session_state.family_members)
    }

    selected_member = st.selectbox(
        "Selecciona el integrante",
        list(delete_options.keys()),
    )

    if st.button("Eliminar integrante"):
        selected_index = delete_options[selected_member]
        st.session_state.family_members.pop(selected_index)
        clear_income_state()
        st.rerun()


family = [
    student_as_member(student),
    *st.session_state.family_members,
]


# ---------------------------------------------------------
# 3. INGRESOS
# ---------------------------------------------------------

st.subheader("3. Ingresos del grupo familiar")

st.info(
    "El postulante aparece automáticamente en primer lugar. "
    "Ingresa el promedio mensual solicitado para cada año."
)

with st.form(
    "income_form",
    clear_on_submit=False,
    enter_to_submit=False,
):
    income_rows = []

    for member_index, member in enumerate(family):
        member_name = member["Nombre completo"]
        relation = member["Parentesco"]

        with st.expander(
            f"{member_index + 1}. {member_name} — {relation}",
            expanded=(member_index == 0),
        ):
            for year in INCOME_YEARS:
                st.markdown(f"#### Promedio mensual {year}")

                columns = st.columns(3)
                values = {}

                saved_row = next(
                    (
                        row
                        for row in st.session_state.saved_incomes
                        if row["Nombre"] == member_name
                        and row["Año"] == year
                    ),
                    {},
                )

                for income_index, income_type in enumerate(
                    INCOME_TYPES
                ):
                    values[income_type] = columns[
                        income_index % 3
                    ].number_input(
                        income_type,
                        min_value=0,
                        value=int(saved_row.get(income_type, 0)),
                        step=1000,
                        key=(
                            f"income_{member_index}_"
                            f"{year}_{income_index}"
                        ),
                    )

                total = sum(values.values())

                st.caption(
                    f"Total mensual {year}: "
                    f"${total:,.0f}".replace(",", ".")
                )

                income_rows.append(
                    {
                        "Nombre": member_name,
                        "Año": year,
                        **values,
                        "Total": total,
                    }
                )

    save_incomes = st.form_submit_button(
        "Guardar ingresos",
        type="primary",
        use_container_width=True,
    )


if save_incomes:
    st.session_state.saved_incomes = income_rows
    st.session_state.pdf_bytes = None
    st.success("Ingresos guardados correctamente.")


# ---------------------------------------------------------
# 4. PDF
# ---------------------------------------------------------

st.subheader("4. Revisión y descarga")

if not st.session_state.saved_incomes:
    st.warning(
        "Guarda primero los ingresos para preparar el PDF."
    )

else:
    total_2025 = sum(
        row["Total"]
        for row in st.session_state.saved_incomes
        if row["Año"] == 2025
    )

    total_2026 = sum(
        row["Total"]
        for row in st.session_state.saved_incomes
        if row["Año"] == 2026
    )

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Integrantes", len(family))

    metric2.metric(
        "Ingreso mensual 2025",
        f"${total_2025:,.0f}".replace(",", "."),
    )

    metric3.metric(
        "Ingreso mensual 2026",
        f"${total_2026:,.0f}".replace(",", "."),
    )

    accepted = st.checkbox(
        "Confirmo que revisaré estos antecedentes y los validaré "
        "en el portal oficial."
    )

    if st.button(
        "Preparar PDF",
        type="primary",
        use_container_width=True,
    ):
        if not accepted:
            st.error(
                "Debes confirmar la revisión antes de generar el PDF."
            )

        else:
            pdf_data = {
                "postulante": {
                    "nombre": student["nombre"],
                    "rut": student["cedula"],
                    "estado_civil": student["estado_civil"],
                    "nacionalidad": student["nacionalidad"],
                    "pueblo": student["pueblo"],
                    "salud": student["salud"],
                    "nivel": student["nivel"],
                    "actividad": student["actividad"],
                    "correo": student["correo"],
                    "celular": student["celular"],
                    "direccion": student["direccion"],
                    "comuna": student["comuna"],
                    "region": student["region"],
                },
                "academicos": {
                    "tipo_establecimiento": (
                        student["tipo_establecimiento"]
                    ),
                    "nem": student["nem"],
                    "media_chile": student["media_chile"],
                    "institucion": student["institucion"],
                    "ultimo_ano": (
                        student["ultimo_ano"]
                        if student["ultimo_ano"] != 0
                        else "No aplica"
                    ),
                    "cuenta_ahorro": student["cuenta_ahorro"],
                },
                "familia": family,
                "ingresos": st.session_state.saved_incomes,
                "income_types": INCOME_TYPES,
                "years": INCOME_YEARS,
            }

            st.session_state.pdf_bytes = build_pdf(pdf_data)
            st.success("PDF preparado correctamente.")

    if st.session_state.pdf_bytes:
        st.download_button(
            "Descargar borrador PDF",
            data=st.session_state.pdf_bytes,
            file_name="borrador_fuas_2027_no_oficial.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )


st.markdown(
    """
    <div class="disclaimer" translate="no">
        IMPORTANTE: este PDF es solamente un borrador de apoyo.
        La postulación y el comprobante válido se obtienen
        exclusivamente en fuas.cl.
    </div>
    """,
    unsafe_allow_html=True,
)
