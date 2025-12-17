
# Evaluacion_Norma.py — Integración con Google Drive (Streamlit Cloud)
import os
import json
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Utilidades de Drive (colocar drive_uploader.py en la raíz del repo)
from drive_uploader import (
    fetch_token_from_code,     # maneja el callback OAuth (?code=)
    get_service,               # obtiene el servicio de Drive o muestra "Autorizar"
    ensure_path,               # crea/encuentra carpetas: raiz/sitio/norma/descripcion
    upload_file,               # sube archivo → (file_id, web_link)
    set_permission_anyone,     # abre el enlace para "anyone with the link"
    slugify                    # normaliza texto
)

# -------------------------------------------------------------------
# Configuración de la página
# -------------------------------------------------------------------
st.set_page_config(page_title="Evaluación de Cumplimiento", layout="wide")

# -------------------------------------------------------------------
# Manejo del callback OAuth usando API estable: st.query_params
# -------------------------------------------------------------------
code = st.query_params.get("code", None)
if code and "google_creds" not in st.session_state:
    # Intercambia el code por tokens y guarda la sesión
    fetch_token_from_code(code)
    # Limpia solo el parámetro 'code' manteniendo otros (si existieran)
    qp = dict(st.query_params)
    qp.pop("code", None)
    st.query_params = qp  # reasigna el dict limpio

# -------------------------------------------------------------------
# Funciones auxiliares (basadas en tu código original)
# -------------------------------------------------------------------
def cargar_diagnostico_especifico(norma: str) -> pd.DataFrame:
    """Carga el Excel específico de la norma: <norma>_diagnostico.xlsx."""
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
    """Carga el JSON persistido con respuestas/evidencias de una norma/sitio."""
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

# -------------------------------------------------------------------
# Estado de la página: sitio y norma actuales
# -------------------------------------------------------------------
sitio_actual = st.session_state.get("sitio_actual", "")
norma_actual = st.session_state.get("norma_actual", "")

# Carga de datos
df = cargar_diagnostico_especifico(norma_actual)
diagnostico_guardado = cargar_diagnostico_guardado(norma_actual, sitio_actual)

# -------------------------------------------------------------------
# Encabezado
# -------------------------------------------------------------------
header_left, header_right = st.columns([0.8, 0.2])
with header_left:
    st.markdown(f"## Evaluación de Cumplimiento para **{norma_actual}**")
with header_right:
    if st.button("← Regresar al Diagnóstico"):
        st.switch_page("pages/Compliance.py")  # respeta tu ruta original

st.markdown("---")

# -------------------------------------------------------------------
# Estructura de evidencias
# -------------------------------------------------------------------
archivos_evidencia = diagnostico_guardado.get("archivos_evidencia", {})
if not isinstance(archivos_evidencia, dict):
    archivos_evidencia = {}

# -------------------------------------------------------------------
# Flujo principal
# -------------------------------------------------------------------
if not df.empty:
    respuestas_usuario = diagnostico_guardado.get("respuestas", {})

    # ================================================================
    # Escenario 1: YA HAY RESPUESTAS → Reporte con AgGrid
    # ================================================================
    if respuestas_usuario:
        data_resultados = []

        # Resolver nombres de columnas de forma flexible
        col_desc = next((c for c in ["Descripción", "Descripcion"] if c in df.columns), None)
        col_cat  = next((c for c in ["Categoría", "Categoria"] if c in df.columns), None)
        col_sec  = next((c for c in ["Sección / Capítulo", "Seccion / Capitulo"] if c in df.columns), None)

        for descripcion, respuesta in respuestas_usuario.items():
            categoria = "N/A"
            seccion_cap = "N/A"
            if col_desc:
                filas = df[df[col_desc] == descripcion]
                if not filas.empty:
                    if col_cat and col_cat in filas.columns:
                        categoria = str(filas.iloc[0][col_cat])
                    if col_sec and col_sec in filas.columns:
                        seccion_cap = str(filas.iloc[0][col_sec])

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
        selected_rows = grid_response.get("selected_rows", [])
        selected_row = selected_rows[0] if isinstance(selected_rows, list) and selected_rows else None

        if selected_row is not None:
            descripcion_sel = selected_row["Descripción"]
            estado_actual = selected_row["Estado"]

            # Botón para cambiar estado
            if st.button("Cambiar estado"):
                respuestas_usuario[descripcion_sel] = "No" if estado_actual == "Cumple" else "Sí"

                cumple_count = sum(1 for r in respuestas_usuario.values() if r == "Sí")
                total_count = len(respuestas_usuario)
                nuevo_cumplimiento = (cumple_count / total_count * 100) if total_count > 0 else 0

                # Persistir
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
                    f"Se cambió **{descripcion_sel}** a "
                    f"**{'No cumple' if estado_actual == 'Cumple' else 'Cumple'}**."
                )
                st.rerun()

            # Evidencias actuales (URLs de Drive)
            st.markdown(f"### Evidencias para: **{descripcion_sel}**")
            evidencias_urls = archivos_evidencia.get(descripcion_sel, [])
            if evidencias_urls:
                st.write("Evidencias en la nube (Google Drive):")
                for url in evidencias_urls:
                    cols = st.columns([0.8, 0.2])
                    with cols[0]:
                        st.markdown(f"- {url}")
                    with cols[1]:
                        if st.button("Eliminar", key=f"del_{hash(url)}"):
                            archivos_evidencia[descripcion_sel].remove(url)
                            # Persistir cambios
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
                            st.success("Enlace eliminado del registro.")
                            st.rerun()

            # Uploader de nuevas evidencias
            archivos_subidos = st.file_uploader(
                "Selecciona uno o varios archivos",
                type=["jpg", "jpeg", "png", "docx", "pdf", "xlsx"],
                accept_multiple_files=True,
                key=f"file_{slugify(descripcion_sel)}"
            )

            # Subida a Google Drive
            ROOT_FOLDER_ID = st.secrets["DRIVE_ROOT_FOLDER_ID"]

            if archivos_subidos:
                if st.button("Guardar archivo(s)"):
                    service = get_service()
                    if service is None:
                        st.stop()  # esperar autorización

                    # Jerarquía: raiz / sitio / norma / descripcion
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

                        # Abrir por enlace (anyone with the link)
                        set_permission_anyone(service, file_id)

                        archivos_evidencia[descripcion_sel].append(web_link)

                        # Limpieza temporal
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass

                    # Recalcular cumplimiento y persistir JSON
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

    # ================================================================
    # Escenario 2: NO hay respuestas → Preguntas y guardado
    # ================================================================
    else:
        st.markdown("## 📝 Responder Preguntas de Diagnóstico")

        # Detectar columna de pregunta
        if "Preguntas para Diagnóstico" in df.columns:
            COL_PREG = "Preguntas para Diagnóstico"
        elif "Pregunta para Diagnóstico" in df.columns:
            COL_PREG = "Pregunta para Diagnóstico"
        elif "Diagnóstico" in df.columns:
            COL_PREG = "Diagnóstico"
        elif "Diagnostico" in df.columns:
            COL_PREG = "Diagnostico"
        else:
            COL_PREG = "Descripción"

        # Columna descripción
        col_desc = "Descripción" if "Descripción" in df.columns else (
            "Descripcion" if "Descripcion" in df.columns else COL_PREG
        )

        respuestas_map = {}
        cumple_list = []
        no_cumple_list = []

        for _, row in df.iterrows():
            descripcion = str(row.get(col_desc, "")).strip()
            texto_pregunta = str(row.get(COL_PREG, "")).strip() or descripcion

            respuesta = st.radio(
                f"🔹 {texto_pregunta}",
                ("No", "Sí"),
                key=f"{norma_actual}_{descripcion}"
            )
            respuestas_map[descripcion] = respuesta
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
                    "cumplimiento": f"{cumplimiento:.                    "cumplimiento": f"{cumplimiento:.2f}%",
                    "respuestas": respuestas_map,
                    "archivos_evidencia": {}  # se llenará al subir evidencias
                }, file, indent=4, ensure_ascii=False)
            st.success("✅ Evaluación guardada.")
            st.rerun()
else:
 st.warning("⚠️ No se ha seleccionado una norma para evaluar.")
