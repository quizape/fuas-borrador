import pandas as pd
import streamlit as st

from pdf_generator import build_pdf
from validators import format_rut, nonnegative_number, valid_rut


st.set_page_config(
    page_title="Borrador FUAS 2027",
    page_icon="🎓",
    layout="wide",
)

# Confirmar estos años cuando se publique el instructivo FUAS 2027.
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
            Organiza tus antecedentes antes de completar la
            postulación oficial.
        </p>
    </div>

    <div class="warning">
        <b>Documento no oficial.</b>
        Esta herramienta no realiza una postulación, no reemplaza
        a fuas.cl y no genera un comprobante del Mineduc.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Privacidad: esta aplicación no utiliza una base de datos. "
    "Los antecedentes permanecen solamente durante la sesión."
)


# Datos iniciales del grupo familiar
if "familia" not in st.session_state:
    st.session_state.familia = pd.DataFrame(
        [
            {
                "RUT": "",
                "Nombre completo": "",
                "Edad": 18,
                "Estado civil": "Soltero/a",
                "Parentesco": "Postulante",
                "Actividad": "Estudiante",
                "Nivel de estudios": "Enseñanza media",
            }
        ]
    )

if "ingresos_guardados" not in st.session_state:
    st.session_state.ingresos_guardados = pd.DataFrame()


# ---------------------------------------------------------
# 1. DATOS PERSONALES
# ---------------------------------------------------------

st.subheader("1. Antecedentes de la persona postulante")

column1, column2, column3 = st.columns(3)

nombre = column1.text_input("Nombre completo *")
rut = column2.text_input(
    "RUT *",
    placeholder="12.345.678-5",
)
estado_civil = column3.selectbox(
    "Estado civil",
    [
        "Soltero/a",
        "Casado/a",
        "Divorciado/a",
        "Viudo/a",
        "Conviviente civil",
        "Otro",
    ],
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
        "Prefiero revisarlo en el portal oficial",
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
    [
        "Estudiante",
        "Trabajador/a dependiente",
        "Trabajador/a independiente",
        "Cesante",
        "Dueño/a de casa",
        "Otra",
    ],
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
    "¿Cursaste los 4 niveles de enseñanza media en Chile?",
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
    "Incluye a quienes comparten ingresos y gastos. "
    "La persona postulante también debe aparecer en esta tabla."
)

familia = st.data_editor(
    st.session_state.familia,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "Edad": st.column_config.NumberColumn(
            "Edad",
            min_value=0,
            max_value=120,
            step=1,
        ),
        "Estado civil": st.column_config.SelectboxColumn(
            "Estado civil",
            options=[
                "Soltero/a",
                "Casado/a",
                "Divorciado/a",
                "Viudo/a",
                "Conviviente civil",
                "Otro",
            ],
        ),
        "Parentesco": st.column_config.SelectboxColumn(
            "Parentesco",
            options=[
                "Postulante",
                "Madre",
                "Padre",
                "Hermano/a",
                "Cónyuge o pareja",
                "Hijo/a",
                "Abuelo/a",
                "Otro familiar",
                "No familiar",
            ],
        ),
    },
    key="editor_familia",
)

st.session_state.familia = familia.copy()


# ---------------------------------------------------------
# 4. INGRESOS
# ---------------------------------------------------------

st.subheader("4. Ingresos del grupo familiar")

st.info(
    "Escribe el promedio mensual de cada ingreso. "
    "Para calcularlo, suma lo recibido entre enero y diciembre "
    "y divide el resultado por 12."
)

nombres_integrantes = []

if "Nombre completo" in familia.columns:
    nombres_integrantes = [
        str(value).strip()
        for value in familia["Nombre completo"].tolist()
        if str(value).strip()
    ]

if not nombres_integrantes:
    st.warning(
        "Primero escribe el nombre de al menos un integrante "
        "en la tabla anterior."
    )
    ingresos = pd.DataFrame()
else:
    filas_ingresos = []

    for integrante in nombres_integrantes:
        for year in INCOME_YEARS:
            fila = {
                "Nombre": integrante,
                "Año": year,
            }

            for income_type in INCOME_TYPES:
                fila[income_type] = 0.0

            filas_ingresos.append(fila)

    ingresos_base = pd.DataFrame(filas_ingresos)

    guardados = st.session_state.ingresos_guardados

    if not guardados.empty:
        ingresos_base = ingresos_base.merge(
            guardados,
            on=["Nombre", "Año"],
            how="left",
            suffixes=("", "_guardado"),
        )

        for income_type in INCOME_TYPES:
            saved_column = income_type + "_guardado"

            if saved_column in ingresos_base.columns:
                ingresos_base[income_type] = (
                    ingresos_base[saved_column]
                    .fillna(ingresos_base[income_type])
                )

        ingresos_base = ingresos_base[
            ["Nombre", "Año"] + INCOME_TYPES
        ]

    ingresos = st.data_editor(
        ingresos_base,
        use_container_width=True,
        hide_index=True,
        disabled=["Nombre", "Año"],
        column_config={
            income_type: st.column_config.NumberColumn(
                income_type,
                min_value=0,
                step=1000,
                format="$ %d",
            )
            for income_type in INCOME_TYPES
        },
        key="editor_ingresos",
    )


# ---------------------------------------------------------
# 5. VALIDACIÓN Y PDF
# ---------------------------------------------------------

st.subheader("5. Revisión y descarga")

acepto = st.checkbox(
    "Confirmo que revisaré estos antecedentes con mi grupo "
    "familiar y los validaré en el portal oficial."
)

generar = st.button(
    "Validar y preparar PDF",
    type="primary",
    use_container_width=True,
)

if generar:
    errors = []

    if not nombre.strip():
        errors.append("Falta el nombre completo.")

    if not valid_rut(rut):
        errors.append("El RUT de la persona postulante no es válido.")

    if (
        "@" not in correo
        or "." not in correo.split("@")[-1]
    ):
        errors.append("El correo electrónico no parece válido.")

    if familia.empty:
        errors.append(
            "Debes incluir al menos un integrante del grupo familiar."
        )

    if not nombres_integrantes:
        errors.append(
            "Completa el nombre de al menos un integrante."
        )

    if ingresos.empty:
        errors.append(
            "No se pudo crear la tabla de ingresos."
        )

    if not acepto:
        errors.append(
            "Debes confirmar la revisión antes de generar el PDF."
        )

    if "RUT" in familia.columns:
        member_ruts = [
            str(value).strip()
            for value in familia["RUT"].tolist()
            if str(value).strip()
        ]

        invalid_member_ruts = [
            value
            for value in member_ruts
            if not valid_rut(value)
        ]

        if invalid_member_ruts:
            errors.append(
                "Hay RUT inválidos en el grupo familiar: "
                + ", ".join(invalid_member_ruts)
            )

    if errors:
        for error in errors:
            st.error(error)

    else:
        ingresos_limpios = ingresos.copy()

        for income_type in INCOME_TYPES:
            ingresos_limpios[income_type] = (
                ingresos_limpios[income_type]
                .map(nonnegative_number)
            )

        ingresos_limpios["Total"] = (
            ingresos_limpios[INCOME_TYPES]
            .sum(axis=1)
        )

        st.session_state.ingresos_guardados = (
            ingresos_limpios[
                ["Nombre", "Año"] + INCOME_TYPES
            ].copy()
        )

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
            "familia": (
                familia.fillna("").to_dict("records")
            ),
            "ingresos": (
                ingresos_limpios.fillna(0).to_dict("records")
            ),
            "income_types": INCOME_TYPES,
            "years": INCOME_YEARS,
        }

        pdf = build_pdf(datos_pdf)

        st.success(
            "Los antecedentes fueron validados. "
            "Ya puedes descargar el borrador."
        )

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Integrantes",
            len(familia),
        )

        total_year_1 = ingresos_limpios.loc[
            ingresos_limpios["Año"] == INCOME_YEARS[0],
            "Total",
        ].sum()

        total_year_2 = ingresos_limpios.loc[
            ingresos_limpios["Año"] == INCOME_YEARS[1],
            "Total",
        ].sum()

        metric2.metric(
            f"Ingreso mensual {INCOME_YEARS[0]}",
            f"${total_year_1:,.0f}".replace(",", "."),
        )

        metric3.metric(
            f"Ingreso mensual {INCOME_YEARS[1]}",
            f"${total_year_2:,.0f}".replace(",", "."),
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
    **Importante:** para postular y obtener un comprobante válido,
    debes ingresar al sitio oficial
    [fuas.cl](https://fuas.cl).
    """
)
