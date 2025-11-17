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

# Función para cargar el cuestionario de cumplimiento de una norma específica
def cargar_cuestionario_norma(archivo_excel):
    if os.path.exists(archivo_excel):
        df = pd.read_excel(archivo_excel)
        return df
    return None

# Función para cargar los requerimientos y evidencias
def cargar_requerimientos_norma(archivo_csv):
    if os.path.exists(archivo_csv):
        df = pd.read_csv(archivo_csv)
        return df
    return None

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
                if st.button(f"📖 {norma}: {titulo}", key=f"detalle_{norma}"):
                    st.session_state["norma_seleccionada"] = norma
                    st.session_state["titulo_seleccionado"] = titulo
                    st.session_state["sitio"] = sitio
                    st.session_state["opcion"] = "Evaluar Norma"

            st.markdown("### ❌ Normas que NO aplican:")
            for norma in normas_no_aplicables:
                titulo = normas_titulos.get(norma, "Título no encontrado")
                st.markdown(f"- {norma}: {titulo}")

# Evaluación de cumplimiento de la norma
elif st.session_state["opcion"] == "Evaluar Norma":
    norma = st.session_state.get("norma_seleccionada")
    titulo = st.session_state.get("titulo_seleccionado")
    sitio = st.session_state.get("sitio")

    if norma and titulo:
        st.markdown(f"## 📋 Evaluación de {norma}: {titulo}")

        # Cargar el archivo de diagnóstico específico de la norma
        archivo_norma = f"{norma}_diagnostico.csv"
        df_requerimientos = cargar_requerimientos_norma(archivo_norma)

        if df_requerimientos is not None:
            st.markdown("### 🏗️ Requerimientos y Evidencias")
            categorias = df_requerimientos["Categoría"].unique()

            for categoria in categorias:
                st.markdown(f"#### 📌 {categoria}")
                df_categoria = df_requerimientos[df_requerimientos["Categoría"] == categoria]
                
                for _, row in df_categoria.iterrows():
                    st.markdown(f"🔹 **Requerimiento**: {row['Requerimiento']}")
                    st.markdown(f"📎 **Evidencia requerida**: {row['Evidencia']}")
                    st.markdown("---")

            st.markdown("### 📊 Evaluación de Cumplimiento")
            respuestas = {}
            total_preguntas = len(df_requerimientos)
            respuestas_correctas = 0

            for index, row in df_requerimientos.iterrows():
                pregunta = row["Pregunta"]  # Columna de la pregunta
                respuesta = st.radio(f"🔹 {pregunta}", ["No", "Sí", "No aplica"], key=f"{norma}_{index}")
                respuestas[pregunta] = respuesta

                if respuesta == "Sí":
                    respuestas_correctas += 1

            porcentaje_cumplimiento = (respuestas_correctas / total_preguntas) * 100

            if st.button("📊 Generar Evaluación"):
                st.success(f"✅ Cumplimiento: {porcentaje_cumplimiento:.2f}%")

                st.markdown("### 🚨 Acciones recomendadas:")
                for index, row in df_requerimientos.iterrows():
                    pregunta = row["Pregunta"]
                    accion_correctiva = row["Acción Correctiva"]
                    if respuestas[pregunta] == "No":
                        st.markdown(f"🔸 **{pregunta}** → {accion_correctiva}")

    if st.button("🔙 Volver al Diagnóstico"):
        st.session_state["opcion"] = "Diagnóstico Nuevo"