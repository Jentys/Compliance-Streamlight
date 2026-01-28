import streamlit as st

st.set_page_config(page_title="Analytics & Reportes", layout="wide")

st.markdown(
    """
    <style>
        header {visibility: hidden;}

        :root {
            --primary: #008ab8;
            --background-light: #f5f8f8;
            --text-dark: #0c181d;
            --text-muted: #458aa1;
            --card-border: #cde2ea;
            --accent-success: #078836;
            --accent-warning: #f59e0b;
            --accent-danger: #e73508;
        }

        body {
            font-family: 'Public Sans', sans-serif;
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
            font-size: 20px;
            font-weight: 700;
            color: var(--text-dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(7, 136, 54, 0.1);
            color: var(--accent-success);
            font-size: 11px;
            font-weight: 700;
        }

        .nav-action .stButton > button {
            border-radius: 999px;
            padding: 8px 14px;
            border: 1px solid var(--card-border);
            background: #f8fbfc;
            color: var(--text-dark);
            font-weight: 600;
        }

        .nav-action .stButton > button:hover {
            border-color: var(--primary);
            color: var(--primary);
        }

        .hero-title {
            font-size: 32px;
            font-weight: 800;
            color: var(--text-dark);
            margin-bottom: 4px;
        }

        .hero-subtitle {
            color: var(--text-muted);
            font-size: 14px;
        }

        .card {
            background: white;
            border-radius: 16px;
            border: 1px solid var(--card-border);
            padding: 20px;
            box-shadow: 0 6px 16px rgba(12, 24, 29, 0.04);
        }

        .metric-label {
            color: var(--text-muted);
            font-size: 12px;
            font-weight: 600;
        }

        .metric-value {
            font-size: 28px;
            font-weight: 800;
            color: var(--text-dark);
        }

        .metric-pill {
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 999px;
            background: rgba(0, 138, 184, 0.1);
            color: var(--primary);
        }

        .progress-track {
            height: 8px;
            background: #e6f1f4;
            border-radius: 999px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: var(--primary);
            border-radius: 999px;
        }

        .subtle-divider {
            height: 1px;
            background: #cde2ea;
            margin: 24px 0;
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="top-nav">', unsafe_allow_html=True)
nav_left, nav_right = st.columns([0.7, 0.3])
with nav_left:
    st.markdown(
        '<div class="nav-title"><span class="material-icons-round" style="color:#008ab8;">bar_chart</span>Compliance Analytics</div>',
        unsafe_allow_html=True,
    )
with nav_right:
    st.markdown('<div style="display:flex; gap:12px; justify-content:flex-end;">', unsafe_allow_html=True)
    st.markdown('<span class="status-pill">LIVE DATA</span>', unsafe_allow_html=True)
    st.markdown('<div class="nav-action">', unsafe_allow_html=True)
    if st.button("← Volver a Compliance"):
        st.switch_page("pages/Compliance.py")
    st.markdown("</div></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div>
        <div class="hero-title">Reports & Analytics</div>
        <div class="hero-subtitle">Vista general de cumplimiento para el sitio seleccionado.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

filters_left, filters_right = st.columns([0.6, 0.4])
with filters_left:
    st.selectbox(
        "Sitio industrial",
        ["Planta Monterrey", "Centro Querétaro", "Fábrica Guadalajara", "Centro Puebla"],
    )
with filters_right:
    st.text_input("Buscar indicador", placeholder="Buscar parámetros...")

st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)

metrics = st.columns(3)
with metrics[0]:
    st.markdown(
        """
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div class="metric-label">Cumplimiento general</div>
                <span class="metric-pill">+5.2%</span>
            </div>
            <div class="metric-value">85.4%</div>
            <div class="progress-track" style="margin-top:12px;">
                <div class="progress-fill" style="width:85%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metrics[1]:
    st.markdown(
        """
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div class="metric-label">No conformidades críticas</div>
                <span class="metric-pill" style="background: rgba(231, 53, 8, 0.1); color: var(--accent-danger);">-2 items</span>
            </div>
            <div class="metric-value" style="color: var(--accent-danger);">12</div>
            <div class="hero-subtitle" style="margin-top:10px;">Requiere atención en zona C</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with metrics[2]:
    st.markdown(
        """
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div class="metric-label">Ítems inspeccionados</div>
                <span class="metric-pill">Mes actual</span>
            </div>
            <div class="metric-value">1,240</div>
            <div class="hero-subtitle" style="margin-top:10px;">98.5% de auditorías completadas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

section_left, section_right = st.columns([0.65, 0.35])
with section_left:
    st.markdown(
        """
        <div class="card">
            <h3 style="margin-top:0;">Performance global</h3>
            <div style="display:flex; gap:24px; align-items:center;">
                <div style="width:180px; height:180px; border-radius:50%; border:14px solid #e6f1f4; position:relative;">
                    <div style="position:absolute; inset:0; border-radius:50%; border:14px solid #008ab8; clip-path: inset(0 0 35% 0);"></div>
                    <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                        <div class="metric-value">85%</div>
                        <div class="metric-label">Score global</div>
                    </div>
                </div>
                <div style="flex:1;">
                    <div style="margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between;">
                            <span class="metric-label">Normas seguridad</span>
                            <strong>92%</strong>
                        </div>
                        <div class="progress-track"><div class="progress-fill" style="width:92%; background: var(--accent-success);"></div></div>
                    </div>
                    <div style="margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between;">
                            <span class="metric-label">Salud ocupacional</span>
                            <strong>78%</strong>
                        </div>
                        <div class="progress-track"><div class="progress-fill" style="width:78%; background: var(--accent-warning);"></div></div>
                    </div>
                    <div>
                        <div style="display:flex; justify-content:space-between;">
                            <span class="metric-label">Gestión documental</span>
                            <strong>88%</strong>
                        </div>
                        <div class="progress-track"><div class="progress-fill" style="width:88%;"></div></div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with section_right:
    st.markdown(
        """
        <div class="card">
            <h3 style="margin-top:0;">Acciones rápidas</h3>
            <ul style="padding-left:18px; color: var(--text-muted); font-size: 14px; line-height:1.8;">
                <li>Exportar reporte ejecutivo en PDF.</li>
                <li>Comparar avances trimestrales.</li>
                <li>Revisar no conformidades críticas.</li>
                <li>Actualizar criterios del sitio.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="subtle-divider"></div>', unsafe_allow_html=True)

actions_left, actions_right = st.columns([0.7, 0.3])
with actions_left:
    st.markdown(
        """
        <div class="card">
            <h3 style="margin-top:0;">Últimos reportes generados</h3>
            <div style="display:flex; flex-direction:column; gap:12px;">
                <div style="display:flex; justify-content:space-between;">
                    <span>Reporte Ejecutivo - Septiembre</span>
                    <span class="metric-label">PDF • 4.2 MB</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span>Resumen NOM Críticas - Agosto</span>
                    <span class="metric-label">PDF • 3.8 MB</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span>Indicadores de Auditoría - Julio</span>
                    <span class="metric-label">PDF • 5.1 MB</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with actions_right:
    st.markdown(
        """
        <div class="card">
            <h3 style="margin-top:0;">Descargar</h3>
            <div class="hero-subtitle" style="margin-bottom:12px;">
                Genera reportes en formatos listos para auditorías.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button("Exportar PDF", data=b"", file_name="reporte.pdf")
    st.download_button("Exportar CSV", data=b"", file_name="reporte.csv")
