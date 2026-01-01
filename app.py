import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Modo Diagnóstico", layout="wide")

st.title("🕵️ Modo Diagnóstico: Analizador de Columnas")
st.info("Este programa leerá tus archivos y nos dirá los nombres exactos de las cabeceras.")

# Buscar archivos
archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos:
    st.error("⚠️ No encontré archivos Excel en el repositorio.")
else:
    for archivo in archivos:
        st.markdown(f"---")
        st.subheader(f"📂 Archivo: {archivo}")
        
        try:
            # Leer solo los encabezados del Excel
            df = pd.read_excel(archivo)
            
            # Obtener nombres de columnas
            columnas = df.columns.tolist()
            
            # Mostrar visualmente
            st.write("Las columnas detectadas son:")
            st.code(columnas)
            
            # Mostrar primeros 3 datos para verificar
            st.write("Ejemplo de datos:")
            st.dataframe(df.head(3))
            
        except Exception as e:
            st.error(f"Error leyendo este archivo: {e}")
