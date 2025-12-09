import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="Diagnóstico de Normas STPS", layout="wide")

# -----------------------------------------------------------------------------
# BLOQUE DE ESTILO (CSS) PARA BOTONES
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Estiliza todos los botones en la aplicación */
    .stButton > button {
        background-color: #E0F2FF;
        color: black;
        border-radius: 8px;
        border: 1px solid #008CBA;
        padding: 6px 12px;
        font-weight: 600;
        transition: background-color 0.3s, color 0.3s;
    }
    .stButton > button:hover {
        background-color: #008CBA;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# Funciones para cargar datos desde Excel
# -----------------------------------------------------------------------------
def cargar_preguntas_excel(archivo_excel):
    if os.path.exists(archivo_excel):
        preguntas = {}
        xls = pd.ExcelFile(archivo_excel)
        for hoja in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=hoja)
            preguntas[hoja] = {}
            for _, row in df.iterrows():
                norma = row.iloc[0]
                preguntas_lista = [str(p) for p in row.iloc[1:].dropna().tolist()]
                if norma in preguntas[hoja]:
                    preguntas[hoja][norma].extend(preguntas_lista)
                else:
                    preguntas[hoja][norma] = preguntas_lista
        return preguntas
    return {}

def cargar_normas_excel(archivo_excel):
    if os.path.exists(archivo_excel):
        df = pd.read_excel(archivo_excel)
        return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))  # Mapea norma → título
    return {}

# -----------------------------------------------------------------------------
# Cargar archivos externos y diagnósticos guardados
# -----------------------------------------------------------------------------
preguntas = cargar_preguntas_excel("preguntas.xlsx")
normas_titulos = cargar_normas_excel("normas_titulos.xlsx")

if os.path.exists("diagnosticos_guardados.json"):
    with open("diagnosticos_guardados.json", "r", encoding="utf-8") as file:
        diagnosticos_previos = json.load(file)
else:
    diagnosticos_previos = {}

# -----------------------------------------------------------------------------
# INTERFAZ PRINCIPAL
# -----------------------------------------------------------------------------

# 1. Encabezado con el botón de "Regresar" en la parte superior (volver al menú principal)
header_left, header_right = st.columns([0.8, 0.2])
with header_left:
    st.markdown("# 📋 Diagnóstico de Normas STPS")
with header_right:
    if st.button("← Regresar al Inicio"):
        st.session_state["opcion"] = None
        st.rerun()

st.markdown("---")

# 2. Selección de opciones
st.markdown("### Seleccione una opción:")
col1, col2 = st.columns(2)
with col1:
    if st.button("🆕 Nuevo Diagnóstico", use_container_width=True):
        st.session_state["opcion"] = "Diagnóstico Nuevo"
        st.rerun()
with col2:
    if st.button("📂 Diagnósticos Previos", use_container_width=True):
        st.session_state["opcion"] = "Revisar Diagnósticos Previos"
        st.rerun()

st.markdown("---")

# =============================================================================
# 1) Diagnóstico Nuevo
# =============================================================================
if st.session_state.get("opcion") == "Diagnóstico Nuevo":
    st.markdown("## 📝 Diagnóstico Nuevo")
    sitio = st.text_input("📍 Nombre del Sitio:", placeholder="Ejemplo: Planta Monterrey")

    if sitio:
        st.session_state["sitio_actual"] = sitio
        st.markdown("### 🔍 Responde las siguientes preguntas:")
        normas_aplicables = []
        normas_no_aplicables = []

        # Recorremos cada categoría y norma
        for categoria, normas in preguntas.items():
            st.markdown(f'#### {categoria}')
            for norma, preguntas_lista in normas.items():
                aplica = False
                for pregunta in preguntas_lista:
                    respuesta = st.radio(f"🔹 {pregunta}", ("No", "Sí"), key=f"{norma}_{pregunta}")
                    if respuesta == "Sí":
                        aplica = True
                if aplica:
                    normas_aplicables.append(norma)
                else:
                    normas_no_aplicables.append(norma)

        if st.button("📊 Guardar Diagnóstico", use_container_width=True):
            diagnosticos_previos[sitio] = {"aplican": normas_aplicables, "no_aplican": normas_no_aplicables}
            with open("diagnosticos_guardados.json", "w", encoding="utf-8") as file:
                json.dump(diagnosticos_previos, file, indent=4)
            st.success("✅ Diagnóstico guardado correctamente.")
            # Se reinicia la opción para volver al menú principal y se refresca la app
            st.session_state["opcion"] = None
            st.rerun()

# =============================================================================
# 2) Revisar Diagnósticos Previos
# =============================================================================
elif st.session_state.get("opcion") == "Revisar Diagnósticos Previos":
    st.markdown("## 📂 Diagnósticos Guardados")
    if diagnosticos_previos:
        # Selección de sitio
        sitio_seleccionado = st.selectbox("📂 Seleccione un sitio:", list(diagnosticos_previos.keys()))
        if sitio_seleccionado:
            st.session_state["sitio_actual"] = sitio_seleccionado
            diagnostico = diagnosticos_previos[sitio_seleccionado]

            # Encabezado y botón de eliminar en la parte superior derecha
            top_left, top_right = st.columns([0.8, 0.2])
            with top_left:
                st.markdown(f"### 📍 Diagnóstico de {sitio_seleccionado}")
            with top_right:
                if st.button("🗑️ Borrar Diagnóstico", key=f"borrar_{sitio_seleccionado}"):
                    del diagnosticos_previos[sitio_seleccionado]
                    with open("diagnosticos_guardados.json", "w", encoding="utf-8") as file:
                        json.dump(diagnosticos_previos, file, indent=4)
                    st.success("🚮 Diagnóstico eliminado correctamente.")
                    st.rerun()

            st.markdown("---")

            # Sección de Normas que aplican (siempre visible)
            st.markdown("### ✅ Normas que aplican:")
            if diagnostico["aplican"]:
                for norma in diagnostico["aplican"]:
                    if pd.isna(norma) or not str(norma).strip():
                        st.warning("⚠️ Esta norma no tiene un identificador válido y no se puede evaluar.")
                        continue
                    titulo = normas_titulos.get(norma, "Título no encontrado")
                    if st.button(f"📖 Evaluar {norma}: {titulo}", key=f"evaluar_{str(norma).strip()}"):
                        st.session_state["norma_actual"] = norma
                        st.switch_page("pages/Evaluacion_Norma.py")
            else:
                st.info("No se encontraron normas que apliquen.")

            # Sección de Normas que NO aplican (con expander)
            with st.expander("❌ Normas que NO aplican"):
                if diagnostico["no_aplican"]:
                    for norma in diagnostico["no_aplican"]:
                        if pd.isna(norma) or not str(norma).strip():
                            st.warning("⚠️ Esta norma no tiene un identificador válido.")
                            continue
                        titulo = normas_titulos.get(norma, "Título no encontrado")
                        st.write(f"**{norma}**: {titulo}")
                else:
                    st.info("No se encontraron normas marcadas como 'no aplican'.")
    else:
        st.warning("⚠️ No hay diagnósticos guardados aún.")
