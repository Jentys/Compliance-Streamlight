import streamlit as st
import pandas as pd
import os
import json


# Configurar la página
st.set_page_config(page_title="Diagnóstico de Normas STPS", layout="wide")

# Función para cargar preguntas desde Excel
def cargar_preguntas_excel(archivo_excel):
    if os.path.exists(archivo_excel):
        preguntas = {}
        xls = pd.ExcelFile(archivo_excel)

        for hoja in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=hoja)
            preguntas[hoja] = {}

            for _, row in df.iterrows():
                norma = row.iloc[0]  # Primera columna es la norma
                preguntas_lista = [str(p) for p in row.iloc[1:].dropna().tolist()]  # Resto son preguntas

                if norma in preguntas[hoja]:
                    preguntas[hoja][norma].extend(preguntas_lista)
                else:
                    preguntas[hoja][norma] = preguntas_lista
        return preguntas
    return {}

# Función para cargar títulos de normas desde Excel
def cargar_normas_excel(archivo_excel):
    if os.path.exists(archivo_excel):
        df = pd.read_excel(archivo_excel)
        return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))  # Mapea norma → título
    return {}

# Cargar archivos externos
preguntas = cargar_preguntas_excel("preguntas.xlsx")
normas_titulos = cargar_normas_excel("normas_titulos.xlsx")

# Inicializar session_state si no existe
if "opcion" not in st.session_state:
    st.session_state["opcion"] = None

# Menú de opciones
st.markdown("## Plataforma de Cumplimiento EHS")
st.markdown("### Seleccione una opción:")

col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Diagnóstico Nuevo"):
        st.session_state["opcion"] = "Diagnóstico Nuevo"

with col2:
    if st.button("📂 Revisar Diagnósticos Previos"):
        st.session_state["opcion"] = "Revisar Diagnósticos Previos"

st.divider()

# Diagnóstico nuevo
if st.session_state["opcion"] == "Diagnóstico Nuevo":
    st.markdown("## 📝 Diagnóstico Nuevo")
    sitio = st.text_input("📍 Nombre del Sitio:", placeholder="Ejemplo: Planta Monterrey")
    
    if sitio:
        st.markdown("### 🔍 Responde las siguientes preguntas:")
        
        normas_aplicables = []
        normas_no_aplicables = []

        for categoria, normas in preguntas.items():
            st.markdown(f'### {categoria}')
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

        if st.button("📊 Generar Diagnóstico"):
            st.success("✅ Diagnóstico guardado correctamente.")

            # Guardar diagnóstico en un archivo JSON
            diagnosticos_previos = {}
            if os.path.exists("diagnosticos_guardados.json"):
                with open("diagnosticos_guardados.json", "r", encoding="utf-8") as file:
                    diagnosticos_previos = json.load(file)

            diagnosticos_previos[sitio] = {"aplican": normas_aplicables, "no_aplican": normas_no_aplicables}

            with open("diagnosticos_guardados.json", "w", encoding="utf-8") as file:
                json.dump(diagnosticos_previos, file, indent=4)

            st.markdown("### ✅ Normas que aplican:")
            for norma in normas_aplicables:
                titulo = normas_titulos.get(norma, "Título no encontrado")
                st.markdown(f"- **{norma}: {titulo}**")
            
            st.markdown("### ❌ Normas que NO aplican:")
            for norma in normas_no_aplicables:
                titulo = normas_titulos.get(norma, "Título no encontrado")
                st.markdown(f"- {norma}: {titulo}")

# Revisar diagnósticos previos
elif st.session_state["opcion"] == "Revisar Diagnósticos Previos":
    st.markdown("## 📂 Diagnósticos Guardados")
    if os.path.exists("diagnosticos_guardados.json"):
        with open("diagnosticos_guardados.json", "r", encoding="utf-8") as file:
            diagnosticos_previos = json.load(file)

        if diagnosticos_previos:
            sitio_seleccionado = st.selectbox("Seleccione un sitio:", list(diagnosticos_previos.keys()))
            if sitio_seleccionado:
                diagnostico = diagnosticos_previos[sitio_seleccionado]
                st.markdown(f"### 📍 Diagnóstico de {sitio_seleccionado}")

                st.markdown("#### ✅ Normas que aplican:")
                for norma in diagnostico["aplican"]:
                    titulo = normas_titulos.get(norma, "Título no encontrado")
                    st.markdown(f"- **{norma}: {titulo}**")

                st.markdown("#### ❌ Normas que NO aplican:")
                for norma in diagnostico["no_aplican"]:
                    titulo = normas_titulos.get(norma, "Título no encontrado")
                    st.markdown(f"- {norma}: {titulo}")
        else:
            st.warning("⚠️ No hay diagnósticos guardados aún.")
