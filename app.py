import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(page_title="Herramientas PEI - Edenor", layout="wide")

# Menú lateral para separar los entornos
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Edenor_logo.svg/2560px-Edenor_logo.svg.png", width=150)
st.sidebar.title("Departamento de Ensayos")
modo = st.sidebar.radio(
    "Seleccione el Entorno:",
    ["📊 Generador de Preinformes", "🎓 Academia PEI (Simulador)"]
)

if modo == "📊 Generador de Preinformes":
    st.title("Preinforme de Ensayos de Tangente Delta")
    st.markdown("Procesamiento automático de archivos de exportación de equipos de ensayo.")

    archivo_subido = st.file_uploader("Cargar archivo de ensayo (.txt)", type=["txt"])

    if archivo_subido is not None:
        # Lectura y limpieza de datos
        df = pd.read_csv(archivo_subido, sep='\t', decimal='.', encoding='utf-8', on_bad_lines='skip')
        df.columns = [" ".join(str(col).split()) for col in df.columns]
        
        if 'Time' not in df.columns or 'Sweep Mode' not in df.columns:
            st.error(f"🚨 Problema de lectura. Las columnas detectadas en tu archivo son: {df.columns.tolist()}")
            st.stop()
        
        df = df.dropna(subset=['Time', 'Sweep Mode'])
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        
        if 'U(kV)' in df.columns:
            df['U(kV)'] = pd.to_numeric(df['U(kV)'], errors='coerce')
        if 'f(Hz)' in df.columns:
            df['f(Hz)'] = pd.to_numeric(df['f(Hz)'], errors='coerce')
        if '%TanD' in df.columns:
            df['%TanD'] = pd.to_numeric(df['%TanD'], errors='coerce') * 10

        # Lógica de detección de barridos
        cambio_modo = df['Sweep Mode'] != df['Sweep Mode'].shift()
        reinicio_tension = (df['Sweep Mode'] == 'AmplitudeList') & (df['U(kV)'] < df['U(kV)'].shift() - 1)
        reinicio_frec = (df['Sweep Mode'] == 'FrequencyList') & (df['f(Hz)'] > df['f(Hz)'].shift() + 10)
        pausa_larga = df['Time'].diff().dt.total_seconds() > 300
        
        df['N° de Medición'] = (cambio_modo | reinicio_tension | reinicio_frec | pausa_larga).cumsum().astype(str)

        # Gráficos de Tensión
        st.subheader("Barridos en Tensión (Tip-Up)")
        df_tension = df[df['Sweep Mode'] == 'AmplitudeList'].copy()
        
        if not df_tension.empty:
            df_tension = df_tension.sort_values(by=['Time'])
            fig_tension = px.line(df_tension, x='U(kV)', y='%TanD', color='N° de Medición', markers=True)
            st.plotly_chart(fig_tension, use_container_width=True)
            
        # Gráficos de Frecuencia
        st.subheader("Barridos en Frecuencia (Espectroscopía)")
        df_frecuencia = df[df['Sweep Mode'] == 'FrequencyList'].copy()
        
        if not df_frecuencia.empty:
            df_frecuencia = df_frecuencia.sort_values(by=['Time'])
            fig_frec = px.line(df_frecuencia, x='f(Hz)', y='%TanD', color='N° de Medición', markers=True)
            fig_frec.update_xaxes(type="log")
            fig_frec.update_yaxes(type="log")
            st.plotly_chart(fig_frec, use_container_width=True)

        # Tabla de datos
        st.subheader("Datos Procesados")
        columnas_ordenadas = ['N° de Medición'] + [col for col in df.columns if col != 'N° de Medición']
        st.dataframe(df[columnas_ordenadas], use_container_width=True)

elif modo == "🎓 Academia PEI (Simulador)":
    st.title("Simulador de Diagnóstico de Aislación")
    st.markdown("Analice paso a paso el comportamiento de las curvas para llegar a un diagnóstico fundamentado.")
    st.divider()

    # Escenarios ocultos (solo por número)
    escenario = st.selectbox("Seleccionar Escenario de Práctica", ["Caso 1", "Caso 2", "Caso 3"])
    
    tensiones = np.array([2, 4, 6, 8, 10])
    frecuencias = np.array([500, 300, 150, 70, 35, 15, 5, 2, 1])

    # Definición de expectativas según el caso seleccionado
    if escenario == "Caso 1":
        tg_tension = np.array([2.5, 2.5, 2.5, 2.5, 2.5])
        tg_frecuencia = np.array([3.8, 3.5, 3.2, 3.0, 2.8, 2.6, 2.5, 2.4, 2.3])
        exp_tipup = "Constante / Estable"
        exp_espectro = "Creciente normal con la frecuencia / Estable"
        exp_integral = "Buen estado general"
        exp_periodo = "Mantener periodicidad normal (2 a 3 años)"
    
    elif escenario == "Caso 2":
        tg_tension = np.array([3.7, 3.8, 3.9, 4.1, 4.3])
        tg_frecuencia = np.array([3.1, 3.2, 3.5, 4.2, 5.8, 7.5, 12.0, 18.0, 25.0])
        exp_tipup = "Creciente con el aumento de tensión"
        exp_espectro = "Elevación de valores a bajas frecuencias"
        exp_integral = "Aislación deteriorada (Humedad/Envejecimiento)"
        exp_periodo = "Acortar período (Sugerir remedición o intervención)"
        
    elif escenario == "Caso 3":
        tg_tension = np.array([26.0, 18.5, 12.0, 8.5, 7.9])
        tg_frecuencia = np.array([65.0, 42.0, 25.0, 12.3, 8.5, 6.2, 4.0, 3.8, 3.5])
        exp_tipup = "Decreciente con el aumento de tensión"
        exp_espectro = "Elevación de valores a altas frecuencias"
        exp_integral = "Problema de contacto (Perno/Tap u otro vínculo)"
        exp_periodo = "Acortar período (Sugerir remedición o intervención)"

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ensayo Tip-Up (50 Hz)")
        fig_tipup = go.Figure()
        fig_tipup.add_trace(go.Scatter(x=tensiones, y=tg_tension, mode='lines+markers', name="Tg Delta Actual", line=dict(color='red')))
        fig_tipup.update_layout(xaxis_title="Tensión [kV]", yaxis_title="Tangente Delta [x10^-3]")
        st.plotly_chart(fig_tipup, use_container_width=True)

    with col2:
        st.subheader("Espectroscopía Dieléctrica (1 kV)")
        fig_espectro = go.Figure()
        fig_espectro.add_trace(go.Scatter(x=frecuencias, y=tg_frecuencia, mode='lines+markers', name="Tg Delta Actual", line=dict(color='red')))
        fig_espectro.update_layout(xaxis_title="Frecuencia [Hz]", yaxis_title="Tangente Delta [x10^-3]", xaxis_type="log")
        st.plotly_chart(fig_espectro, use_container_width=True)

    # Evaluación paso a paso
    st.subheader("Evaluación de Resultados")
    
    st.markdown("**Paso 1: Análisis Gráfico**")
    user_tipup = st.selectbox("Interpretación de Tip-up (Barrido en tensión):", 
                              ["Seleccione una opción...", 
                               "Constante / Estable", 
                               "Creciente con el aumento de tensión", 
                               "Decreciente con el aumento de tensión"])
    
    user_espectro = st.selectbox("Interpretación de Espectroscopía (Barrido en frecuencia):", 
                                 ["Seleccione una opción...", 
                                  "Creciente normal con la frecuencia / Estable", 
                                  "Elevación de valores a bajas frecuencias", 
                                  "Elevación de valores a altas frecuencias"])
    
    st.markdown("**Paso 2: Diagnóstico y Acción**")
    user_integral = st.selectbox("Evaluación integral del equipo:", 
                                 ["Seleccione una opción...", 
                                  "Buen estado general", 
                                  "Aislación deteriorada (Humedad/Envejecimiento)", 
                                  "Problema de contacto (Perno/Tap u otro vínculo)"])
    
    user_periodo = st.radio("¿Modificaría la periodicidad de ensayos para este equipo?", 
                            ["Seleccione una opción...", 
                             "Mantener periodicidad normal (2 a 3 años)", 
                             "Acortar período (Sugerir remedición o intervención)"])

    if st.button("Validar Diagnóstico"):
        if "Seleccione" in user_tipup or "Seleccione" in user_espectro or "Seleccione" in user_integral or "Seleccione" in user_periodo:
            st.warning("⚠ Complete todos los pasos del análisis para evaluar.")
        else:
            errores = []
            if user_tipup != exp_tipup: errores.append("Interpretación Tip-up")
            if user_espectro != exp_espectro: errores.append("Interpretación Espectroscopía")
            if user_integral != exp_integral: errores.append("Evaluación Integral")
            
            # Evaluación estricta para la interpretación, ligera para el periodo
            if not errores:
                st.success("✅ **¡Excelente análisis!** Logró interpretar correctamente las gráficas y asociarlas a la condición física del equipo.")
                if user_periodo != exp_periodo:
                    st.info(f"💡 *Nota sobre periodicidad:* El diagnóstico es correcto, pero considere que para este caso se sugiere: **{exp_periodo}**.")
            else:
                st.error("❌ Hay discrepancias en el análisis.")
                st.markdown("Revise los siguientes puntos:")
                for error in errores:
                    st.write(f"- **{error}**")
                
                with st.expander("Ver solución esperada"):
                    st.write(f"- **Tip-up:** {exp_tipup}")
                    st.write(f"- **Espectroscopía:** {exp_espectro}")
                    st.write(f"- **Evaluación Integral:** {exp_integral}")
