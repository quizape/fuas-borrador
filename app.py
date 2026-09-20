import pandas as pd
import streamlit as st

from pdf_generator import build_pdf
from validators import format_rut, nonnegative_number, valid_rut


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
        color: white;
        background: linear-gradient(110deg, #063b6f, #0b75c9);
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2rem;
    }

    .hero p {
        margin: 0.4rem 0 0;
        opacity: 0.95;
    }

    .warning {
        border-left: 5px solid #e3a008;
        background: #fff8df;
        padding: 0.9rem 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }

    [data-testid="stMetricValue"] {
        color: #0B5CAD;
    }
    </style>

    <div class="hero">
        <h1>Borrador FUAS 2027</h1>
        <p>
            Organiza tus antecedentes antes de completar
            la postulación oficial.
        </p>
    </div>

    <div class="warning">
        <b>Documento no oficial.</b>
        Esta herramienta no realiza una postulación,
        no reemplaza a fuas.cl y no genera un comprobante Mineduc.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Privacidad: los datos permanecen solamente durante esta sesión. "
    "La aplicación no utiliza una base de datos."
)


# ---------------------------------------------------------
# 1. DATOS DEL ESTUDIANTE
# ---------------------------------------------------------

st.subheader("1. Antecedentes del estudiante")

column1, column2, column3, column4 = st.columns(4)

nombre = column1.text_input(
    "Nombre completo *",
    key="nombre_estudiante",
)

rut = column2.text_input(
    "RUT *",
    placeholder="12.345.678-5",
    key="rut_estudiante",
)

edad = column3.number_input(
    "Edad *",
    min_value=14,
    max_value=120,
    value=18,
    step=1,
    key="edad_estudiante",
)

estado_civil = column4.selectbox(
    "Estado civil",
    ESTADOS_CIVILES,
    key="estado_estudiante",
)

column1, column2, column3 = st.columns(3)

nacionalidad = column1.selectbox(
    "Nacionalidad",
    ["Chilena", "Extranjera"],
)

pueblo = column2.selectbox(
    "Pueblo originario",
    [
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
    ],
)

salud = column3.selectbox(
    "Condición de salud o discapacidad",
    [
        "No",
        "Sí, acreditada",
        "Sí, sin acreditar",
        "Revisar en el portal oficial",
    ],
)

column1, column2, column3 = st.columns(3)

nivel = column1.selectbox(
    "Nivel de estudio",
    [
        "4° medio",
        "Egresado/a de enseñanza media",
        "Primer año de educación superior",
        "Curso superior de educación superior",
        "Titulado/a",
        "Otro",
    ],
)

actividad = column2.selectbox(
    "Actividad",
    ACTIVIDADES,
    key="actividad_estudiante",
)

correo = column3.text_input("Correo electrónico *")

column1, column2 = st.columns(2)

celular = column1.text_input("Celular")
direccion = column2.text_input("Dirección del grupo familiar")

column1, column2 = st.columns(2)

comuna = column1.text_input("Comuna")

region = column2.selectbox(
    "Región",
    [
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
    ],
)


# ---------------------------------------------------------
# 2. DATOS ACADÉMICOS
# ---------------------------------------------------------

st.subheader("2. Antecedentes académicos")

column1, column2, column3 = st.columns(3)

tipo_establecimiento = column1.selectbox(
    "Tipo de establecimiento de egreso",
    [
        "Municipal / SLEP",
        "Particular subvencionado",
        "Particular pagado",
        "Administración delegada",
        "Extranjero",
        "Otro",
    ],
)

nem = column2.number_input(
    "Promedio NEM",
    min_value=1.0,
    max_value=7.0,
    value=5.0,
    step=0.1,
)

media_chile = column3.radio(
    "¿Cursaste los cuatro niveles de enseñanza media en Chile?",
    ["Sí", "No"],
    horizontal=True,
)

column1, column2, column3 = st.columns(3)

institucion = column1.text_input(
    "Institución de educación superior, si corresponde"
)

ultimo_ano = column2.number_input(
    "Último año de matrícula",
    min_value=0,
    max_value=2027,
    value=0,
    step=1,
    help="Usa 0 si no corresponde.",
)

cuenta_ahorro = column3.radio(
    "¿Cuenta de ahorro para educación superior?",
    ["No", "Sí"],
    horizontal=True,
)


# ---------------------------------------------------------
# 3. GRUPO FAMILIAR
# ---------------------------------------------------------

st.subheader("3. Integrantes del grupo familiar")

st.info(
    "El estudiante se incorpora automáticamente como primer integrante. "
    "Agrega solamente a las demás personas que comparten ingresos y gastos."
)

nombre_mostrado = nombre.strip() or "Estudiante"

with st.expander(
    f"Integrante 1: {nombre_mostrado} — Estudiante",
    expanded=True,
):
    column1, column2, column3, column4 = st.columns(4)

    column1.text_input(
        "Nombre completo",
        value=nombre,
        disabled=True,
        key="resumen_nombre_estudiante",
    )

    column2.text_input(
        "RUT",
        value=format_rut(rut) if rut else "",
        disabled=True,
        key="resumen_rut_estudiante",
    )

    column3.number_input(
        "Edad",
        value=int(edad),
        disabled=True,
        key="resumen_edad_estudiante",
    )

    column4.text_input(
        "Parentesco",
        value="Postulante",
        disabled=True,
        key="resumen_parentesco_estudiante",
    )

cantidad_adicional = st.number_input(
    "¿Cuántos integrantes adicionales tiene el grupo familiar?",
    min_value=0,
    max_value=15,
    value=0,
    step=1,
)

familia = [
    {
        "RUT": format_rut(rut) if rut else "",
        "Nombre completo": nombre.strip(),
        "Edad": int(edad),
        "Estado civil": estado_civil,
        "Parentesco": "Postulante",
        "Actividad": actividad,
        "Nivel de estudios": nivel,
    }
]

for index in range(int(cantidad_adicional)):
    number = index + 2

    with st.expander(
        f"Integrante {number}",
        expanded=True,
    ):
        column1, column2, column3 = st.columns(3)

        member_name = column1.text_input(
            "Nombre completo *",
            key=f"member_name_{index}",
        )

        member_rut = column2.text_input(
            "RUT",
            key=f"member_rut_{index}",
            placeholder="12.345.678-5",
        )

        member_age = column3.number_input(
            "Edad",
            min_value=0,
            max_value=120,
            value=18,
            step=1,
            key=f"member_age_{index}",
        )

        column1, column2, column3, column4 = st.columns(4)

        member_status = column1.selectbox(
            "Estado civil",
            ESTADOS_CIVILES,
            key=f"member_status_{index}",
        )

        member_relation = column2.selectbox(
            "Parentesco",
            PARENTESCOS,
            key=f"member_relation_{index}",
        )

        member_activity = column3.selectbox(
            "Actividad",
            ACTIVIDADES,
            key=f"member_activity_{index}",
        )

        member_studies = column4.selectbox(
            "Nivel de estudios",
            NIVELES_ESTUDIO,
            key=f"member_studies_{index}",
        )

        familia.append(
            {
                "RUT": (
                    format_rut(member_rut)
                    if member_rut
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


# ---------------------------------------------------------
# 4. INGRESOS
# ---------------------------------------------------------

st.subheader("4. Ingresos del grupo familiar")

st.info(
    "El estudiante aparece automáticamente primero. "
    "Ingresa directamente el promedio mensual solicitado para cada año."
)

ingresos = []

for member_index, member in enumerate(familia):
    member_name = (
        member["Nombre completo"]
        or f"Integrante {member_index + 1}"
    )

    relation = member["Parentesco"]

    with st.expander(
        f"{member_index + 1}. {member_name} — {relation}",
        expanded=(member_index == 0),
    ):
        for year in INCOME_YEARS:
            st.markdown(f"#### Ingresos mensuales {year}")

            values = {}
            columns = st.columns(3)

            for income_index, income_type in enumerate(INCOME_TYPES):
                selected_column = columns[income_index % 3]

                values[income_type] = selected_column.number_input(
                    income_type,
                    min_value=0,
                    value=0,
                    step=1000,
                    key=(
                        f"income_{member_index}_"
                        f"{year}_{income_index}"
                    ),
                )

            total = sum(
                nonnegative_number(value)
                for value in values.values()
            )

            st.metric(
                f"Total mensual {year}",
                f"${total:,.0f}".replace(",", "."),
            )

            ingresos.append(
                {
                    "Nombre": member_name,
                    "Año": year,
                    **values,
                    "Total": total,
                }
            )


# ---------------------------------------------------------
# 5. REVISIÓN Y PDF
# ---------------------------------------------------------

st.subheader("5. Revisión y descarga")

acepto = st.checkbox(
    "Confirmo que revisaré estos antecedentes con mi grupo familiar "
    "y los validaré en el portal oficial."
)

generar = st.button(
    "Validar y preparar PDF",
    type="primary",
    use_container_width=True,
)

if generar:
    errores = []

    if not nombre.strip():
        errores.append("Falta el nombre completo del estudiante.")

    if not valid_rut(rut):
        errores.append("El RUT del estudiante no es válido.")

    if "@" not in correo or "." not in correo.split("@")[-1]:
        errores.append("El correo electrónico no parece válido.")

    for index, member in enumerate(familia[1:], start=2):
        if not member["Nombre completo"]:
            errores.append(
                f"Falta el nombre del integrante {index}."
            )

        if (
            member["RUT"]
            and not valid_rut(member["RUT"])
        ):
            errores.append(
                f"El RUT del integrante {index} no es válido."
            )

    if not acepto:
        errores.append(
            "Debes confirmar la revisión antes de generar el PDF."
        )

    if errores:
        for error in errores:
            st.error(error)

    else:
        datos_pdf = {
            "postulante": {
                "nombre": nombre.strip(),
                "rut": format_rut(rut),
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
            },
            "academicos": {
                "tipo_establecimiento": tipo_establecimiento,
                "nem": nem,
                "media_chile": media_chile,
                "institucion": institucion.strip(),
                "ultimo_ano": (
                    ultimo_ano
                    if ultimo_ano != 0
                    else "No aplica"
                ),
                "cuenta_ahorro": cuenta_ahorro,
            },
            "familia": familia,
            "ingresos": ingresos,
            "income_types": INCOME_TYPES,
            "years": INCOME_YEARS,
        }

        pdf = build_pdf(datos_pdf)

        st.success(
            "Los antecedentes fueron validados correctamente."
        )

        total_2025 = sum(
            row["Total"]
            for row in ingresos
            if row["Año"] == 2025
        )

        total_2026 = sum(
            row["Total"]
            for row in ingresos
            if row["Año"] == 2026
        )

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Integrantes",
            len(familia),
        )

        metric2.metric(
            "Ingreso mensual 2025",
            f"${total_2025:,.0f}".replace(",", "."),
        )

        metric3.metric(
            "Ingreso mensual 2026",
            f"${total_2026:,.0f}".replace(",", "."),
        )

        st.download_button(
            "Descargar borrador PDF",
            data=pdf,
            file_name="borrador_fuas_2027_no_oficial.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )


st.divider()

st.markdown(
    """
    **Importante:** la postulación y el comprobante válido
    se obtienen exclusivamente en
    [fuas.cl](https://fuas.cl).
    """
)
