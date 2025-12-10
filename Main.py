import streamlit as st

# Configurar la página
st.set_page_config(page_title="Citro-One Safety System 360°", layout="wide")

# CSS personalizado
st.markdown(
    """
    <style>
    header {visibility: hidden;}

    .title-h1 {
        text-align: center;
        color: #1976D2;
        font-size: 30px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 30px;
    }

    .stButton > button {
        background-color: #ff9800;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 40px 20px;
        font-size: 18px;
        font-weight: bold;
        margin: 20px 0px;
        width: 100%;
        height: 120px;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 4px 4px 20px rgba(0,0,0,0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título principal centrado
st.markdown(
    '<h1 class="title-h1">SCitro-One Safety System 360°</h1>',
    unsafe_allow_html=True
)

# ===== Fila 1: tres botones =====
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Seguridad Laboral y Riesgos", use_container_width=True):
        st.switch_page("pages/Seguridad.py")

with col2:
    if st.button("Normativas y Regulaciones", use_container_width=True):
        st.switch_page("pages/Compliance.py")

with col3:
    if st.button("Salud Ocupacional", use_container_width=True):
        st.switch_page("pages/Salud.py")

st.markdown("---")

# ===== Fila 2: botón de Backup centrado =====
bcol1, bcol2, bcol3 = st.columns([1, 1, 1])

with bcol2:  # botón en la columna de en medio
    if st.button("🔐 Backup de datos de cumplimiento", use_container_width=True):
        st.switch_page("pages/Backup.py")
