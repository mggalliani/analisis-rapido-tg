import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuración general
st.set_page_config(page_title="Herramientas PEI - Edenor", layout="wide")

# Menú lateral
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Edenor_logo.svg/2560px-Edenor_logo.svg.png", width=150)
st.sidebar.title("Departamento de Ensayos")
modo = st.sidebar.radio(
    "Seleccione el Entorno:",
    ["📊 Generador de Preinformes", "🎓 Academia PEI (Simulador)"]
)

# ==========================================
# 1. GENERADOR DE PREINFORMES OPERATIVO
# ==========================================
if modo == "📊 Generador de Preinformes":
    st.title("Preinforme de Ensayos de Tangente Delta")
    st.markdown("Procesamiento automático y visualización de barridos de ensayo.")

    archivo_subido = st.file_uploader("Cargar archivo de ensayo (.txt)", type=["txt"])

    if archivo_subido is not None:
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

        # Detección de barridos independientes
        cambio_modo = df['Sweep Mode'] != df['Sweep Mode'].shift()
        reinicio_tension = (df['Sweep Mode'] == 'AmplitudeList') & (df['U(kV)'] < df['U(kV)'].shift() - 1)
        reinicio_frec = (df['Sweep Mode'] == 'FrequencyList') & (df['f(Hz)'] > df['f(Hz)'].shift() + 10)
        pausa_larga = df['Time'].diff().dt.total_seconds() > 300
        
        df['N° de Medición'] = (cambio_modo | reinicio_tension | reinicio_frec | pausa_larga).cumsum().astype(str)

        st.subheader("Barridos en Tensión (Tip-Up)")
        df_tension = df[df['Sweep Mode'] == 'AmplitudeList'].copy()
        if not df_tension.empty:
            df_tension = df_tension.sort_values(by=['Time'])
            fig_tension = px.line(df_tension, x='U(kV)', y='%TanD', color='N° de Medición', markers=True)
            st.plotly_chart(fig_tension, use_container_width=True)
            
        st.subheader("Barridos en Frecuencia (Espectroscopía)")
        df_frecuencia = df[df['Sweep Mode'] == 'FrequencyList'].copy()
        if not df_frecuencia.empty:
            df_frecuencia = df_frecuencia.sort_values(by=['Time'])
            fig_frec = px.line(df_frecuencia, x='f(Hz)', y='%TanD', color='N° de Medición', markers=True)
            fig_frec.update_xaxes(type="log")
            fig_frec.update_yaxes(type="log")
            st.plotly_chart(fig_frec, use_container_width=True)

        st.subheader("Datos Procesados")
        columnas_ordenadas = ['N° de Medición'] + [col for col in df.columns if col != 'N° de Medición']
        st.dataframe(df[columnas_ordenadas], use_container_width=True)

# ==========================================
# 2. ACADEMIA PEI (SIMULADOR DE VUELO)
# ==========================================
elif modo == "🎓 Academia PEI (Simulador)":
    st.title("Simulador de Diagnóstico de Aislación")
    st.markdown("Evalúe los gráficos paso a paso y determine la condición del equipo o de la medición.")
    st.divider()

    # Casos anónimos para evitar pistas
    escenario = st.selectbox(
        "Seleccionar Escenario de Práctica", 
        ["Caso 1", "Caso 2", "Caso 3", "Caso 4", "Caso 5", "Caso 6", "Caso 7"]
    )
    
    tensiones = np.array([2, 4, 6, 8, 10])
    frecuencias = np.array([500, 300, 150, 70, 35, 15, 5, 2, 1])

    # Configuración de los escenarios sintéticos
    if escenario == "Caso 1":
        tg_tension = np.array([2.5, 2.52, 2.49, 2.51, 2.5])
        tg_frecuencia = np.array([3.6, 3.3, 3.0, 2.8, 2.6, 2.5, 2.4, 2.4, 2.3])
        exp_tipup = "Constante / Estable"
        exp_espectro = "Creciente normal con la frecuencia / Estable"
        exp_integral = "Buen estado general"
        exp_accion = "Ninguna acción adicional (medición consistente)"
        exp_periodo = "Mantener periodicidad normal (2 a 3 años)"
        exp_explicacion = "La curva Tip-up plana indica ausencia de descargas parciales o vacíos en la aislación, mientras que el leve incremento a altas frecuencias es el comportamiento dieléctrico normal del material sano. No hay signos de deterioro por humedad."

    elif escenario == "Caso 2":
        tg_tension = np.array([24.5, 18.2, 13.1, 9.8, 7.6])
        tg_frecuencia = np.array([62.0, 41.5, 24.0, 12.0, 7.8, 5.5, 4.1, 3.8, 3.6])
        exp_tipup = "Decreciente con el aumento de tensión"
        exp_espectro = "Elevación de valores a altas frecuencias"
        exp_integral = "Problema de contacto (Perno/Tap u otro vínculo interno)"
        exp_accion = "Remedir desde el cabezal / corona (Método Cabezal)"
        exp_periodo = "Acortar período (Sugerir remedición en 6 meses o 1 año)"
        exp_explicacion = "Una tangente decreciente con la tensión señala que las pérdidas no provienen de la masa aislante, sino de una resistencia en serie (contacto deficiente) que se estabiliza al aumentar la corriente de inyección. A altas frecuencias, la reactancia capacitiva disminuye, haciendo que esta resistencia de contacto domine y dispare las pérdidas totales."

    elif escenario == "Caso 3":
        tg_tension = np.array([3.1, 3.12, 3.08, 3.11, 3.1])
        tg_frecuencia = np.array([4.1, 3.8, 3.5, 3.2, 3.1, 3.3, 9.4, 1.2, 11.8])
        exp_tipup = "Constante / Estable"
        exp_espectro = "Valores erráticos / dispersos a baja frecuencia (ruido)"
        exp_integral = "Medición afectada por ruido / interferencia externa"
        exp_accion = "Remedir sin variar nada para verificar repetibilidad o ajustar supresión"
        exp_periodo = "Mantener periodicidad normal (2 a 3 años)"
        exp_explicacion = "Las fluctuaciones erráticas exclusivamente a bajas frecuencias (generalmente menores a 10 Hz) suelen ser producto de interferencias electromagnéticas o capacitivas del entorno, ya que en ese rango la relación señal/ruido empeora drásticamente. No refleja un daño físico en la aislación."

    elif escenario == "Caso 4":
        tg_tension = np.array([3.8, 4.2, 4.7, 5.3, 5.9])
        tg_frecuencia = np.array([3.2, 3.4, 4.0, 5.5, 8.2, 14.5, 28.0, 42.0, 65.0])
        exp_tipup = "Creciente con el aumento de tensión"
        exp_espectro = "Elevación de valores a bajas frecuencias"
        exp_integral = "Aislación deteriorada (Humedad/Envejecimiento)"
        exp_accion = "Ninguna acción adicional (medición consistente)"
        exp_periodo = "Acortar período (Sugerir remedición en 6 meses o 1 año)"
        exp_explicacion = "Un Tip-up creciente revela que el aumento del campo eléctrico incrementa desproporcionadamente las pérdidas, típico de envejecimiento o micro-vacíos. La elevación exponencial a bajas frecuencias es la huella digital de la polarización interfacial y la alta conductividad generada por la humedad atrapada en la celulosa o el aceite."

    elif escenario == "Caso 5":
        tg_tension = np.array([14.2, 6.8, 19.4, 11.5, 16.0])
        tg_frecuencia = np.array([18.2, 8.5, 22.4, 12.1, 15.3, 7.4, 20.1, 11.0, 17.5])
        exp_tipup = "Valores erráticos / saltos anormales entre escalones"
        exp_espectro = "Curva errática en todo el espectro / sin tendencia física"
        exp_integral = "Falso contacto / problema en pinzas de medición o circuito de guarda"
        exp_accion = "Verificar y limpiar conexionado del puente, pinzas y guarda"
        exp_periodo = "Mantener periodicidad normal (2 a 3 años)"
        exp_explicacion = "Saltos bruscos y sin un patrón físico predecible en ambos gráficos revelan inestabilidad eléctrica en el circuito de medición (típicamente falsos contactos en las mordazas de las pinzas o mallas de guarda mal conectadas). La aislación física del equipo no cambia sus propiedades de forma tan caótica e instantánea."

    elif escenario == "Caso 6":
        tg_tension = np.array([-0.35, -0.18, 0.05, 0.22, 0.40])
        tg_frecuencia = np.array([-0.8, -0.5, -0.2, 0.1, 0.5, 0.9, 1.4, 2.1, 3.0])
        exp_tipup = "Valores erráticos / saltos anormales entre escalones"
        exp_espectro = "Curva errática en todo el espectro / sin tendencia física"
        exp_integral = "Problema en la puesta a tierra del equipo o referencia flotante"
        exp_accion = "Verificar y reforzar la puesta a tierra del equipo y del puente"
        exp_periodo = "Mantener periodicidad normal (2 a 3 años)"
        exp_explicacion = "Valores de tangente negativos o invertidos indican un problema grave en el flujo de retorno de la corriente de medición. Generalmente ocurre cuando la puesta a tierra del equipo bajo ensayo (o del propio puente) es deficiente, generando referencias de potencial flotantes que falsean por completo el cálculo vectorial de las pérdidas."

    elif escenario == "Caso 7":
        tg_tension = np.array([5.8, 4.9, 4.3, 3.8, 3.5])
        tg_frecuencia = np.array([14.5, 10.2, 7.1, 5.0, 4.1, 3.6, 3.2, 3.0, 2.9])
        exp_tipup = "Decreciente con el aumento de tensión"
        exp_espectro = "Elevación de valores a altas frecuencias"
        exp_integral = "Problema de contacto (Perno/Tap u otro vínculo interno)"
        exp_accion = "Remedir desde el cabezal / corona (Método Cabezal)"
        exp_periodo = "Acortar período (Sugerir remedición en 6 meses o 1 año)"
        exp_explicacion = "Al igual que en un caso severo, el Tip-up decreciente y el aumento a altas frecuencias confirman la presencia de una resistencia parásita en serie (falso contacto incipiente interno). La acción de remedir inyectando desde el cabezal corona permite 'puentear' el perno; si los valores se normalizan, el diagnóstico del perno queda confirmado."

    # Render de gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ensayo Tip-Up (50 Hz)")
        fig_tipup = go.Figure()
        fig_tipup.add_trace(go.Scatter(x=tensiones, y=tg_tension, mode='lines+markers', name="Tg Delta", line=dict(color='royalblue', width=2)))
        fig_tipup.update_layout(xaxis_title="Tensión [kV]", yaxis_title="Tangente Delta [x10^-3]")
        st.plotly_chart(fig_tipup, use_container_width=True)

    with col2:
        st.subheader("Espectroscopía Dieléctrica")
        fig_espectro = go.Figure()
        fig_espectro.add_trace(go.Scatter(x=frecuencias, y=tg_frecuencia, mode='lines+markers', name="Tg Delta", line=dict(color='firebrick', width=2)))
        fig_espectro.update_layout(xaxis_title="Frecuencia [Hz]", yaxis_title="Tangente Delta [x10^-3]", xaxis_type="log")
        st.plotly_chart(fig_espectro, use_container_width=True)

    # Formulario pedagógico paso a paso
    st.subheader("Evaluación de Resultados")
    
    st.markdown("#### Paso 1: Análisis Gráfico Individual")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        user_tipup = st.selectbox(
            "Interpretación de Tip-up (Barrido en tensión):", 
            ["Seleccione una opción...", 
             "Constante / Estable", 
             "Creciente con el aumento de tensión", 
             "Decreciente con el aumento de tensión",
             "Valores erráticos / saltos anormales entre escalones"]
        )
    with col_g2:
        user_espectro = st.selectbox(
            "Interpretación de Espectroscopía (Barrido en frecuencia):", 
            ["Seleccione una opción...", 
             "Creciente normal con la frecuencia / Estable", 
             "Elevación de valores a bajas frecuencias", 
             "Elevación de valores a altas frecuencias",
             "Valores erráticos / dispersos a baja frecuencia (ruido)",
             "Curva errática en todo el espectro / sin tendencia física"]
        )
    
    st.markdown("#### Paso 2: Diagnóstico y Acciones de Campo")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        user_integral = st.selectbox(
            "Evaluación integral del equipo / medición:", 
            ["Seleccione una opción...", 
             "Buen estado general", 
             "Aislación deteriorada (Humedad/Envejecimiento)", 
             "Problema de contacto (Perno/Tap u otro vínculo interno)",
             "Medición afectada por ruido / interferencia externa",
             "Falso contacto / problema en pinzas de medición o circuito de guarda",
             "Problema en la puesta a tierra del equipo o referencia flotante"]
        )
    with col_d2:
        user_accion = st.selectbox(
            "Acción adicional a realizar en campo:",
            ["Seleccione una opción...",
             "Ninguna acción adicional (medición consistente)",
             "Remedir desde el cabezal / corona (Método Cabezal)",
             "Remedir sin variar nada para verificar repetibilidad o ajustar supresión",
             "Verificar y limpiar conexionado del puente, pinzas y guarda",
             "Verificar y reforzar la puesta a tierra del equipo y del puente"]
        )

    st.markdown("#### Paso 3: Criterio de Periodicidad")
    user_periodo = st.radio(
        "¿Modificaría la periodicidad de ensayos recomendada para este equipo?", 
        ["Seleccione una opción...", 
         "Mantener periodicidad normal (2 a 3 años)", 
         "Acortar período (Sugerir remedición en 6 meses o 1 año)"],
        horizontal=True
    )

    if st.button("Validar Diagnóstico"):
        if any("Seleccione" in resp for resp in [user_tipup, user_espectro, user_integral, user_accion, user_periodo]):
            st.warning("⚠️ Complete todos los pasos del análisis antes de validar.")
        else:
            errores = []
            if user_tipup != exp_tipup: errores.append("Interpretación de Tip-up")
            if user_espectro != exp_espectro: errores.append("Interpretación de Espectroscopía")
            if user_integral != exp_integral: errores.append("Evaluación Integral")
            if user_accion != exp_accion: errores.append("Acción Adicional en Campo")
            
            if not errores:
                st.success("✅ **¡Diagnóstico y Acciones Impecables!**")
                st.info(f"💡 **Repaso del concepto aplicado:** {exp_explicacion}")
                
                if user_periodo != exp_periodo:
                    st.warning(f"⏳ *Nota sobre periodicidad:* El diagnóstico y la acción técnica son correctos, pero para este escenario se sugiere: **{exp_periodo}**.")
            else:
                st.error("❌ Hay discrepancias en el análisis.")
                st.markdown("Puntos a revisar:")
                for e in errores:
                    st.write(f"- **{e}**")
                
                with st.expander("Ver solución técnica explicada"):
                    st.markdown(f"""
                    * **Tip-up:** {exp_tipup}
                    * **Espectroscopía:** {exp_espectro}
                    * **Evaluación Integral:** {exp_integral}
                    * **Acción en Campo:** {exp_accion}
                    * **Periodicidad esperada:** {exp_periodo}
                    
                    💡 **Repaso del concepto aplicado:** {exp_explicacion}
                    """)
