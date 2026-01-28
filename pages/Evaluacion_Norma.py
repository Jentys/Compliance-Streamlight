import streamlit as st
import pandas as pd
import json
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Evaluación de Cumplimiento", layout="wide")

st.markdown(
    """
    <style>
        header {visibility: hidden;}

        :root {
            --primary: #008CBA;
            --background-light: #F8FAFC;
            --text-dark: #0F172A;
            --text-muted: #64748B;
            --card-border: #E2E8F0;
        }

        body {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: var(--background-light);
        }

        .top-nav {
            position: sticky;
            top: 0;
            z-index: 10;
            background: white;
            border-bottom: 1px solid var(--card-border);
            padding: 18px 32px;
            margin: 0 -16px 24px -16px;
        }

        .nav-title {
            font-size: 20px;
            font-weight: 700;
            color: var(--text-dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .nav-action .stButton > button {
            border-radius: 999px;
            padding: 8px 14px;
            border: 1px solid var(--card-border);
            background: #F8FAFC;
            color: var(--text-dark);
            font-weight: 600;
        }

        .nav-action .stButton > button:hover {
            border-color: var(--primary);
            color: var(--primary);
        }

        .hero-title {
            font-size: 28px;
            font-weight: 800;
            color: var(--text-dark);
            margin-bottom: 6px;
        }

        .hero-subtitle {
            font-size: 14px;
            color: var(--text-muted);
        }

        .content-card {
            background: white;
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 24px;
            margin-top: 16px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--text-dark);
            margin-bottom: 12px;
        }

        .primary-action .stButton > button {
            width: 100%;
            border-radius: 14px;
            padding: 12px 18px;
            font-weight: 600;
            border: none;
            background: var(--primary);
            color: white;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .primary-action .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 16px rgba(0, 140, 186, 0.25);
        }

        .secondary-action .stButton > button {
            width: 100%;
            border-radius: 14px;
            padding: 10px 16px;
            background: #E2E8F0;
            color: var(--text-dark);
            border: none;
            font-weight: 600;
        }

        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] > div,
        .stTextArea textarea {
            border-radius: 14px !important;
            border: 1px solid #E2E8F0 !important;
            background: #F8FAFC !important;
            padding: 12px 14px !important;
            font-size: 14px !important;
            box-shadow: none !important;
        }

        .stRadio [role="radiogroup"] {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .stRadio label {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 999px;
            padding: 6px 14px;
            font-weight: 600;
            color: var(--text-dark);
            margin-right: 0;
        }

        .stAlert {
            border-radius: 16px;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Función para cargar el diagnóstico específico de una norma desde Excel
# -----------------------------------------------------------------------------

def cargar_diagnostico_especifico(norma):
    archivo_norma = f"{norma}_diagnostico.xlsx"
    if os.path.exists(archivo_norma):
        try:
            df = pd.read_excel(archivo_norma, engine="openpyxl")
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"⚠️ Error al leer el archivo: {e}")
            return pd.DataFrame()
    return pd.DataFrame()


# -----------------------------------------------------------------------------
# Función para cargar diagnósticos previos desde un archivo JSON
# -----------------------------------------------------------------------------

def cargar_diagnostico_guardado(norma, sitio):
    folder = os.path.join("diagnosticos", norma)
    archivo_guardado = os.path.join(folder, f"cumplimiento_{sitio}_{norma}.json")
    if os.path.exists(archivo_guardado):
        with open(archivo_guardado, "r", encoding="utf-8") as file:
            contenido = file.read().strip()
            if not contenido:
                return {}
            try:
                return json.loads(contenido)
            except json.decoder.JSONDecodeError:
                return {}
    return {}


# -----------------------------------------------------------------------------
# Recuperar norma y sitio
# -----------------------------------------------------------------------------

sitio_actual = st.session_state.get("sitio_actual", "")
norma_actual = st.session_state.get("norma_actual", "")

# Cargar el DataFrame
df = cargar_diagnostico_especifico(norma_actual)
# Cargar respuestas guardadas
diagnostico_guardado = cargar_diagnostico_guardado(norma_actual, sitio_actual)

# -----------------------------------------------------------------------------
# Encabezado
# -----------------------------------------------------------------------------

st.markdown('<div class="top-nav">', unsafe_allow_html=True)
header_left, header_right = st.columns([0.7, 0.3])
with header_left:
    st.markdown(
        f'<div class="nav-title"><span class="material-icons-round" style="color:#008CBA;">fact_check</span>Evaluación {norma_actual}</div>',
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown('<div class="nav-action">', unsafe_allow_html=True)
    if st.button("← Regresar al Diagnóstico"):
        st.switch_page("pages/Compliance.py")
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div>
        <div class="hero-title">Evaluación de Cumplimiento</div>
        <div class="hero-subtitle">Sitio: <strong>{sitio_actual or 'Sin seleccionar'}</strong> · Norma: <strong>{norma_actual or 'Sin seleccionar'}</strong></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Preparar estructura de evidencias
# -----------------------------------------------------------------------------

archivos_evidencia = diagnostico_guardado.get("archivos_evidencia", {})
if not isinstance(archivos_evidencia, dict):
    archivos_evidencia = {}

if not df.empty:
    respuestas_usuario = diagnostico_guardado.get("respuestas", {})

    # -------------------------------------------------------------------------
    # Escenario 1: YA HAY RESPUESTAS GUARDADAS → Mostrar REPORTE con AgGrid
    # -------------------------------------------------------------------------
    if respuestas_usuario:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        data_resultados = []
        for descripcion, respuesta in respuestas_usuario.items():
            fila = df.loc[df["Descripción"] == descripcion]
            if not fila.empty:
                categoria = fila["Categoría"].values[0]
                seccion_cap = fila["Sección / Capítulo"].values[0]
            else:
                categoria = "N/A"
                seccion_cap = "N/A"
            estado = "Cumple" if respuesta == "Sí" else "No cumple"
            archivos_count = len(archivos_evidencia.get(descripcion, []))
            data_resultados.append(
                {
                    "Categoría": categoria,
                    "Sección / Capítulo": seccion_cap,
                    "Descripción": descripcion,
                    "Estado": estado,
                    "Archivos": archivos_count,
                }
            )
        df_resultados = pd.DataFrame(data_resultados)

        cumple_count = sum(1 for r in respuestas_usuario.values() if r == "Sí")
        total_count = len(respuestas_usuario)
        cumplimiento = (cumple_count / total_count * 100) if total_count > 0 else 0

        st.markdown(
            f'<div class="section-title">📜 Evaluación de Cumplimiento ({cumplimiento:.2f}%)</div>',
            unsafe_allow_html=True,
        )

        gb = GridOptionsBuilder.from_dataframe(df_resultados)
        gb.configure_default_column(filter=True, sortable=True)
        gb.configure_selection(selection_mode="single", use_checkbox=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            df_resultados,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="balham",
            fit_columns_on_grid_load=True,
        )

        selected_rows = grid_response["selected_rows"]
        selected_row = None
        if isinstance(selected_rows, list) and len(selected_rows) > 0:
            selected_row = selected_rows[0]
        elif isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
            selected_row = selected_rows.iloc[0].to_dict()

        if selected_row is not None:
            descripcion_sel = selected_row["Descripción"]
            estado_actual = selected_row["Estado"]

            st.markdown('<div class="secondary-action">', unsafe_allow_html=True)
            if st.button("Cambiar estado"):
                if estado_actual == "Cumple":
                    respuestas_usuario[descripcion_sel] = "No"
                else:
                    respuestas_usuario[descripcion_sel] = "Sí"
                cumple_count = sum(1 for r in respuestas_usuario.values() if r == "Sí")
                total_count = len(respuestas_usuario)
                nuevo_cumplimiento = (cumple_count / total_count * 100) if total_count > 0 else 0
                folder = os.path.join("diagnosticos", norma_actual)
                os.makedirs(folder, exist_ok=True)
                archivo_guardado = os.path.join(folder, f"cumplimiento_{sitio_actual}_{norma_actual}.json")
                with open(archivo_guardado, "w", encoding="utf-8") as file:
                    json.dump(
                        {
                            "sitio": sitio_actual,
                            "norma": norma_actual,
                            "cumplimiento": f"{nuevo_cumplimiento:.2f}%",
                            "respuestas": respuestas_usuario,
                            "archivos_evidencia": archivos_evidencia,
                        },
                        file,
                        indent=4,
                    )
                st.success(
                    f"Se cambió la descripción '{descripcion_sel}' a estado "
                    f"{'No cumple' if estado_actual == 'Cumple' else 'Cumple'}."
                )
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                f"<div class=\"section-title\">📎 Evidencia para: {descripcion_sel}</div>",
                unsafe_allow_html=True,
            )
            archivos_actuales = archivos_evidencia.get(descripcion_sel, [])
            if archivos_actuales:
                for ruta in archivos_actuales:
                    nombre_archivo = os.path.basename(ruta)
                    cols = st.columns([0.5, 0.25, 0.25])
                    with cols[0]:
                        st.markdown(f"**{nombre_archivo}**")
                    with cols[1]:
                        with open(ruta, "rb") as f:
                            file_bytes = f.read()
                        st.download_button(
                            label="Descargar",
                            data=file_bytes,
                            file_name=nombre_archivo,
                            key=f"descarga_{ruta}",
                        )
                    with cols[2]:
                        if st.button("Eliminar", key=f"eliminar_{ruta}"):
                            archivos_evidencia[descripcion_sel].remove(ruta)
                            if os.path.exists(ruta):
                                os.remove(ruta)
                            folder = os.path.join("diagnosticos", norma_actual)
                            os.makedirs(folder, exist_ok=True)
                            archivo_guardado = os.path.join(
                                folder, f"cumplimiento_{sitio_actual}_{norma_actual}.json"
                            )
                            with open(archivo_guardado, "w", encoding="utf-8") as file:
                                json.dump(
                                    {
                                        "sitio": sitio_actual,
                                        "norma": norma_actual,
                                        "respuestas": respuestas_usuario,
                                        "archivos_evidencia": archivos_evidencia,
                                    },
                                    file,
                                    indent=4,
                                )
                            st.success("Archivo eliminado correctamente.")
                            st.rerun()

            archivos_subidos = st.file_uploader(
                "Selecciona uno o varios archivos",
                type=["jpg", "jpeg", "png", "docx", "pdf", "xlsx"],
                accept_multiple_files=True,
                key=f"file_{descripcion_sel}",
            )
            if archivos_subidos:
                st.markdown('<div class="primary-action">', unsafe_allow_html=True)
                if st.button("Guardar archivo(s)"):
                    carpeta_evidencias = os.path.join("evidencias", norma_actual)
                    os.makedirs(carpeta_evidencias, exist_ok=True)
                    for file_obj in archivos_subidos:
                        filename = f"{descripcion_sel}_{file_obj.name}".replace(" ", "_")
                        filepath = os.path.join(carpeta_evidencias, filename)
                        with open(filepath, "wb") as f:
                            f.write(file_obj.getbuffer())
                        if descripcion_sel not in archivos_evidencia:
                            archivos_evidencia[descripcion_sel] = []
                        archivos_evidencia[descripcion_sel].append(filepath)
                    cumple_count = sum(1 for r in respuestas_usuario.values() if r == "Sí")
                    total_count = len(respuestas_usuario)
                    nuevo_cumplimiento = (cumple_count / total_count * 100) if total_count > 0 else 0
                    folder = os.path.join("diagnosticos", norma_actual)
                    os.makedirs(folder, exist_ok=True)
                    archivo_guardado = os.path.join(
                        folder, f"cumplimiento_{sitio_actual}_{norma_actual}.json"
                    )
                    with open(archivo_guardado, "w", encoding="utf-8") as file:
                        json.dump(
                            {
                                "sitio": sitio_actual,
                                "norma": norma_actual,
                                "cumplimiento": f"{nuevo_cumplimiento:.2f}%",
                                "respuestas": respuestas_usuario,
                                "archivos_evidencia": archivos_evidencia,
                            },
                            file,
                            indent=4,
                        )
                    st.success("Archivo(s) guardado(s) correctamente.")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Escenario 2: NO hay respuestas → Mostrar PREGUNTAS (columna E)
    # -------------------------------------------------------------------------
    else:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📝 Responder Preguntas de Diagnóstico</div>', unsafe_allow_html=True)

        if "Preguntas para Diagnóstico" in df.columns:
            col_preg = "Preguntas para Diagnóstico"
        elif "Pregunta para Diagnóstico" in df.columns:
            col_preg = "Pregunta para Diagnóstico"
        elif "Diagnóstico" in df.columns:
            col_preg = "Diagnóstico"
        elif "Diagnostico" in df.columns:
            col_preg = "Diagnostico"
        else:
            col_preg = "Descripción"

        respuestas_usuario = {}
        cumple_list = []
        no_cumple_list = []

        for _, row in df.iterrows():
            descripcion = row.get("Descripción", "")
            texto_pregunta = row.get(col_preg, "")
            if pd.isna(texto_pregunta) or str(texto_pregunta).strip() == "":
                texto_pregunta = descripcion
            texto_pregunta = str(texto_pregunta).strip()

            respuesta = st.radio(
                f"🔹 {texto_pregunta}",
                ("No", "Sí"),
                key=f"{norma_actual}_{descripcion}",
            )
            respuestas_usuario[descripcion] = respuesta

            if respuesta == "Sí":
                cumple_list.append(descripcion)
            else:
                no_cumple_list.append(descripcion)

        total_count = len(cumple_list) + len(no_cumple_list)
        cumplimiento = (len(cumple_list) / total_count * 100) if total_count > 0 else 0
        st.markdown(
            f'<div class="section-title">📜 Evaluación de Cumplimiento ({cumplimiento:.2f}%)</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="primary-action">', unsafe_allow_html=True)
        if st.button("📊 Guardar Evaluación de Cumplimiento"):
            folder = os.path.join("diagnosticos", norma_actual)
            os.makedirs(folder, exist_ok=True)
            archivo_guardado = os.path.join(folder, f"cumplimiento_{sitio_actual}_{norma_actual}.json")
            with open(archivo_guardado, "w", encoding="utf-8") as file:
                json.dump(
                    {
                        "sitio": sitio_actual,
                        "norma": norma_actual,
                        "cumplimiento": f"{cumplimiento:.2f}%",
                        "respuestas": respuestas_usuario,
                        "archivos_evidencia": {},
                    },
                    file,
                    indent=4,
                )
            st.success("✅ Evaluación guardada.")
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)
else:
    st.warning("⚠️ No se ha seleccionado una norma para evaluar.")
