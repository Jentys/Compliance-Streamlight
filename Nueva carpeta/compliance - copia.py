import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

# Configurar la página
st.set_page_config(page_title="Diagnóstico de Normas STPS", layout="wide")

# Estilos mejorados
st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            padding-top: 10px;
        }
        .subheader {
            font-size: 22px;
            font-weight: bold;
            margin-top: 20px;
            color: #1976D2;
        }
        .norma-title {
            font-size: 18px;
            font-weight: bold;
            margin-top: 15px;
            padding: 5px;
            border-left: 5px solid #1976D2;
            background-color: #f8f8f8;
        }
    </style>
    """, unsafe_allow_html=True
)

# Título principal
st.markdown('<div class="main-title">Plataforma de Cumplimiento EHS - Diagnóstico Compliance</div>', unsafe_allow_html=True)

# Ingreso del nombre del sitio
sitio = st.text_input("📍 Nombre del Sitio:", placeholder="Ejemplo: Planta Monterrey")

st.markdown('<div class="subheader">📝 Responde las siguientes preguntas para determinar qué normas aplican:</div>', unsafe_allow_html=True)

# Diccionario completo con TODAS las normas
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

# Guardar respuestas
normas_aplicables = []
for categoria, normas in preguntas.items():
    st.markdown(f'<div class="subheader">{categoria}</div>', unsafe_allow_html=True)
    for norma, preguntas_lista in normas.items():
        st.markdown(f'<div class="norma-title">{norma}</div>', unsafe_allow_html=True)
        for pregunta in preguntas_lista:
            respuesta = st.radio(f"🔹 {pregunta}", ("No", "Sí"), key=f"{norma}_{pregunta}")
            if respuesta == "Sí" and norma not in normas_aplicables:
                normas_aplicables.append(norma)

# Confirmar y descargar diagnóstico
if st.button("📊 Generar Diagnóstico"):
    st.success("✅ Diagnóstico completado.")
    for norma in normas_aplicables:
        st.markdown(f"- ✅ **{norma}**")

