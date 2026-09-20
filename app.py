import pandas as pd
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

NIVELES_POSTULANTE = [
    "4° medio",
    "Egresado/a de enseñanza media",
    "Primer año de educación superior",
    "Curso superior de educación superior",
    "Titulado/a",
    "Otro",
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

PUEBLOS = [
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

SALUD = [
    "No",
    "Sí, acreditada",
    "Sí, sin acreditar",
    "Revisar en el portal oficial",
]

ESTABLECIMIENTOS = [
    "Municipal / SLEP",
    "Particular subvencionado",
    "Particular pagado",
    "Administración delegada",
    "Extranjero",
    "Otro",
]


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

def option_index(options, value):
    return options.index(value) if value in options else 0


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


def clear_income_data():
    st.session_state.saved_incomes = []
    st.session_state.pdf_bytes = None

    income_keys = [
        key
        for key in list(st.session_state.keys())
        if str(key).startswith("income_")
    ]

    for key in income_keys:
        del st.session_state[key]


def format_money(value):
    return f"${value:,.0f}".replace(",", ".")


# ---------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------

st.title("🎓 Borrador FUAS 2027")

st.write(
    "Organiza tus antecedentes antes de completar "
    "la postulación oficial."
)

st.warning(
    "**DOCUMENTO NO OFICIAL:** esta herramienta no realiza una "
    "postulación, no reemplaza a fuas.cl y no genera un "
    "comprobante del Ministerio de Educación."
)

st.info(
    "**Privacidad:** los datos permanecen solamente durante esta "
    "sesión. La aplicación no utiliza una base de datos."
)


# ---------------------------------------------------------
# 1. ESTUDIANTE
# ---------------------------------------------------------

st.header("1. Antecedentes del estudiante")

saved = st.session_state.student or {}

with st.form(
    "student_form",
    clear_on_submit=False,
    enter_to_submit=False,
):
    col1, col2, col3, col4 = st.columns(4)

    nombre = col1.text_input(
        "Nombre completo *",
        value=saved.get("nombre", ""),
    )

    cedula = col2.text_input(
        "Cédula de identidad *",
        value=saved.get("cedula", ""),
        placeholder="12.345.678-5",
    )

    edad = col3.number_input(
        "Edad *",
        min_value=14,
        max_value=120,
        value=int(saved.get("edad", 18)),
        step=1,
    )

    estado_civil = col4.selectbox(
        "Estado civil",
        ESTADOS_CIVILES,
        index=option_index(
            ESTADOS_CIVILES,
            saved.get("estado_civil", "Soltero/a"),
        ),
    )

    col1, col2, col3 = st.columns(3)

    nacionalidad = col1.selectbox(
        "Nacionalidad",
        ["Chilena", "Extranjera"],
        index=option_index(
            ["Chilena", "Extranjera"],
            saved.get("nacionalidad", "Chilena"),
        ),
    )

    pueblo = col2.selectbox(
        "Pueblo originario",
        PUEBLOS,
        index=option_index(
            PUEBLOS,
            saved.get("pueblo", "No pertenece"),
        ),
    )

    salud = col3.selectbox(
        "Condición de salud o discapacidad",
        SALUD,
        index=option_index(
            SALUD,
            saved.get("salud", "No"),
        ),
    )

    col1, col2, col3 = st.columns(3)

    nivel = col1.selectbox(
        "Nivel de estudio",
        NIVELES_POSTULANTE,
        index=option_index(
            NIVELES_POSTULANTE,
            saved.get("nivel", "4° medio"),
        ),
    )

    actividad = col2.selectbox(
        "Actividad",
        ACTIVIDADES,
        index=option_index(
            ACTIVIDADES,
            saved.get("actividad", "Estudiante"),
        ),
    )

    correo = col3.text_input(
        "Correo electrónico *",
        value=saved.get("correo", ""),
    )

    col1, col2 = st.columns(2)

    celular = col1.text_input(
        "Celular",
        value=saved.get("celular", ""),
    )

    direccion = col2.text_input(
        "Dirección del grupo familiar",
        value=saved.get("direccion", ""),
    )

    col1, col2 = st.columns(2)

    comuna = col1.text_input(
        "Comuna",
        value=saved.get("comuna", ""),
    )

    region = col2.selectbox(
        "Región",
        REGIONES,
        index=option_index(
            REGIONES,
            saved.get("region", "Metropolitana"),
        ),
    )

    st.subheader("Antecedentes académicos")

    col1, col2, col3 = st.columns(3)

    tipo_establecimiento = col1.selectbox(
        "Tipo de establecimiento de egreso",
        ESTABLECIMIENTOS,
        index=option_index(
            ESTABLECIMIENTOS,
            saved.get(
                "tipo_establecimiento",
                "Municipal / SLEP",
            ),
        ),
    )

    nem = col2.number_input(
        "Promedio NEM",
        min_value=1.0,
        max_value=7.0,
        value=float(saved.get("nem", 5.0)),
        step=0.1,
    )

    media_chile = col3.radio(
        "¿Cursaste los cuatro niveles de enseñanza media en Chile?",
        ["Sí", "No"],
        index=option_index(
            ["Sí", "No"],
            saved.get("media_chile", "Sí"),
        ),
        horizontal=True,
    )

    col1, col2, col3 = st.columns(3)

    institucion = col1.text_input(
        "Institución de educación superior",
        value=saved.get("institucion", ""),
    )

    ultimo_ano = col2.number_input(
        "Último año de matrícula",
        min_value=0,
        max_value=2027,
        value=int(saved.get("ultimo_ano", 0)),
        step=1,
        help="Usa 0 si no corresponde.",
    )

    cuenta_ahorro = col3.radio(
        "¿Cuenta de ahorro para educación superior?",
        ["No", "Sí"],
        index=option_index(
            ["No", "Sí"],
            saved.get("cuenta_ahorro", "No"),
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
            clear_income_data()

        st.session_state.student = new_student
        st.rerun()


if st.session_state.student is None:
    st.info(
        "Completa y guarda primero los antecedentes del estudiante."
    )
    st.stop()


student = st.session_state.student


# ---------------------------------------------------------
# 2. GRUPO FAMILIAR
# ---------------------------------------------------------

st.header("2. Integrantes del grupo familiar")

st.info(
    "**El postulante aparece automáticamente como integrante 1.** "
    "Agrega solamente a las demás personas del grupo familiar."
)

family = [
    student_as_member(student),
    *st.session_state.family_members,
]

family_table = pd.DataFrame(family)

family_table.insert(
    0,
    "N.º",
    range(1, len(family_table) + 1),
)

st.dataframe(
    family_table,
    hide_index=True,
    use_container_width=True,
)

st.subheader("Agregar otro integrante")

with st.form(
    "family_form",
    clear_on_submit=True,
    enter_to_submit=False,
):
    col1, col2, col3 = st.columns(3)

    member_name = col1.text_input(
        "Nombre completo *",
        key="new_member_name",
    )

    member_cedula = col2.text_input(
        "Cédula de identidad",
        placeholder="12.345.678-5",
        key="new_member_cedula",
    )

    member_age = col3.number_input(
        "Edad",
        min_value=0,
        max_value=120,
        value=18,
        step=1,
        key="new_member_age",
    )

    col1, col2, col3, col4 = st.columns(4)

    member_status = col1.selectbox(
        "Estado civil",
        ESTADOS_CIVILES,
        key="new_member_status",
    )

    member_relation = col2.selectbox(
        "Parentesco",
        PARENTESCOS,
        key="new_member_relation",
    )

    member_activity = col3.selectbox(
        "Actividad",
        ACTIVIDADES,
        key="new_member_activity",
    )

    member_studies = col4.selectbox(
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
            "La cédula de identidad ingresada no es válida."
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

        clear_income_data()
        st.rerun()


if st.session_state.family_members:
    st.subheader("Eliminar un integrante")

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

        clear_income_data()
        st.rerun()


family = [
    student_as_member(student),
    *st.session_state.family_members,
]


# ---------------------------------------------------------
# 3. INGRESOS
# ---------------------------------------------------------

st.header("3. Ingresos del grupo familiar")

st.info(
    "**El postulante aparece automáticamente en primer lugar.** "
    "Ingresa el promedio mensual correspondiente a cada año."
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
                st.subheader(f"Promedio mensual {year}")

                saved_row = next(
                    (
                        row
                        for row in st.session_state.saved_incomes
                        if row["Nombre"] == member_name
                        and row["Año"] == year
                    ),
                    {},
                )

                columns = st.columns(3)
                values = {}

                for income_index, income_type in enumerate(
                    INCOME_TYPES
                ):
                    values[income_type] = columns[
                        income_index % 3
                    ].number_input(
                        income_type,
                        min_value=0,
                        value=int(
                            saved_row.get(income_type, 0)
                        ),
                        step=1000,
                        key=(
                            f"income_{member_index}_"
                            f"{year}_{income_index}"
                        ),
                    )

                total = sum(values.values())

                st.metric(
                    f"Total mensual {year}",
                    format_money(total),
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

st.header("4. Revisión y descarga")

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

    col1, col2, col3 = st.columns(3)

    col1.metric("Integrantes", len(family))
    col2.metric("Ingreso mensual 2025", format_money(total_2025))
    col3.metric("Ingreso mensual 2026", format_money(total_2026))

    accepted = st.checkbox(
        "Confirmo que revisaré estos antecedentes y los validaré "
        "en el portal oficial."
    )

    prepare_pdf = st.button(
        "Preparar PDF",
        type="primary",
        use_container_width=True,
    )

    if prepare_pdf:
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


st.warning(
    "**IMPORTANTE:** este PDF es solamente un borrador de apoyo. "
    "La postulación y el comprobante válido se obtienen "
    "exclusivamente en fuas.cl."
)
