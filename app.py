import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Modo Rayos X", layout="wide")
st.title("🩻 Diagnóstico: Rayos X del Excel")

archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos:
    st.error("No hay archivos.")
else:
    for archivo in archivos:
        st.divider()
        st.subheader(f"Analizando archivo: {archivo}")
        
        try:
            # Leemos el archivo SIN buscar cabeceras (leemos todo tal cual)
            df_raw = pd.read_excel(archivo, header=None, nrows=10)
            
            st.warning("Así es como la computadora ve las primeras 10 filas:")
            
            # Mostramos la tabla tal cual
            st.dataframe(df_raw)
            
            st.info("👆 Mira la tabla de arriba. Busca en qué FILA (número 0, 1, 2...) aparecen las palabras 'DESCRIPCIÓN' o 'SERIE'.")
            
        except Exception as e:
            st.error(f"Error crítico leyendo el archivo: {e}")
            st.error("Posible causa: Si el archivo es muy antiguo (.xls), necesitamos instalar 'xlrd'.")
