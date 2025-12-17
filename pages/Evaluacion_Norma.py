
# Evaluacion_Norma.py (VERSIÓN ACTUALIZADA PARA GOOGLE DRIVE)
import streamlit as st
import pandas as pd
import json
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# --- OAuth callback: si Google regresa ?code=..., capturamos y guardamos tokens ---
from drive_uploader import fetch_token_from_code

params = st.experimental_get_query_params()
code = params.get("code", [None])[0]
if code and "google_creds" not in st.session_state:
    fetch_token_from_code(code)
    # Limpia parámetros de la URL para no re-ejecutar el callback
    st.experimental_set_query_params()

st.set_page_config(page_title="Evaluación de Cumplimiento", layout="wide")

# ===== Funciones de carga existentes =====
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

def cargar_diagnostico_guardado(norma, sitio):
    folder = os.path.join("diagnosticos", norma)
    archivo_guardado = os.path.join(folder, f"cumplimiento_{sitio}_{norma}.json")
    if os.path.exists(archivo_guardado):
        with open(archivo_guardado, "r", encoding="utf-8") as file:
            contenido = file.read().strip()
            if not contenido:
                return {}
            else:
                try:
                    return json.loads(contenido)
                except json.decoder.JSONDecodeError:
                    return {}
    return {}

# ===== Recuperar norma y sitio =====
sitio_actual = st.session_state.get("sitio_actual", "")
norma_actual = st.session_state.get("norma_actual", "")

# ===== Cargar DataFrame =====
df = cargar_diagnostico_especifico(norma_actual)

# ===== Cargar respuestas guardadas =====
diagnostico_guardado = cargar_diagnostico_guardado(norma_actual, sitio_actual)

# ===== Encabezado =====
header_left, header_right = st.columns([0.8, 0.2])
with header_left:
    st.markdown(f"## Evaluación de Cumplimiento para {norma_actual}")
with header_right:
    if st.button("← Regresar al Diagnóstico"):
        st.switch_page("pages/Compliance.py")  # respeta tu ruta original

st.markdown("---")

# ===== Preparar estructura de evidencias =====
archivos_evidencia = diagnostico_guardado.get("archivos_evidencia", {})
if not isinstance(archivos_evidencia, dict):
    archivos_evidencia = {}

if not df.empty:
    # Respuestas previas
    respuestas_usuario = diagnostico_guardado.get("respuestas", {})

    # ===== Escenario 1: YA HAY RESPUESTAS → Mostrar REPORTE con AgGrid =====
    if respuestas_usuario:
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
        st.markdown(f"### 📝 Evaluación de Cumplimiento ({cumplimiento:.2f}%)")

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

            # Cambiar estado
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
                    json.dump({
                        "sitio": sitio_actual,
                        "norma": norma_actual,
                        "cumplimiento": f"{nuevo_cumplimiento:.2f}%",
                        "respuestas": respuestas_usuario,
                        "archivos_evidencia": archivos_evidencia
                    }, file, indent=4, ensure_ascii=False)
                st.success(
                    f"Se cambió la descripción '{descripcion_sel}' a estado "
                    + f"{'No cumple' if estado_actual == 'Cumple' else 'Cumple'}."
                )
                st.rerun()

            # ===== Evidencia para la descripción seleccionada =====
            st.markdown(f"### Evidencia para: **{descripcion_sel}**")
            archivos_actuales = archivos_evidencia.get(descripcion_sel, [])
            if archivos_actuales:
                st.write("Evidencias en la nube (Google Drive):")
                for url in archivos_actuales:
                    cols = st.columns([0.7, 0.3])
                    with cols[0]:
                        st.markdown(f"- {url}")
                    with cols[1]:
                        if st.button("Eliminar", key=f"eliminar_{hash(url)}"):
                            archivos_evidencia[descripcion_sel].remove(url)
                            folder = os.path.join("diagnosticos", norma_actual)
                            os.makedirs(folder, exist_ok=True)
                            archivo_guardado = os.path.join(
                                folder, f"cumplimiento_{sitio_actual}_{norma_actual}.json"
                            )
                            with open(archivo_guardado, "w", encoding="utf-8") as file:
                                json.dump({
                                    "sitio": sitio_actual,
                                    "norma": norma_actual,
                                    "respuestas": respuestas_usuario,
                                    "archivos_evidencia": archivos_evidencia
                                }, file, indent=4, ensure_ascii=False)
                            st.success("Enlace eliminado del registro.")
                            st.rerun()

            # ===== Subir evidencia (Google Drive) =====
            archivos_subidos = st.file_uploader(
                "Selecciona uno o varios archivos",
                type=["jpg", "jpeg", "png", "docx", "pdf", "xlsx"],
                accept_multiple_files=True,
                key=f"file_{descripcion_sel}"
            )

            # >>>>>>>>>>>>> CAMBIO: BLOQUE DE SUBIDA A GOOGLE DRIVE <<<<<<<<<<<<<
            from drive_uploader import (
                get_service, ensure_path, upload_file, set_permission_anyone, slugify
            )
            ROOT_FOLDER_ID = st.secrets["DRIVE_ROOT_FOLDER_ID"]  # tu carpeta raíz en Drive

            if archivos_subidos:
                if st.button("Guardar archivo(s)"):
                    service = get_service()
                    if service is None:
                        st.stop()  # esperar autorización de OAuth

                    # Jerarquía en Drive: raiz / sitio / norma / descripcion (slug)
                    dest_folder_id = ensure_path(service, ROOT_FOLDER_ID, [
                        str(sitio_actual),
                        str(norma_actual),
                        slugify(str(descripcion_sel))
                    ])

                    if descripcion_sel not in archivos_evidencia:
                        archivos_evidencia[descripcion_sel] = []

                    tmp_dir = os.path.join("tmp_upload")
                    os.makedirs(tmp_dir, exist_ok=True)

                    for file_obj in archivos_subidos:
                        tmp_path = os.path.join(tmp_dir, file_obj.name)
                        with open(tmp_path, "wb") as f:
                            f.write(file_obj.getbuffer())

                        display_name = (
                            f"{sitio_actual}_{norma_actual}_{slugify(descripcion_sel)}_{file_obj.name}"
                        ).replace(" ", "_")

                        file_id, web_link = upload_file(service, tmp_path, dest_folder_id, display_name)
                        # Abrir por enlace (anyone)
                        set_permission_anyone(service, file_id)

                        archivos_evidencia[descripcion_sel].append(web_link)

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

    # ===== Escenario 2: NO hay respuestas → Mostrar preguntas =====
    else:
        st.markdown("## 📝 Responder Preguntas de Diagnóstico")

        # Detectar la columna de pregunta una sola vez
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
        st.markdown(f"### 📝 Evaluación de Cumplimiento ({cumplimiento:.2f}%)")

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
                    "archivos_evidencia": {}  # vacío (se llenará cuando subas evidencias)
                }, file, indent=4, ensure_ascii=False)
            st.success("✅ Evaluación guardada.")
                       st.rerun()
else:

