import streamlit as st
import pandas as pd
import json
import os

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

        .matrix-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 12px;
        }

        .matrix-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        .matrix-table th {
            text-align: left;
            font-weight: 600;
            color: var(--text-muted);
            padding: 12px 10px;
            border-bottom: 1px solid var(--card-border);
        }

        .matrix-table td {
            padding: 14px 10px;
            border-bottom: 1px solid #eef2f6;
            color: var(--text-dark);
            vertical-align: top;
        }

        .matrix-table tr:hover {
            background: #f8fafc;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 999px;
            font-weight: 600;
            font-size: 12px;
        }

        .status-ok {
            background: rgba(34, 197, 94, 0.15);
            color: #15803d;
        }

        .status-bad {
            background: rgba(239, 68, 68, 0.15);
            color: #b91c1c;
        }

        .action-dot {
            color: #94a3b8;
            font-size: 20px;
        }

        .side-card {
            background: white;
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 20px;
        }

        .file-card {
            border: 1px solid #eef2f6;
            border-radius: 14px;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
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

        .stTextInput input:focus,
        .stSelectbox div[data-baseweb="select"] > div:focus-within,
        .stTextArea textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(0, 140, 186, 0.15) !important;
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

def _status_badge(estado):
    if estado == "Cumple":
        return '<span class="status-pill status-ok">Cumple</span>'
    return '<span class="status-pill status-bad">No cumple</span>'


def _render_matrix_table(rows):
    if not rows:
        st.info("No hay registros que coincidan con la búsqueda.")
        return
    table_rows = []
    for row in rows:
        table_rows.append(
            f"""
            <tr>
                <td><strong>{row['Categoría']}</strong></td>
                <td>{row['Sección / Capítulo']}</td>
                <td>{row['Descripción']}</td>
                <td>{_status_badge(row['Estado'])}</td>
                <td class="action-dot">⋯</td>
            </tr>
            """
        )
    table_html = """
        <table class="matrix-table">
            <thead>
                <tr>
                    <th>Norma</th>
                    <th>Sección</th>
                    <th>Descripción</th>
                    <th>Estado</th>
                    <th>Acción</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    """.format(rows="".join(table_rows))
    st.markdown(table_html, unsafe_allow_html=True)


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

        search_query = st.text_input("Buscar estándar o sección", placeholder="Buscar estándar o sección...")
        if search_query:
            filtered_rows = df_resultados[
                df_resultados.apply(
                    lambda row: search_query.lower() in str(row["Descripción"]).lower()
                    or search_query.lower() in str(row["Sección / Capítulo"]).lower()
                    or search_query.lower() in str(row["Categoría"]).lower(),
                    axis=1,
                )
            ]
        else:
            filtered_rows = df_resultados

        st.markdown(
            '<div class="matrix-header"><strong>Evaluation Matrix</strong></div>',
            unsafe_allow_html=True,
        )
        _render_matrix_table(filtered_rows.to_dict("records"))

        opciones_descripcion = filtered_rows["Descripción"].tolist()
        if opciones_descripcion:
            descripcion_sel = st.selectbox(
                "Selecciona un criterio para gestionar evidencia",
                opciones_descripcion,
            )
        else:
            descripcion_sel = None

        if descripcion_sel:
            estado_actual = df_resultados.loc[
                df_resultados["Descripción"] == descripcion_sel, "Estado"
            ].iloc[0]

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

            evidence_left, evidence_right = st.columns([0.6, 0.4])
            with evidence_left:
                st.markdown(
                    f"<div class=\"section-title\">📎 Evidencia para: {descripcion_sel}</div>",
                    unsafe_allow_html=True,
                )
                archivos_actuales = archivos_evidencia.get(descripcion_sel, [])
                if archivos_actuales:
                    for ruta in archivos_actuales:
                        nombre_archivo = os.path.basename(ruta)
                        cols = st.columns([0.6, 0.2, 0.2])
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
            with evidence_right:
                st.markdown('<div class="side-card">', unsafe_allow_html=True)
                st.markdown("**Subir nueva evidencia**")
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
