import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="Diagnóstico de Normas STPS", layout="wide")

st.session_state.setdefault("opcion", None)

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
            font-size: 22px;
            font-weight: 700;
            color: var(--text-dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .nav-action .stButton > button {
            width: 100%;
            border-radius: 999px;
            padding: 8px 16px;
            border: 1px solid var(--card-border);
            background: #F8FAFC;
            color: var(--text-dark);
            font-weight: 600;
        }

        .nav-action .stButton > button:hover {
            border-color: var(--primary);
            color: var(--primary);
        }

        .hero {
            margin-bottom: 24px;
        }

        .hero-title {
            font-size: 30px;
            font-weight: 800;
            color: var(--text-dark);
            margin-bottom: 6px;
        }

        .hero-subtitle {
            font-size: 15px;
            color: var(--text-muted);
            max-width: 720px;
        }

        .menu-card {
            background: white;
            border: 2px solid #F1F5F9;
            border-radius: 24px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            height: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        }

        .menu-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
            border-color: var(--primary);
        }

        .menu-icon {
            width: 56px;
            height: 56px;
            border-radius: 18px;
            background: rgba(0, 140, 186, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            font-size: 28px;
        }

        .menu-title {
            font-size: 22px;
            font-weight: 700;
            color: var(--text-dark);
            margin: 0;
        }

        .menu-description {
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
            margin: 0;
            flex-grow: 1;
        }

        .primary-action .stButton > button,
        .secondary-action .stButton > button {
            width: 100%;
            border-radius: 14px;
            padding: 12px 18px;
            font-weight: 600;
            border: none;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .primary-action .stButton > button {
            background: var(--primary);
            color: white;
        }

        .primary-action .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 16px rgba(0, 140, 186, 0.25);
        }

        .secondary-action .stButton > button {
            background: #E2E8F0;
            color: var(--text-dark);
        }

        .secondary-action .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 16px rgba(148, 163, 184, 0.35);
        }

        .content-card {
            background: white;
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 24px;
            margin-top: 16px;
        }

        .section-title {
            font-size: 20px;
            font-weight: 700;
            color: var(--text-dark);
            margin-bottom: 12px;
        }

        .subtle-divider {
            height: 1px;
            background: #E2E8F0;
            margin: 24px 0;
        }

        @media (max-width: 768px) {
            .top-nav {
                padding: 16px 20px;
                margin: 0 -8px 20px -8px;
            }

            .hero-title {
                font-size: 24px;
            }
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="top-nav">', unsafe_allow_html=True)
nav_left, nav_right = st.columns([0.75, 0.25])
with nav_left:
    st.markdown(
        '<div class="nav-title"><span class="material-icons-round" style="color:#008CBA;">fact_check</span>Diagnóstico de Normas STPS</div>',
        unsafe_allow_html=True,
    )
with nav_right:
    st.markdown('<div class="nav-action">', unsafe_allow_html=True)
    if st.button("← Regresar al Inicio", use_container_width=True):
        st.session_state["opcion"] = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Gestiona tus diagnósticos de cumplimiento</div>
        <div class="hero-subtitle">
            Crea nuevas evaluaciones, consulta historiales y administra el avance de
            cumplimiento de las normas STPS en tu organización.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

menu_left, menu_right = st.columns(2, gap="large")
with menu_left:
    st.markdown(
        """
        <div class="menu-card">
            <div class="menu-icon"><span class="material-icons-round">add_circle_outline</span></div>
            <h3 class="menu-title">Nuevo Diagnóstico</h3>
            <p class="menu-description">
                Inicia una nueva evaluación guiada para tu sitio y registra las normas
                aplicables desde cero.
            </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="primary-action">', unsafe_allow_html=True)
    if st.button("Comenzar evaluación", key="nuevo_diagnostico", use_container_width=True):
        st.session_state["opcion"] = "Diagnóstico Nuevo"
        st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

with menu_right:
    st.markdown(
        """
        <div class="menu-card">
            <div class="menu-icon"><span class="material-icons-round">folder_open</span></div>
            <h3 class="menu-title">Diagnósticos Previos</h3>
            <p class="menu-description">
                Revisa historiales existentes, descarga reportes y continúa evaluaciones
                guardadas.
            </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="secondary-action">', unsafe_allow_html=True)
    if st.button("Ver historial", key="diagnosticos_previos", use_container_width=True):
        st.session_state["opcion"] = "Revisar Diagnósticos Previos"
        st.rerun()
    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)

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
        return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
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

# =============================================================================
# 1) Diagnóstico Nuevo
# =============================================================================
if st.session_state.get("opcion") == "Diagnóstico Nuevo":
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Diagnóstico Nuevo</div>', unsafe_allow_html=True)
    sitio = st.text_input("📍 Nombre del Sitio:", placeholder="Ejemplo: Planta Monterrey")

    if sitio:
        st.session_state["sitio_actual"] = sitio
        st.markdown("#### 🔍 Responde las siguientes preguntas:")
        normas_aplicables = []
        normas_no_aplicables = []

        for categoria, normas in preguntas.items():
            st.markdown(f"#### {categoria}")
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

        st.markdown('<div class="primary-action">', unsafe_allow_html=True)
        if st.button("📊 Guardar Diagnóstico", use_container_width=True):
            diagnosticos_previos[sitio] = {
                "aplican": normas_aplicables,
                "no_aplican": normas_no_aplicables,
            }
            with open("diagnosticos_guardados.json", "w", encoding="utf-8") as file:
                json.dump(diagnosticos_previos, file, indent=4)
            st.success("✅ Diagnóstico guardado correctamente.")
            st.session_state["opcion"] = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 2) Revisar Diagnósticos Previos
# =============================================================================
elif st.session_state.get("opcion") == "Revisar Diagnósticos Previos":
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📂 Diagnósticos Guardados</div>', unsafe_allow_html=True)
    if diagnosticos_previos:
        sitio_seleccionado = st.selectbox("📂 Seleccione un sitio:", list(diagnosticos_previos.keys()))
        if sitio_seleccionado:
            st.session_state["sitio_actual"] = sitio_seleccionado
            diagnostico = diagnosticos_previos[sitio_seleccionado]

            top_left, top_right = st.columns([0.75, 0.25])
            with top_left:
                st.markdown(f"### 📍 Diagnóstico de {sitio_seleccionado}")
            with top_right:
                st.markdown('<div class="secondary-action">', unsafe_allow_html=True)
                if st.button("🗑️ Borrar Diagnóstico", key=f"borrar_{sitio_seleccionado}"):
                    del diagnosticos_previos[sitio_seleccionado]
                    with open("diagnosticos_guardados.json", "w", encoding="utf-8") as file:
                        json.dump(diagnosticos_previos, file, indent=4)
                    st.success("🚮 Diagnóstico eliminado correctamente.")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")

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
    st.markdown("</div>", unsafe_allow_html=True)
