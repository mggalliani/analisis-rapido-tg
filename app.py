import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Preinforme de Ensayos DELTA4000")

archivo_subido = st.file_uploader("Cargar archivo .txt del equipo", type=["txt"])

if archivo_subido is not None:
    
    # El on_bad_lines='skip' evita que el programa falle si hay alguna fila corrupta
    df = pd.read_csv(archivo_subido, sep='\t', decimal='.', encoding='utf-8', on_bad_lines='skip')
    
    # Solución definitiva para los nombres de columnas:
    # split() rompe por CUALQUIER tipo de espacio oculto y join() lo une con un solo espacio limpio.
    df.columns = [" ".join(str(col).split()) for col in df.columns]
    
    # Freno de seguridad: si no encuentra las columnas, avisa amigablemente y frena acá.
    if 'Time' not in df.columns or 'Sweep Mode' not in df.columns:
        st.error(f"🚨 Problema de lectura. Las columnas detectadas en tu archivo son: {df.columns.tolist()}")
        st.stop()
    
    df = df.dropna(subset=['Time', 'Sweep Mode'])
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    
    # Validación extra por si el archivo no trae alguna de estas columnas
    if 'U(kV)' in df.columns:
        df['U(kV)'] = pd.to_numeric(df['U(kV)'], errors='coerce')
    if 'f(Hz)' in df.columns:
        df['f(Hz)'] = pd.to_numeric(df['f(Hz)'], errors='coerce')
    if '%TanD' in df.columns:
        df['%TanD'] = pd.to_numeric(df['%TanD'], errors='coerce') * 10

    # Lógica robusta para detectar verdaderos inicios de barrido
    cambio_modo = df['Sweep Mode'] != df['Sweep Mode'].shift()
    reinicio_tension = (df['Sweep Mode'] == 'AmplitudeList') & (df['U(kV)'] < df['U(kV)'].shift() - 1)
    reinicio_frec = (df['Sweep Mode'] == 'FrequencyList') & (df['f(Hz)'] > df['f(Hz)'].shift() + 10)
    pausa_larga = df['Time'].diff().dt.total_seconds() > 300
    
    # Asignamos el nombre de la columna
    df['N° de Medición'] = (cambio_modo | reinicio_tension | reinicio_frec | pausa_larga).cumsum().astype(str)

    # Gráficos de Tensión
    st.subheader("Barridos en Tensión (AmplitudeList)")
    df_tension = df[df['Sweep Mode'] == 'AmplitudeList'].copy()
    
    if not df_tension.empty:
        df_tension = df_tension.sort_values(by=['Time'])
        
        fig_tension = px.line(
            df_tension, 
            x='U(kV)', 
            y='%TanD', 
            color='N° de Medición', 
            markers=True
        )
        st.plotly_chart(fig_tension)
        
    # Gráficos de Frecuencia
    st.subheader("Barridos en Frecuencia (FrequencyList)")
    df_frecuencia = df[df['Sweep Mode'] == 'FrequencyList'].copy()
    
    if not df_frecuencia.empty:
        df_frecuencia = df_frecuencia.sort_values(by=['Time'])
        
        fig_frec = px.line(
            df_frecuencia, 
            x='f(Hz)', 
            y='%TanD', 
            color='N° de Medición', 
            markers=True
        )
        
        fig_frec.update_xaxes(type="log")
        fig_frec.update_yaxes(type="log")
        
        st.plotly_chart(fig_frec)

    # Tabla de datos interactiva
    st.subheader("Datos Procesados")
    
    # Reordenamos para que el N° de Medición aparezca primero en la tabla
    columnas_ordenadas = ['N° de Medición'] + [col for col in df.columns if col != 'N° de Medición']
    
    # Renderizamos la tabla estilo Excel
    st.dataframe(df[columnas_ordenadas], use_container_width=True)
