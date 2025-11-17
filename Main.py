import streamlit as st

# Configurar la página
st.set_page_config(page_title="Smart EHS Consulting Platform", layout="wide")

# CSS personalizado
st.markdown(
    """
    <style>
    /* Ocultar la barra nativa de Streamlit (el header con menú) */
    header {visibility: hidden;}

    /* Título principal centrado */
    .title-h1 {
        text-align: center;
        color: #1976D2; /* Azul */
        font-size: 30px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 30px;
    }

    /* Estilo general de los botones (cuadros) */
    .stButton > button {
        background-color: #ff9800; /* Naranja */
        color: white;
        border: none;
        border-radius: 12px;
        padding: 40px 20px;
        font-size: 18px;
        font-weight: bold;
        margin: 20px;
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
st.markdown('<h1 class="title-h1">Smart EHS Consulting '
'platform</h1>', unsafe_allow_html=True)

# Tres columnas para los "cuadros"
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Seguridad Laboral y Riesgos"):
        st.switch_page("Seguridad.py")

with col2:
    if st.button("Normativas y Regulaciones"):
        st.switch_page("pages/Compliance.py")

with col3:
    if st.button("Salud Ocupacional"):
        st.switch_page("Salud.py")


st.markdown("---")
if st.button("🔐 Backup de datos de cumplimiento"):
    st.switch_page("pages/Backup.py")
