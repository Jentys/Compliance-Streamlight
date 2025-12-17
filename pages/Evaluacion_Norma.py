
# Evaluacion_Norma.py — Integración con Google Drive (Streamlit Cloud)
import streamlit as st
import pandas as pd
import json
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# --------------------------
# 1) Manejo de OAuth (callback)
# --------------------------
from drive_uploader import fetch_token_from_code, get_service, ensure_path, upload_file, set_permission_anyone, slugify

# Captura '?code=' cuando Google regresa a la app tras autorizar Drive
params = st.experimental_get_query_params()
code = params.get("code", [None])[0]
if code and "google_creds" not in st.session_state:
    fetch_token_from_code(code)
    # Limpia la URL para no re-ejecutar el callback
    st.experimental_set_query_params()

# Configuración de la página
st.set_page_config(page_title="Evaluación de Cumplimiento", layout="wide")

# --------------------------
# 2) Funciones auxiliares (sin cambios en lógica base)
# --------------------------
def cargar_diagnostico_especifico(norma: str) -> pd.DataFrame:
    """
    Carga el archivo Excel específico de la norma, p.ej: 'NOM-001_diagnostico.xlsx'.
    """
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

def cargar_diagnostico_guardado(norma: str, sitio: str) -> dict:
    """
    Carga el JSON persistido con respuestas y evidencias de una norma/sitio.
    """
    folder = os.path.join("diagnosticos", norma)
    archivo_guardado = os.path.join(folder, f"cumplimiento_{sitio}_{norma}.json")
    if os.path.exists(archivo_guardado):
        try:
            with open(archivo_guardado, "r", encoding="utf-8") as file:
                contenido = file.read().strip()
            if not contenido:
                return {}
            return json.loads(contenido)
        except json.decoder.JSONDecodeError:
            return {}
        except Exception as e:
            st.error(f"⚠️ Error al leer el archivo guardado: {e}")
            return {}
    return {}

# --------------------------
# 3) Estado y carga de datos
# --------------------------
sitio_actual = st.session_state.get("sitio_actual", "")
norma_actual = st.session_state.get("norma_actual", "")

df = cargar_diagnostico_especifico(norma_actual)
diagnostico_guardado = cargar_diagnostico_guardado(norma_actual, sitio_actual)

# --------------------------
# 4) Encabezado de la página
# --------------------------
header_left, header_right = st.columns([0.8, 0.2])
with header_left:
    st.markdown(f"## Evaluación de Cumplimiento para **{norma_actual}**")
with header_right:
    if st.button("← Regresar al Diagnóstico"):
        st.switch_page("pages/Compliance.py")  # respeta tu ruta original

st.markdown("---")

# --------------------------
# 5) Estructura de evidencias
# --------------------------
archivos_evidencia = diagnostico_guardado.get("archivos_evidencia", {})
if not isinstance(archivos_evidencia, dict):
    archivos_evidencia = {}

# --------------------------
# 6) Flujo principal
# --------------------------
if not df.empty:
    # Respuestas previas (si existen)
    respuestas_usuario = diagnostico_guardado.get("respuestas", {})

    # ===== Escenario 1: YA HAY RESPUESTAS → Reporte con AgGrid =====
    if respuestas_usuario:
        data_resultados = []
        for descripcion, respuesta in respuestas_usuario.items():
            # Busca metadatos en el DF
            fila = df.loc[df.get("Descripción", pd.Series(dtype=str)) == descripcion]
            if not fila.empty:
                categoria = fila.get("Categoría", pd.Series(["N/A"])).values[0]
                seccion_cap = fila.get("Sección / Capítulo", pd.Series(["N/A"])).values[0]
            else:
                categoria = "N/A"
                seccion_cap = "N/A"

            estado = "Cumple" if respuesta == "Sí" else "No cumple"
            archivos_count = len(archivos_evidencia.get(descripcion, []))
            data_resultados.append({
                "Categoría": categoria,
                "Sección / Capítulo": seccion_cap,
                "Descripción": descripcion,
                "Estado": estado,
                "Archivos": archivos_count
            })

        df_resultados = pd.DataFrame(data_resultados)

        # % cumplimiento
        cumple_count = sum(1 for r in respuestas_usuario.values() if r == "Sí")
        total_count = len(respuestas_usuario)
        cumplimiento = (cumple_count / total_count * 100) if total_count > 0 else 0
        st.markdown(f"### 📝 Evaluación de Cumplimiento (**{cumplimiento:.2f}%**)")

        # AgGrid
        gb = GridOptionsBuilder.from_dataframe(df_resultados)
        gb.configure_default_column(filter=True, sortable=True)
        gb.configure_selection(selection_mode="single", use_checkbox=True)
        gridOptions = gb.build()
        grid_response = AgGrid(
            df_resultados,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            theme="balham",
            fit_columns_on_grid_load=True
        )

        # Fila seleccionada
        selected_rows = grid_response["selected_rows"]
        selected_row = None
        if isinstance(selected_rows, list) and len(selected_rows) > 0:
            selected_row = selected_rows[0]
        elif isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
            selected_row = selected_rows.iloc[0].to_dict()

        if selected_row is not None:
            descripcion_sel = selected_row["Descripción"]
            estado_actual = selected_row["Estado"]

            # Botón para cambiar estado (Cumple / No cumple)
            if st.button("Cambiar estado"):
                if estado_actual == "Cumple":
                    respuestas_usuario[descripcion_sel] = "No"
                else:
                    respuestas_usuario[descripcion_sel] = "Sí"

                cumple_count = sum(1 for r in respuestas_usuario.values() if r == "Sí")
                total_count = len(respuestas_usuario)
                nuevo_cumplimiento = (cumple_count / total_count * 100) if total_count > 0 else 0

                # Persistencia
                folder = os.path.join("diagnosticos", norma_actual)
                os.makedirs(folder, exist_ok=True)
                archivo_guardado = os.path.join(folder, f"cumplimiento_{sitio_actual}_{norma_actual}.json")
                with open(archivo_guardado, "w", encoding="utf-8") as file:
                    json.dump({
                        "sitio": sitio_actual,
                        "norma": norma_actual,
                        "cumplimiento": f"{nuevo_cumplimiento:.2f}%",
                        "respuestas": respuestas_usuario,
                        "archivos_evidencia": archivos_evidencia
                    }, file, indent=4, ensure_ascii=False)

                st.success(
                    f"Se cambió la descripción **{descripcion_sel}** a estado "
                    f"**{'No cumple' if estado_actual == 'Cumple' else 'Cumple'}**."
                )
                st.rerun()

            # ===== Evidencias para la descripción seleccionada =====
            st.markdown(f"### Evidencias para: **{descripcion_sel}**")
            archivos_actuales = archivos_evidencia.get(descripcion_sel, [])

            # Listado de evidencias (URLs de Drive)
            if archivos_actuales:
                st.write("Evidencias en la nube (Google Drive):")
                for url in archivos_actuales:
                    cols = st.columns([0.8, 0.2])
                    with cols[0]:
                        # Muestra el enlace; si prefieres, usar markdown con nombre legible
                        st.markdown(f"- [{os.path.basename(url)}]({url})")
                    with cols[1]:
                        if st.button("Eliminar", key=f"del_{hash(url)}"):
                            archivos_evidencia[descripcion_sel].remove(url)
                            folder = os.path.join("diagnosticos", norma_actual)
                            os.makedirs(folder, exist_ok=True)
                            archivo_guardado = os.path.join(
                                folder, f"cumplimiento_{sitio_actual}_{norma_actual}.json"
                            )
                            with open(archivo_guardado, "w", encoding="utf-8") as f:
                                json.dump({
                                    "sitio": sitio_actual,
                                    "norma": norma_actual,
                                    "respuestas": respuestas_usuario,
                                    "archivos_evidencia": archivos_evidencia
                                }, f, indent=4, ensure_ascii=False)
                            st.success("Enlace de evidencia eliminado del registro.")
                            st.rerun()

            # Uploader de nuevas evidencias
            archivos_subidos = st.file_uploader(
                "Selecciona uno o varios archivos",
                type=["jpg", "jpeg", "png", "docx", "pdf", "xlsx"],
                accept_multiple_files=True,
                key=f"file_{slugify(descripcion_sel)}"
            )

            # --------------------------
            # SUBIDA A GOOGLE DRIVE
            # --------------------------
            ROOT_FOLDER_ID = st.secrets["DRIVE_ROOT_FOLDER_ID"]

            if archivos_subidos:
                if st.button("Guardar archivo(s)"):
                    service = get_service()
                    if service is None:
                        st.stop()  # esperar autorización

                    # Jerarquía en Drive: raiz / sitio / norma / descripcion
                    dest_folder_id = ensure_path(service, ROOT_FOLDER_ID, [
                        str(sitio_actual),
                        str(norma_actual),
                        slugify(str(descripcion_sel))
                    ])

                    if descripcion_sel not in archivos_evidencia:
                        archivos_evidencia[descripcion_sel] = []

                    tmp_dir = "tmp_upload"
                    os.makedirs(tmp_dir, exist_ok=True)

                    for file_obj in archivos_subidos:
                        tmp_path = os.path.join(tmp_dir, file_obj.name)
                        with open(tmp_path, "wb") as f:
                            f.write(file_obj.getbuffer())

                        display_name = f"{sitio_actual}_{norma_actual}_{slugify(descripcion_sel)}_{file_obj.name}"
                        file_id, web_link = upload_file(service, tmp_path, dest_folder_id, display_name)

                        # Abierto por enlace (anyone with the link)
                        set_permission_anyone(service, file_id)

                        archivos_evidencia[descripcion_sel].append(web_link)

                        # Limpia temporal
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass

                    # Recalcula cumplimiento y persiste JSON
                    cumple_count = sum(1 for r in respuestas_usuario.values() if r == "Sí")
                    total_count = len(respuestas_usuario)
                    nuevo_cumplimiento = (cumple_count / total_count * 100) if total_count > 0 else 0

                    folder = os.path.join("diagnosticos", norma_actual)
                    os.makedirs(folder, exist_ok=True)
                    archivo_guardado = os.path.join(
                        folder, f"cumplimiento_{sitio_actual}_{norma_actual}.json"
                    )
                    with open(archivo_guardado, "w", encoding="utf-8") as file:
                        json.dump({
                            "sitio": sitio_actual,
                            "norma": norma_actual,
                            "cumplimiento": f"{nuevo_cumplimiento:.2f}%",
                            "respuestas": respuestas_usuario,
                            "archivos_evidencia": archivos_evidencia
                        }, file, indent=4, ensure_ascii=False)

                    st.success("Archivo(s) subido(s) a Google Drive y registrados correctamente.")
                    st.rerun()

    # ===== Escenario 2: NO hay respuestas → Mostrar preguntas y guardar evaluación =====
    else:
        st.markdown("## 📝 Responder Preguntas de Diagnóstico")

        # Detecta la columna de pregunta (flexible)
        if "Preguntas para Diagnóstico" in df.columns:
            COL_PREG = "Preguntas para Diagnóstico"
        elif "Pregunta para Diagnóstico" in df.columns:
            COL_PREG = "Pregunta para Diagnóstico"
        elif "Diagnóstico" in df.columns:
            COL_PREG = "Diagnóstico"
        elif "Diagnostico" in df.columns:
            COL_PREG = "Diagnostico"
        else:
            COL_PREG = "Descripción"  # último recurso

        respuestas_usuario = {}
        cumple_list = []
        no_cumple_list = []

        for _, row in df.iterrows():
            descripcion = row.get("Descripción", "")
            texto_pregunta = row.get(COL_PREG, "")
            if pd.isna(texto_pregunta) or str(texto_pregunta).strip() == "":
                texto_pregunta = descripcion  # fallback
            texto_pregunta = str(texto_pregunta).strip()

            respuesta = st.radio(
                f"🔹 {texto_pregunta}",
                ("No", "Sí"),
                key=f"{norma_actual}_{descripcion}"
            )
            respuestas_usuario[descripcion] = respuesta
            if respuesta == "Sí":
                cumple_list.append(descripcion)
            else:
                no_cumple_list.append(descripcion)

        total_count = len(cumple_list) + len(no_cumple_list)
        cumplimiento = (len(cumple_list) / total_count * 100) if total_count > 0 else 0
        st.markdown(f"### 📝 Evaluación de Cumplimiento (**{cumplimiento:.2f}%**)")

        if st.button("📊 Guardar Evaluación de Cumplimiento"):
            folder = os.path.join("diagnosticos", norma_actual)
            os.makedirs(folder, exist_ok=True)
            archivo_guardado = os.path.join(folder, f"cumplimiento_{sitio_actual}_{norma_actual}.json")
            with open(archivo_guardado, "w", encoding="utf-8") as file:
                json.dump({
                    "sitio": sitio_actual,
                    "norma": norma_actual,
                    "cumplimiento": f"{cumplimiento:.2f}%",
                    "respuestas": respuestas_usuario,
                    "archivos_evidencia": {}  # se llenará cuando subas evidencias
                }, file, indent=4, ensure_ascii=False)
            st.success("✅ Evaluación guardada.")
            st.rerun()
else:
    st.warning("⚠️ No se ha seleccionado una norma para evaluar.")
``
