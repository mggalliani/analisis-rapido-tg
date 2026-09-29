import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuración de página ancha para mejor visualización
st.set_page_config(page_title="Herramientas Departamento Ensayos", layout="wide")

# Menú lateral para separar los entornos
modo = st.sidebar.radio(
    "Seleccione el Entorno de Trabajo:",
    ["📊 Generador de Preinformes", "🎓 Academia PEI (Simulador)"]
)

if modo == "📊 Generador de Preinformes":
    st.title("Preinforme de Ensayos DELTA4000 / TRAX")
    st.info("Aquí irá el código de lectura de archivos .txt y .html que ya venimos desarrollando.")
    # (Tu código actual de lectura y gráficos va exactamente acá)

elif modo == "🎓 Academia MPEI (Simulador)":
    st.title("Simulador de Diagnóstico de Aislación")
    st.markdown("Evalúe las curvas del ensayo y determine el estado del equipo y la acción correctiva correspondiente.")
    st.divider()

    # Generación de casos sintéticos basados en los criterios de Edenor
    escenario = st.selectbox("Seleccionar Escenario de Práctica", ["Caso 1", "Caso 2", "Caso 3"])
    
    # Datos base
    tensiones = np.array([2, 4, 6, 8, 10])
    frecuencias = np.array([505, 300, 150, 70, 35, 15, 5, 2, 1])

    if escenario == "Caso 1":
        # Aislación OK
        tg_tension = np.array([2.5, 2.5, 2.5, 2.5, 2.5])
        tg_frecuencia = np.array([3.8, 3.5, 3.2, 3.0, 2.8, 2.6, 2.5, 2.4, 2.3])
        respuesta_correcta = "Buen estado"
        accion_correcta = "Ninguna (Mantenimiento Normal)"
    
    elif escenario == "Caso 2":
        # Aislación Deteriorada (Humedad) - Tip-Up creciente, alta baja frecuencia
        tg_tension = np.array([7.8, 8.4, 9.0, 9.5, 9.9])
        tg_frecuencia = np.array([3.1, 3.2, 4.0, 5.6, 10.4, 17.5, 35.0, 50.0, 70.0])
        respuesta_correcta = "Aislación deteriorada (Humedad/Envejecimiento)"
        accion_correcta = "Programar reemplazo o tratamiento de aceite"
        
    elif escenario == "Caso 3":
        # Problema de Contacto - Tip-Up decreciente, alta alta frecuencia
        tg_tension = np.array([9.9, 9.2, 8.5, 8.0, 7.9])
        tg_frecuencia = np.array([22.0, 19.5, 15.8, 12.3, 8.5, 6.2, 2.5, 2.4, 2.3])
        respuesta_correcta = "Problema de contacto (Perno/Tap)"
        accion_correcta = "Remedir utilizando el Método Cabezal"

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ensayo Tip-Up (50 Hz)")
        fig_tipup = go.Figure()
        fig_tipup.add_trace(go.Scatter(x=tensiones, y=tg_tension, mode='lines+markers', name="Tg Delta"))
        fig_tipup.update_layout(xaxis_title="Tensión [kV]", yaxis_title="Tangente Delta [x10^-3]")
        st.plotly_chart(fig_tipup, use_container_width=True)

    with col2:
        st.subheader("Espectroscopía Dieléctrica (1 kV)")
        fig_espectro = go.Figure()
        fig_espectro.add_trace(go.Scatter(x=frecuencias, y=tg_frecuencia, mode='lines+markers', name="Tg Delta"))
        fig_espectro.update_layout(xaxis_title="Frecuencia [Hz]", yaxis_title="Tangente Delta [x10^-3]", xaxis_type="log")
        st.plotly_chart(fig_espectro, use_container_width=True)

    # Interfaz del Operario
    st.subheader("Evaluación del Operario")
    diag_user = st.radio("Diagnóstico Principal:", ["Seleccione una opción...", "Buen estado", "Aislación deteriorada (Humedad/Envejecimiento)", "Problema de contacto (Perno/Tap)"])
    accion_user = st.radio("Acción a tomar en campo:", ["Seleccione una opción...", "Ninguna (Mantenimiento Normal)", "Remedir utilizando el Método Cabezal", "Programar reemplazo o tratamiento de aceite"])

    if st.button("Evaluar Resultados"):
        if diag_user == "Seleccione una opción..." or accion_user == "Seleccione una opción...":
            st.warning("Por favor, seleccione un diagnóstico y una acción.")
        elif diag_user == respuesta_correcta and accion_user == accion_correcta:
            st.success("✅ ¡Excelente diagnóstico! La interpretación y la acción de campo son correctas.")
        else:
            st.error("❌ Diagnóstico o acción incorrecta.")
            st.write(f"**Diagnóstico esperado:** {respuesta_correcta}")
            st.write(f"**Acción esperada:** {accion_correcta}")
