import streamlit as st

st.set_page_config(page_title="Citro-One Safety System 360°", layout="wide")

st.markdown(
    """
    <style>
        header {visibility: hidden;}

        :root {
            --primary: #008CBA;
            --background-light: #F8FAFC;
            --background-dark: #0F172A;
            --text-dark: #0F172A;
            --text-muted: #64748B;
            --card-border: #E2E8F0;
        }

        body {
            font-family: 'Inter', sans-serif;
        }

        .app-shell {
            background: var(--background-light);
            padding: 0 0 40px 0;
        }

        .top-nav {
            position: sticky;
            top: 0;
            z-index: 10;
            background: white;
            border-bottom: 1px solid var(--card-border);
            padding: 18px 32px;
            margin: 0 -16px 32px -16px;
        }

        .top-nav h1 {
            font-size: 22px;
            font-weight: 700;
            color: var(--text-dark);
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 0;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            background: #F1F5F9;
            border-radius: 999px;
            border: 1px solid #E2E8F0;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: #22C55E;
        }

        .hero {
            margin-bottom: 32px;
        }

        .hero-title {
            font-size: 32px;
            font-weight: 800;
            color: var(--text-dark);
            margin-bottom: 8px;
        }

        .hero-subtitle {
            font-size: 16px;
            color: var(--text-muted);
            max-width: 720px;
        }

        .menu-card {
            background: white;
            border: 2px solid #F1F5F9;
            border-radius: 24px;
            padding: 28px;
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

        .menu-action .stButton > button {
            width: 100%;
            border-radius: 14px;
            padding: 12px 18px;
            background: var(--primary);
            color: white;
            border: none;
            font-weight: 600;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .menu-action .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 16px rgba(0, 140, 186, 0.25);
        }

        .footer {
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #E2E8F0;
            display: flex;
            flex-wrap: wrap;
            gap: 24px;
            align-items: center;
            justify-content: space-between;
            color: var(--text-muted);
            font-size: 12px;
        }

        .footer strong {
            color: var(--text-dark);
        }

        @media (max-width: 768px) {
            .top-nav {
                padding: 16px 20px;
                margin: 0 -8px 24px -8px;
            }

            .hero-title {
                font-size: 26px;
            }
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="top-nav">
        <div style="display:flex; align-items:center; justify-content:space-between; gap:16px;">
            <h1><span class="material-icons-round" style="color:#008CBA;">fact_check</span>Citro-One Safety System 360°</h1>
            <span class="status-pill"><span class="status-dot"></span>Sistema activo</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Bienvenido al Portal de Cumplimiento</div>
        <div class="hero-subtitle">
            Administra diagnósticos, normativas y respaldo documental desde un solo lugar.
            Selecciona un módulo para continuar con tu evaluación o gestión de riesgos.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        """
        <div class="menu-card">
            <div class="menu-icon"><span class="material-icons-round">shield</span></div>
            <h3 class="menu-title">Seguridad Laboral y Riesgos</h3>
            <p class="menu-description">
                Evalúa los riesgos operativos, gestiona protocolos preventivos y
                da seguimiento a los planes de acción de seguridad industrial.
            </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="menu-action">', unsafe_allow_html=True)
    if st.button("Abrir módulo", key="seguridad", use_container_width=True):
        st.switch_page("pages/Seguridad.py")
    st.markdown("</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div class="menu-card">
            <div class="menu-icon"><span class="material-icons-round">gavel</span></div>
            <h3 class="menu-title">Normativas y Regulaciones</h3>
            <p class="menu-description">
                Consulta el cumplimiento de las NOM vigentes, administra tus diagnósticos
                y genera reportes listos para auditoría.
            </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="menu-action">', unsafe_allow_html=True)
    if st.button("Gestionar normativas", key="compliance", use_container_width=True):
        st.switch_page("pages/Compliance.py")
    st.markdown("</div></div>", unsafe_allow_html=True)

col3, col4 = st.columns(2, gap="large")

with col3:
    st.markdown(
        """
        <div class="menu-card">
            <div class="menu-icon"><span class="material-icons-round">health_and_safety</span></div>
            <h3 class="menu-title">Salud Ocupacional</h3>
            <p class="menu-description">
                Monitorea indicadores de salud, controla evaluaciones médicas y gestiona
                campañas preventivas para tu personal.
            </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="menu-action">', unsafe_allow_html=True)
    if st.button("Ver salud ocupacional", key="salud", use_container_width=True):
        st.switch_page("pages/Salud.py")
    st.markdown("</div></div>", unsafe_allow_html=True)

with col4:
    st.markdown(
        """
        <div class="menu-card">
            <div class="menu-icon"><span class="material-icons-round">cloud_done</span></div>
            <h3 class="menu-title">Respaldo de Información</h3>
            <p class="menu-description">
                Protege la información crítica de cumplimiento y descarga un respaldo
                seguro de tus diagnósticos y evidencias.
            </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="menu-action">', unsafe_allow_html=True)
    if st.button("Generar backup", key="backup", use_container_width=True):
        st.switch_page("pages/Backup.py")
    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer">
        <div>
            <span style="text-transform:uppercase; letter-spacing:0.12em; font-size:10px;">Última actualización</span><br/>
            <strong>Octubre 2024 • 09:45</strong>
        </div>
        <div>
            <span style="text-transform:uppercase; letter-spacing:0.12em; font-size:10px;">Versión del sistema</span><br/>
            <strong>v3.0.0</strong>
        </div>
        <div>
            Desarrollado por <strong>Citro-One</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
