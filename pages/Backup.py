import streamlit as st
import pandas as pd
import json
import os
import io

st.set_page_config(page_title="Backup de Diagnósticos EHS", layout="wide")

BASE_DIAG_DIR = "diagnosticos"
DIAG_PREVIOS_FILE = "diagnosticos_guardados.json"

def cargar_diagnosticos_previos():
    if os.path.exists(DIAG_PREVIOS_FILE):
        try:
            with open(DIAG_PREVIOS_FILE, "r", encoding="utf-8") as f:
                contenido = f.read().strip()
                if not contenido:
                    return {}
                return json.loads(contenido)
        except Exception:
            return {}
    return {}

def listar_archivos_diagnosticos():
    archivos = []
    if not os.path.isdir(BASE_DIAG_DIR):
        return archivos
    for norma_folder in os.listdir(BASE_DIAG_DIR):
        norma_path = os.path.join(BASE_DIAG_DIR, norma_folder)
        if not os.path.isdir(norma_path):
            continue
        for fname in os.listdir(norma_path):
            if fname.endswith(".json") and fname.startswith("cumplimiento_"):
                archivos.append(os.path.join(norma_path, fname))
    return archivos

st.markdown("# 💾 Backup de Datos de Cumplimiento EHS")
st.markdown(
    "Esta sección te permite **exportar** todos los diagnósticos (por sitio y norma) "
    "a un archivo Excel para respaldo, y también **importar** ese respaldo para "
    "restaurar la información en una app nueva o vacía."
)
st.markdown("---")

tab_export, tab_import = st.tabs(["📤 Exportar backup", "📥 Importar backup"])

with tab_export:
    st.markdown("## 📤 Exportar base de datos maestra")
    if st.button("Generar archivo de backup (Excel)", use_container_width=True):
        archivos_diag = listar_archivos_diagnosticos()
        diag_previos = cargar_diagnosticos_previos()
        filas_respuestas = []
        filas_resumen = []
        for ruta_json in archivos_diag:
            try:
                with open(ruta_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue
            sitio = data.get("sitio", "")
            norma = data.get("norma", "")
            cumplimiento = data.get("cumplimiento", "")
            respuestas = data.get("respuestas", {})
            filas_resumen.append({
                "sitio": sitio,
                "norma": norma,
                "cumplimiento": cumplimiento
            })
            for descripcion, respuesta in respuestas.items():
                filas_respuestas.append({
                    "sitio": sitio,
                    "norma": norma,
                    "descripcion": descripcion,
                    "respuesta": respuesta,
                    "cumplimiento_total": cumplimiento
                })
        df_respuestas = pd.DataFrame(filas_respuestas)
        df_resumen = pd.DataFrame(filas_resumen).drop_duplicates()
        filas_previos = []
        for sitio, info in diag_previos.items():
            aplican = info.get("aplican", [])
            no_aplican = info.get("no_aplican", [])
            filas_previos.append({
                "sitio": sitio,
                "normas_aplican": ";".join([str(x) for x in aplican]),
                "normas_no_aplican": ";".join([str(x) for x in no_aplican])
            })
        df_previos = pd.DataFrame(filas_previos)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            if not df_respuestas.empty:
                df_respuestas.to_excel(writer, sheet_name="respuestas", index=False)
            if not df_resumen.empty:
                df_resumen.to_excel(writer, sheet_name="resumen_norma", index=False)
            if not df_previos.empty:
                df_previos.to_excel(writer, sheet_name="diagnosticos_previos", index=False)
        buffer.seek(0)
        st.success("✅ Backup generado correctamente.")
        st.download_button(
            "⬇️ Descargar backup_compliance.xlsx",
            data=buffer,
            file_name="backup_compliance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

with tab_import:
    st.markdown("## 📥 Importar backup desde Excel")
    st.markdown(
        "Sube el archivo `backup_compliance.xlsx` generado por esta misma plataforma "
        "para restaurar la información de diagnósticos."
    )
    backup_file = st.file_uploader(
        "Selecciona el archivo de backup (.xlsx)",
        type=["xlsx"]
    )
    if backup_file is not None:
        try:
            xls = pd.ExcelFile(backup_file)
        except Exception as e:
            st.error(f"⚠️ No se pudo leer el archivo: {e}")
            st.stop()
        sheet_names = xls.sheet_names
        if "respuestas" in sheet_names:
            df_resp = pd.read_excel(xls, sheet_name="respuestas")
            if not df_resp.empty:
                os.makedirs(BASE_DIAG_DIR, exist_ok=True)
                grupos = df_resp.groupby(["norma", "sitio"], dropna=True)
                for (norma, sitio), grupo in grupos:
                    norma_str = str(norma)
                    sitio_str = str(sitio)
                    norma_dir = os.path.join(BASE_DIAG_DIR, norma_str)
                    os.makedirs(norma_dir, exist_ok=True)
                    respuestas = dict(zip(
                        grupo["descripcion"].astype(str),
                        grupo["respuesta"].astype(str)
                    ))
                    if "cumplimiento_total" in grupo.columns:
                        cumplimiento_total = str(grupo["cumplimiento_total"].iloc[0])
                    else:
                        total = len(grupo)
                        si_count = (grupo["respuesta"].astype(str).str.lower() == "sí").sum()
                        cumplimiento_val = (si_count / total * 100) if total > 0 else 0
                        cumplimiento_total = f"{cumplimiento_val:.2f}%"
                    data_json = {
                        "sitio": sitio_str,
                        "norma": norma_str,
                        "cumplimiento": cumplimiento_total,
                        "respuestas": respuestas,
                        "archivos_evidencia": {}
                    }
                    fname = f"cumplimiento_{sitio_str}_{norma_str}.json"
                    ruta_salida = os.path.join(norma_dir, fname)
                    with open(ruta_salida, "w", encoding="utf-8") as f:
                        json.dump(data_json, f, indent=4, ensure_ascii=False)
        diag_previos_restaurados = {}
        if "diagnosticos_previos" in sheet_names:
            df_prev = pd.read_excel(xls, sheet_name="diagnosticos_previos")
            for _, row in df_prev.iterrows():
                sitio = str(row.get("sitio", "")).strip()
                if not sitio:
                    continue
                aplican_raw = str(row.get("normas_aplican", "") or "")
                no_aplican_raw = str(row.get("normas_no_aplican", "") or "")
                aplican = [x.strip() for x in aplican_raw.split(";") if x.strip()]
                no_aplican = [x.strip() for x in no_aplican_raw.split(";") if x.strip()]
                diag_previos_restaurados[sitio] = {
                    "aplican": aplican,
                    "no_aplican": no_aplican,
                }
            with open(DIAG_PREVIOS_FILE, "w", encoding="utf-8") as f:
                json.dump(diag_previos_restaurados, f, indent=4, ensure_ascii=False)
        st.success("✅ Backup importado y datos restaurados correctamente.")
        st.info("Ahora puedes ir al módulo de Normativas y ver los diagnósticos como si estuvieran guardados en local.")
