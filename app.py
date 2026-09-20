import pandas as pd
import streamlit as st

from pdf_generator import build_pdf
from validators import format_rut, valid_rut


st.set_page_config(
    page_title="Borrador FUAS 2027",
    page_icon="🎓",
    layout="wide",
)

YEARS = [2025, 2026]

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

NIVELES_FAMILIA = [
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

ESTABLECIMIENTOS = [
    "Municipal / SLEP",
    "Particular subvencionado",
    "Particular pagado",
    "Administración delegada",
    "Extranjero",
    "Otro",
]


# ---------------------------------------------------------
# ESTADO DE LA APLICACIÓN
# ---------------------------------------------------------

DEFAULTS = {
    "student": None,
    "family_members": [],
    "health_records": {},
    "saved_incomes": [],
    "pdf_bytes": None,
    "next_member_id": 1,
}

for key, default in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------
# FUNCIONES
# ---------------------------------------------------------

def option_index(options, value):
    return options.index(value) if value in options else 0


def money(value):
    return f"${value:,.0f}".replace(",", ".")


def footer():
    st.divider()
    st.caption("App desarrollada por peqz")


def student_as_member(student):
    return {
        "ID": "postulante",
        "RUT": student["cedula"],
        "Nombre completo": student["nombre"],
        "Edad": student["edad"],
        "Estado civil": student["estado_civil"],
        "Parentesco": "Postulante",
        "Actividad": student["actividad"],
        "Nivel de estudios": student["nivel"],
    }


def current_family():
    if st.session_state.student is None:
        return []

    return [
        student_as_member(st.session_state.student),
        *st.session_state.family_members,
    ]


def clear_derived_data():
    st.session_state.saved_incomes = []
    st.session_state.pdf_bytes = None

    for key in list(st.session_state.keys()):
        if str(key).startswith("income_"):
            del st.session_state[key]


def default_health_record():
    return {
        "condicion_larga_duracion": "No",
        "discapacidad": "No",
        "tipo_condicion": "",
        "duracion": "",
        "tratamiento_permanente": "No",
        "gastos_mensuales": "No",
        "monto_gasto": 0,
        "observaciones": "",
    }


# ---------------------------------------------------------
# ENCABEZADO Y DESCARGO
# ---------------------------------------------------------

st.title(
    "🎓 Borrador FUAS 2027 — "
    "Uso exclusivo Colegio Superior del Maipo"
)

st.write(
    "Organiza tus antecedentes antes de completar "
    "la postulación oficial."
)

st.warning(
    "### Descargo de responsabilidad\n\n"
    "Esta aplicación es una herramienta informativa y de apoyo. "
    "No realiza una postulación oficial, no representa al "
    "Ministerio de Educación y no reemplaza el proceso disponible "
    "en fuas.cl."
)

accepted_terms = st.checkbox(
    "Entiendo y acepto que esta herramienta no realiza una "
    "postulación, no reemplaza a fuas.cl y no genera un "
    "comprobante del Ministerio de Educación.",
    key="accepted_terms",
)

if not accepted_terms:
    st.info(
        "El formulario permanecerá bloqueado hasta aceptar "
        "el descargo de responsabilidad."
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
        disabled=not accepted_terms,
    )

    cedula = col2.text_input(
        "Cédula de identidad *",
        value=saved.get("cedula", ""),
        placeholder="12.345.678-5",
        disabled=not accepted_terms,
    )

    edad = col3.number_input(
        "Edad *",
        min_value=14,
        max_value=120,
        value=int(saved.get("edad", 18)),
        step=1,
        disabled=not accepted_terms,
    )

    estado_civil = col4.selectbox(
        "Estado civil",
        ESTADOS_CIVILES,
        index=option_index(
            ESTADOS_CIVILES,
            saved.get("estado_civil", "Soltero/a"),
        ),
        disabled=not accepted_terms,
    )

    col1, col2, col3 = st.columns(3)

    nacionalidad = col1.selectbox(
        "Nacionalidad",
        ["Chilena", "Extranjera"],
        index=option_index(
            ["Chilena", "Extranjera"],
            saved.get("nacionalidad", "Chilena"),
        ),
        disabled=not accepted_terms,
    )

    pueblo = col2.selectbox(
        "Pueblo originario",
        PUEBLOS,
        index=option_index(
            PUEBLOS,
            saved.get("pueblo", "No pertenece"),
        ),
        disabled=not accepted_terms,
    )

    nivel = col3.selectbox(
        "Nivel de estudio",
        NIVELES_POSTULANTE,
        index=option_index(
            NIVELES_POSTULANTE,
            saved.get("nivel", "4° medio"),
        ),
        disabled=not accepted_terms,
    )

    col1, col2, col3 = st.columns(3)

    actividad = col1.selectbox(
        "Actividad",
        ACTIVIDADES,
        index=option_index(
            ACTIVIDADES,
            saved.get("actividad", "Estudiante"),
        ),
        disabled=not accepted_terms,
    )

    correo = col2.text_input(
        "Correo electrónico *",
        value=saved.get("correo", ""),
        disabled=not accepted_terms,
    )

    celular = col3.text_input(
        "Celular",
        value=saved.get("celular", ""),
        disabled=not accepted_terms,
    )

    col1, col2, col3 = st.columns(3)

    direccion = col1.text_input(
        "Dirección del grupo familiar",
        value=saved.get("direccion", ""),
        disabled=not accepted_terms,
    )

    comuna = col2.text_input(
        "Comuna",
        value=saved.get("comuna", ""),
        disabled=not accepted_terms,
    )

    region = col3.selectbox(
        "Región",
        REGIONES,
        index=option_index(
            REGIONES,
            saved.get("region", "Metropolitana"),
        ),
        disabled=not accepted_terms,
    )

    st.subheader("Antecedentes académicos")

    col1, col2, col3 = st.columns(3)

    establecimiento = col1.selectbox(
        "Tipo de establecimiento de egreso",
        ESTABLECIMIENTOS,
        index=option_index(
            ESTABLECIMIENTOS,
            saved.get("establecimiento", "Municipal / SLEP"),
        ),
        disabled=not accepted_terms,
    )

    nem = col2.number_input(
        "Promedio NEM",
        min_value=1.0,
        max_value=7.0,
        value=float(saved.get("nem", 5.0)),
        step=0.1,
        disabled=not accepted_terms,
    )

    media_chile = col3.radio(
        "¿Cursaste los cuatro niveles de enseñanza media en Chile?",
        ["Sí", "No"],
        index=option_index(
            ["Sí", "No"],
            saved.get("media_chile", "Sí"),
        ),
        horizontal=True,
        disabled=not accepted_terms,
    )

    col1, col2, col3 = st.columns(3)

    institucion = col1.text_input(
        "Institución de educación superior",
        value=saved.get("institucion", ""),
        disabled=not accepted_terms,
    )

    ultimo_ano = col2.number_input(
        "Último año de matrícula",
        min_value=0,
        max_value=2027,
        value=int(saved.get("ultimo_ano", 0)),
        step=1,
        help="Usa 0 si no corresponde.",
        disabled=not accepted_terms,
    )

    cuenta_ahorro = col3.radio(
        "¿Cuenta de ahorro para educación superior?",
        ["No", "Sí"],
        index=option_index(
            ["No", "Sí"],
            saved.get("cuenta_ahorro", "No"),
        ),
        horizontal=True,
        disabled=not accepted_terms,
    )

    save_student = st.form_submit_button(
        "Guardar estudiante y continuar",
        type="primary",
        use_container_width=True,
        disabled=not accepted_terms,
    )


if not accepted_terms:
    footer()
    st.stop()


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
            "nivel": nivel,
            "actividad": actividad,
            "correo": correo.strip(),
            "celular": celular.strip(),
            "direccion": direccion.strip(),
            "comuna": comuna.strip(),
            "region": region,
            "establecimiento": establecimiento,
            "nem": float(nem),
            "media_chile": media_chile,
            "institucion": institucion.strip(),
            "ultimo_ano": int(ultimo_ano),
            "cuenta_ahorro": cuenta_ahorro,
        }

        if st.session_state.student != new_student:
            clear_derived_data()

        st.session_state.student = new_student
        st.rerun()


if st.session_state.student is None:
    st.info(
        "Completa y guarda primero los antecedentes del estudiante."
    )
    footer()
    st.stop()


# ---------------------------------------------------------
# 2. GRUPO FAMILIAR
# ---------------------------------------------------------

st.header("2. Integrantes del grupo familiar")

st.info(
    "**El postulante aparece automáticamente como integrante 1.** "
    "Agrega solamente a las demás personas del grupo familiar."
)

family = current_family()

table_rows = []

for number, member in enumerate(family, start=1):
    table_rows.append(
        {
            "N.º": number,
            "Nombre completo": member["Nombre completo"],
            "Cédula de identidad": member["RUT"],
            "Edad": member["Edad"],
            "Estado civil": member["Estado civil"],
            "Parentesco": member["Parentesco"],
            "Actividad": member["Actividad"],
            "Nivel de estudios": member["Nivel de estudios"],
        }
    )

st.dataframe(
    pd.DataFrame(table_rows),
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
        NIVELES_FAMILIA,
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
        member_id = (
            f"familiar_{st.session_state.next_member_id}"
        )

        st.session_state.next_member_id += 1

        st.session_state.family_members.append(
            {
                "ID": member_id,
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

        clear_derived_data()
        st.rerun()


if st.session_state.family_members:
    delete_options = {
        (
            f"{index + 2}. "
            f"{member['Nombre completo']} — "
            f"{member['Parentesco']}"
        ): index
        for index, member in enumerate(
            st.session_state.family_members
        )
    }

    selected_delete = st.selectbox(
        "Eliminar integrante",
        ["No eliminar"] + list(delete_options.keys()),
    )

    if (
        selected_delete != "No eliminar"
        and st.button("Confirmar eliminación")
    ):
        index = delete_options[selected_delete]
        removed = st.session_state.family_members.pop(index)

        st.session_state.health_records.pop(
            removed["ID"],
            None,
        )

        clear_derived_data()
        st.rerun()


# ---------------------------------------------------------
# 3. SALUD
# ---------------------------------------------------------

st.header("3. Encuesta de condición de salud")

st.info(
    "Completa esta sección para cada integrante. "
    "Verifica las preguntas definitivas en el portal oficial."
)

family = current_family()

person_options = {
    (
        f"{number}. {member['Nombre completo']} — "
        f"{member['Parentesco']}"
    ): member
    for number, member in enumerate(family, start=1)
}

selected_label = st.selectbox(
    "Persona a evaluar",
    list(person_options.keys()),
)

selected_person = person_options[selected_label]
selected_id = selected_person["ID"]

saved_health = st.session_state.health_records.get(
    selected_id,
    default_health_record(),
)

condition = st.radio(
    "¿Tiene una condición de salud de larga duración?",
    ["No", "Sí"],
    index=option_index(
        ["No", "Sí"],
        saved_health["condicion_larga_duracion"],
    ),
    horizontal=True,
    key=f"condition_{selected_id}",
)

disability = st.radio(
    "¿Tiene discapacidad acreditada?",
    ["No", "Sí", "En trámite"],
    index=option_index(
        ["No", "Sí", "En trámite"],
        saved_health["discapacidad"],
    ),
    horizontal=True,
    key=f"disability_{selected_id}",
)

if condition == "Sí":
    with st.form(
        f"health_form_{selected_id}",
        clear_on_submit=False,
        enter_to_submit=False,
    ):
        col1, col2 = st.columns(2)

        tipo_condicion = col1.text_input(
            "Tipo de condición *",
            value=saved_health["tipo_condicion"],
        )

        duracion = col2.text_input(
            "Duración aproximada *",
            value=saved_health["duracion"],
        )

        col1, col2 = st.columns(2)

        tratamiento = col1.radio(
            "¿Requiere tratamiento permanente?",
            ["No", "Sí"],
            index=option_index(
                ["No", "Sí"],
                saved_health["tratamiento_permanente"],
            ),
            horizontal=True,
        )

        gastos = col2.radio(
            "¿Genera gastos mensuales?",
            ["No", "Sí"],
            index=option_index(
                ["No", "Sí"],
                saved_health["gastos_mensuales"],
            ),
            horizontal=True,
        )

        monto = st.number_input(
            "Gasto mensual estimado",
            min_value=0,
            value=int(saved_health["monto_gasto"]),
            step=1000,
            disabled=(gastos == "No"),
        )

        observaciones = st.text_area(
            "Observaciones opcionales",
            value=saved_health["observaciones"],
        )

        save_health = st.form_submit_button(
            "Guardar antecedentes de salud",
            type="primary",
            use_container_width=True,
        )

    if save_health:
        if not tipo_condicion.strip() or not duracion.strip():
            st.error(
                "Debes indicar el tipo y la duración de la condición."
            )
        else:
            st.session_state.health_records[selected_id] = {
                "persona": selected_person["Nombre completo"],
                "parentesco": selected_person["Parentesco"],
                "condicion_larga_duracion": "Sí",
                "discapacidad": disability,
                "tipo_condicion": tipo_condicion.strip(),
                "duracion": duracion.strip(),
                "tratamiento_permanente": tratamiento,
                "gastos_mensuales": gastos,
                "monto_gasto": (
                    int(monto) if gastos == "Sí" else 0
                ),
                "observaciones": observaciones.strip(),
            }

            st.session_state.pdf_bytes = None
            st.success("Antecedentes de salud guardados.")

else:
    if st.button(
        "Guardar respuesta de salud",
        use_container_width=True,
    ):
        st.session_state.health_records[selected_id] = {
            "persona": selected_person["Nombre completo"],
            "parentesco": selected_person["Parentesco"],
            "condicion_larga_duracion": "No",
            "discapacidad": disability,
            "tipo_condicion": "",
            "duracion": "",
            "tratamiento_permanente": "No",
            "gastos_mensuales": "No",
            "monto_gasto": 0,
            "observaciones": "",
        }

        st.session_state.pdf_bytes = None
        st.success("Respuesta de salud guardada.")


# ---------------------------------------------------------
# 4. INGRESOS
# ---------------------------------------------------------

st.header("4. Ingresos del grupo familiar")

st.info(
    "**El postulante aparece automáticamente en primer lugar.** "
    "Ingresa el promedio mensual correspondiente a cada año."
)

family = current_family()

with st.form(
    "income_form",
    clear_on_submit=False,
    enter_to_submit=False,
):
    income_rows = []

    for member_index, member in enumerate(family):
        with st.expander(
            f"{member_index + 1}. "
            f"{member['Nombre completo']} — "
            f"{member['Parentesco']}",
            expanded=(member_index == 0),
        ):
            for year in YEARS:
                st.subheader(f"Promedio mensual {year}")

                saved_row = next(
                    (
                        row
                        for row in st.session_state.saved_incomes
                        if row["ID"] == member["ID"]
                        and row["Año"] == year
                    ),
                    {},
                )

                columns = st.columns(3)
                values = {}

                for index, income_type in enumerate(INCOME_TYPES):
                    values[income_type] = columns[
                        index % 3
                    ].number_input(
                        income_type,
                        min_value=0,
                        value=int(
                            saved_row.get(income_type, 0)
                        ),
                        step=1000,
                        key=(
                            f"income_{member['ID']}_"
                            f"{year}_{index}"
                        ),
                    )

                total = sum(values.values())

                st.metric(
                    f"Total mensual {year}",
                    money(total),
                )

                income_rows.append(
                    {
                        "ID": member["ID"],
                        "Nombre": member["Nombre completo"],
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
# 5. PDF
# ---------------------------------------------------------

st.header("5. Revisión y descarga")

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
    col2.metric("Ingreso mensual 2025", money(total_2025))
    col3.metric("Ingreso mensual 2026", money(total_2026))

    accepted_review = st.checkbox(
        "Confirmo que revisaré estos antecedentes y los validaré "
        "en el portal oficial."
    )

    if st.button(
        "Preparar PDF",
        type="primary",
        use_container_width=True,
    ):
        if not accepted_review:
            st.error(
                "Debes confirmar la revisión antes de generar el PDF."
            )
        else:
            student = st.session_state.student

            pdf_data = {
                "postulante": {
                    "nombre": student["nombre"],
                    "rut": student["cedula"],
                    "estado_civil": student["estado_civil"],
                    "nacionalidad": student["nacionalidad"],
                    "pueblo": student["pueblo"],
                    "nivel": student["nivel"],
                    "actividad": student["actividad"],
                    "correo": student["correo"],
                    "celular": student["celular"],
                    "direccion": student["direccion"],
                    "comuna": student["comuna"],
                    "region": student["region"],
                },
                "academicos": {
                    "tipo_establecimiento": student[
                        "establecimiento"
                    ],
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
                "salud": list(
                    st.session_state.health_records.values()
                ),
                "ingresos": st.session_state.saved_incomes,
                "income_types": INCOME_TYPES,
                "years": YEARS,
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

footer()
