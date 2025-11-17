import streamlit as st 
import json

# Configurar la página
st.set_page_config(page_title="Diagnóstico de Normas STPS", layout="wide")

# Archivo donde se guardarán los diagnósticos previos
DIAGNOSTICOS_FILE = "diagnosticos_guardados.json"

# Cargar diagnósticos previos
try:
    with open(DIAGNOSTICOS_FILE, "r") as file:
        diagnosticos_previos = json.load(file)
except FileNotFoundError:
    diagnosticos_previos = {}

# Diccionario de normas y sus títulos
normas_titulos = {
    "NOM-001-STPS-2008": "Edificios, locales e instalaciones",
    "NOM-002-STPS-2010": "Prevención y protección contra incendios",
    "NOM-004-STPS-1999": "Sistemas y dispositivos de seguridad en maquinaria",
    "NOM-005-STPS-1998": "Manejo, transporte y almacenamiento de sustancias peligrosas",
    "NOM-006-STPS-2023": "Almacenamiento y manejo de materiales mediante el uso de maquinaria",
    "NOM-009-STPS-2011": "Trabajos en altura",
    "NOM-020-STPS-2011": "Recipientes sujetos a presión y calderas",
    "NOM-022-STPS-2015": "Electricidad estática",
    "NOM-027-STPS-2008": "Soldadura y corte",
    "NOM-029-STPS-2011": "Mantenimiento de instalaciones eléctricas",
    "NOM-033-STPS-2015": "Trabajos en espacios confinados",
    "NOM-034-STPS-2016": "Acceso y desarrollo de actividades de trabajadores con discapacidad",
    "NOM-010-STPS-2014": "Agentes químicos contaminantes del ambiente laboral",
    "NOM-011-STPS-2001": "Ruido",
    "NOM-012-STPS-2012": "Radiaciones ionizantes",
    "NOM-013-STPS-1993": "Radiaciones no ionizantes",
    "NOM-014-STPS-2000": "Presiones ambientales anormales",
    "NOM-015-STPS-2001": "Condiciones térmicas elevadas o abatidas",
    "NOM-024-STPS-2001": "Vibraciones",
    "NOM-025-STPS-2008": "Iluminación",
    "NOM-035-STPS-2018": "Factores de Riesgo Psicosocial",
    "NOM-036-STPS-2018": "Factores de riesgo ergonómico. Parte 1: Manejo manual de cargas",
    "NOM-017-STPS-2008": "Equipo de protección personal",
    "NOM-018-STPS-2015": "Comunicación de peligros y riesgos por sustancias químicas",
    "NOM-019-STPS-2011": "Comisiones de seguridad e higiene",
    "NOM-026-STPS-2008": "Colores y señales de seguridad",
    "NOM-028-STPS-2012": "Seguridad en procesos y equipos con sustancias químicas",
    "NOM-030-STPS-2009": "Servicios preventivos de seguridad y salud",
    "NOM-003-STPS-1999": "Plaguicidas y fertilizantes",
    "NOM-007-STPS-2000": "Instalaciones, maquinaria, equipo y herramientas agrícolas",
    "NOM-008-STPS-2013": "Aprovechamiento forestal maderable",
    "NOM-016-STPS-2001": "Operación y mantenimiento de ferrocarriles",
    "NOM-023-STPS-2012": "Trabajos en minas subterráneas y a cielo abierto",
    "NOM-031-STPS-2011": "Construcción",
    "NOM-032-STPS-2008": "Minas subterráneas de carbón",
    "NOM-037-STPS-2023": "Teletrabajo-Condiciones de seguridad y salud en el trabajo"
}

# 🔹 PEGA TU DICCIONARIO DE PREGUNTAS AQUÍ 🔹
preguntas = {
    "Seguridad": {
        "NOM-001-STPS-2008": [
            "¿Su empresa cuenta con un edificio, local o instalación física donde se realicen actividades laborales?",
            "¿El inmueble es utilizado de manera permanente para actividades productivas, comerciales o administrativas?"
        ],
        "NOM-002-STPS-2010": [
            "¿Se almacenan, transportan o utilizan materiales inflamables o combustibles?",
            "¿Cuenta su empresa con equipos eléctricos o fuentes de calor que puedan generar riesgo de incendio?",
            "¿Opera en un edificio cerrado donde un incendio pueda representar un riesgo significativo?"
        ],
        "NOM-004-STPS-1999": [
            "¿Se utilizan máquinas o herramientas con partes móviles en su empresa?",
            "¿Las máquinas utilizadas pueden generar atrapamientos, cortes o proyecciones de material?"
        ],
        "NOM-005-STPS-1998": [
            "¿Se manejan sustancias químicas peligrosas?",
            "¿Se almacenan, transportan o manipulan líquidos, gases o sólidos peligrosos?"
        ],
        "NOM-006-STPS-2023": [
            "¿Se utilizan montacargas, grúas, bandas transportadoras o sistemas automatizados?",
            "¿Se manipulan materiales de gran volumen o peso que requieren maquinaria?"
        ],
        "NOM-009-STPS-2011": [
            "¿Se realizan actividades en alturas mayores a 1.80 metros?",
            "¿Existen estructuras, andamios o plataformas elevadas?"
        ],
        "NOM-020-STPS-2011": [
            "¿Su empresa utiliza calderas, compresores o tanques de almacenamiento de gases a presión?",
            "¿Se cuenta con equipos de generación de vapor, aire comprimido o almacenamiento de gas?"
        ],
        "NOM-022-STPS-2015": [
            "¿Se manejan sustancias inflamables o polvos combustibles en su empresa?",
            "¿Existen procesos en su empresa donde pueda generarse electricidad estática (por ejemplo, trasvase de líquidos inflamables)?"
        ],
        "NOM-027-STPS-2008": [
            "¿Se realizan actividades de soldadura o corte térmico en su empresa?",
            "¿Se utilizan equipos de oxicorte, soldadura eléctrica o autógena en los procesos de producción o mantenimiento?"
        ],
        "NOM-029-STPS-2011": [
            "¿Se realizan trabajos de mantenimiento, instalación o reparación de sistemas eléctricos?",
            "¿Existen tableros eléctricos, subestaciones o redes eléctricas que requieren intervención técnica?"
        ],
        "NOM-033-STPS-2015": [
            "¿Se realizan actividades dentro de tanques, cisternas, túneles, alcantarillas o espacios con acceso limitado?",
            "¿Existen espacios donde la ventilación natural es insuficiente y pueda haber acumulación de gases peligrosos?"
        ],
        "NOM-034-STPS-2016": [
            "¿Su empresa tiene trabajadores con discapacidad?",
            "¿Se cuenta con infraestructura o procesos que requieran adecuaciones para trabajadores con discapacidad?"
        ]
    },
    "Salud": {
        "NOM-010-STPS-2014": [
            "¿Se generan vapores, polvos, humos o gases en el ambiente laboral?",
            "¿Se utilizan sustancias químicas peligrosas con riesgo de exposición prolongada?"
        ],
        "NOM-011-STPS-2001": [
            "¿Existen áreas donde el ruido dificulta la comunicación verbal?",
            "¿Se usan herramientas o maquinaria que generen altos niveles de ruido?"
        ],
        "NOM-012-STPS-2012": [
            "¿Se utilizan equipos emisores de radiaciones ionizantes?",
            "¿Existen áreas de trabajo donde el personal pueda estar expuesto a este tipo de radiaciones?"
        ],
        "NOM-013-STPS-1993": [
            "¿Se utilizan fuentes de radiación no ionizante como microondas, ultravioleta o infrarrojo?",
            "¿Los trabajadores están expuestos frecuentemente a estas fuentes de radiación?"
        ],
        "NOM-014-STPS-2000": [
            "¿Se realizan actividades en altitudes superiores a 1,800 metros sobre el nivel del mar o en ambientes hiperbáricos?",
            "¿Los trabajadores están expuestos a variaciones de presión ambiental que puedan afectar su salud?"
        ],
        "NOM-015-STPS-2001": [
            "¿Los trabajadores en su empresa están expuestos a temperaturas extremas (altas o bajas) de forma constante?",
            "¿Existen áreas donde el calor o el frío representan un riesgo para la salud?"
        ],
        "NOM-024-STPS-2001": [
            "¿SEn su empresa se utilizan equipos o maquinaria que generen vibraciones constantes?",
            "¿Los trabajadores deben manipular herramientas eléctricas o vehículos que transmitan vibraciones al cuerpo?"
        ],
        "NOM-025-STPS-2008": [
            "¿Existen áreas de trabajo donde la iluminación es deficiente o excesiva?",
            "¿Los trabajadores realizan tareas que requieren precisión visual en condiciones de iluminación no controladas?"
        ],
        "NOM-035-STPS-2018": [
            "¿En su empresa los trabajadores están sujetos a cargas de trabajo excesivas, violencia laboral o estrés crónico?",
            "¿Se han identificado problemas de salud mental o agotamiento emocional en el personal?"
        ],
        "NOM-036-STPS-2018": [
            "¿En su empresa los trabajadores deben levantar, cargar o transportar objetos pesados manualmente?",
            "¿Existen actividades donde la postura de trabajo pueda causar lesiones musculoesqueléticas?"
        ]
    },
    "Organización": {
        "NOM-017-STPS-2008": [
            "¿Existen actividades donde los trabajadores están expuestos a riesgos físicos, químicos o biológicos?",
            "¿Se requiere el uso de equipo de protección personal como cascos, guantes o lentes?"
        ],
        "NOM-018-STPS-2015": [
            "¿Su empresa maneja sustancias químicas peligrosas en su operación diaria?",
            "¿Es necesario identificar y comunicar los riesgos de estas sustancias al personal?"
        ],
        "NOM-019-STPS-2011": [
            "¿Su empresa tiene más de 50 trabajadores?",
            "¿Se requiere implementar una Comisión de Seguridad e Higiene?"
        ]
    },
    "Específicas": {
        "NOM-007-STPS-2000": [
            "¿Se realizan actividades agrícolas con maquinaria especializada?"
        ],
        "NOM-008-STPS-2013": [
            "¿Se realizan trabajos de tala, aserrado o procesamiento de madera en bosques?"
        ],
        "NOM-016-STPS-2001": [
            "¿Su empresa opera o realiza mantenimiento de infraestructura ferroviaria?"
        ],
        "NOM-031-STPS-2011": [
            "¿Su empresa se dedica a actividades de construcción?"
        ],
        "NOM-037-STPS-2023": [
            "¿Su empresa tiene empleados que trabajan desde casa (teletrabajo)?"
        ]
    }
}

# Inicializar session_state si no existe
if "opcion" not in st.session_state:
    st.session_state["opcion"] = None

# Menú de opciones
st.markdown("## Plataforma de Cumplimiento EHS")
st.markdown("### Seleccione una opción:")

# Botón de Diagnóstico Nuevo
if st.button("📋 Diagnóstico Nuevo"):
    st.session_state["opcion"] = "Diagnóstico Nuevo"

# Espacio para separar visualmente
st.markdown("<br>", unsafe_allow_html=True)

# Botón de Revisar Diagnósticos Previos (ahora debajo)
if st.button("📂 Revisar Diagnósticos Previos"):
    st.session_state["opcion"] = "Revisar Diagnósticos Previos"

st.divider()  # Línea divisoria para separar visualmente

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
            diagnosticos_previos[sitio] = {"aplican": normas_aplicables, "no_aplican": normas_no_aplicables}
            with open(DIAGNOSTICOS_FILE, "w") as file:
                json.dump(diagnosticos_previos, file)
            
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
