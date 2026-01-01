import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Reporte por Curso", layout="wide")

# --- 1. CONFIGURACIÓN ---
# Palabras clave para detectar dónde empiezan los datos
CLAVES_CABECERA = ['serie', 'modelo', 'descripción', 'descripcion', 'bien', 'item', 'marca']

def encontrar_fila_cabecera(archivo):
    """
    Busca en las primeras 20 filas en qué fila están los títulos.
    """
    try:
        df_temp = pd.read_excel(archivo, header=None, nrows=20)
        for i, row in df_temp.iterrows():
            # Convertimos toda la fila a texto para buscar
            fila_texto = [str(celda).lower() for celda in row.tolist()]
            
            # Si encontramos "serie" O "modelo" O "descripción", ahí es.
            if any(clave in x for x in fila_texto for clave in CLAVES_CABECERA):
                return i 
    except Exception:
        return 0
    return 0

# --- 2. INTERFAZ PRINCIPAL ---
st.title("📂 Generador de Informes de Inventario")
st.markdown("Selecciona un archivo (Curso) para ver su reporte detallado.")

# Listar archivos
archivos_disponibles = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos_disponibles:
    st.error("⚠️ No hay archivos Excel cargados en el repositorio.")
else:
    # --- PASO 1: SELECCIONAR CURSO ---
    st.sidebar.header("Navegación")
    
    # Creamos un selector (Dropdown) con los nombres de los archivos
    archivo_seleccionado = st.sidebar.selectbox(
        "📍 Selecciona el Documento/Curso:", 
        archivos_disponibles
    )

    # --- PASO 2: PROCESAR SOLO ESE ARCHIVO ---
    if archivo_seleccionado:
        st.divider()
        st.subheader(f"Informe: {archivo_seleccionado.replace('.xlsx', '')}")
        
        try:
            # Detectar fila de inicio
            fila_inicio = encontrar_fila_cabecera(archivo_seleccionado)
            
            # Leer datos
            df = pd.read_excel(archivo_seleccionado, header=fila_inicio)
            
            # BLINDAJE ANTI-ERROR (El fix de la pantalla roja)
            # Convertimos todo a texto para que no falle si hay números mezclados con letras
            df = df.astype(str)
            
            # Reemplazar "nan" (vacíos) por guiones para que se vea limpio
            df = df.replace('nan', '-')

            # --- PASO 3: MOSTRAR ESTADÍSTICAS ---
            total_items = len(df)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Activos en este Doc", total_items)
            col2.metric("Fila de Cabecera detectada", f"Fila #{fila_inicio}")
            
            # --- PASO 4: BUSCADOR INTERNO ---
            busqueda = st.text_input(f"🔍 Buscar algo dentro de {archivo_seleccionado}...")
            
            df_visible = df.copy()
            if busqueda:
                # Filtra si encuentra el texto en CUALQUIER columna
                df_visible = df_visible[
                    df_visible.apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)
                ]
            
            # Mostrar tabla
            st.dataframe(df_visible, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error abriendo el archivo: {e}")
