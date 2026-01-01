import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Inventario Unificado", layout="wide")

# --- 1. EL CEREBRO ACTUALIZADO (Adaptado a tu Imagen 3) ---
MAPEO_INTELIGENTE = {
    # Aquí están las columnas exactas que vi en tu captura
    'NOMBRE': ['descripción del bien', 'descripcion del bien', 'nombre', 'item', 'detalle', 'activo'],
    'CANTIDAD': ['cant.', 'cant', 'cantidad', 'stock'],
    'CODIGO': ['serie', 'nro de serie', 'código', 'codigo', 'sn', 's/n'],
    'MODELO': ['modelo'],
    'MARCA': ['marca'],
    # Si no encuentra estas columnas, usará el Nombre del Archivo como ubicación
    'UBICACION': ['ubicación', 'ubicacion', 'lugar', 'curso', 'aula', 'departamento']
}

def normalizar_dataframe(df, nombre_archivo):
    # Limpieza: convertir encabezados a minúsculas y quitar espacios
    df.columns = [str(col).strip().lower() for col in df.columns]
    
    columnas_nuevas = {}
    for col_actual in df.columns:
        for estandar, variantes in MAPEO_INTELIGENTE.items():
            # Busca si la palabra clave está dentro del encabezado
            if any(v in col_actual for v in variantes):
                columnas_nuevas[col_actual] = estandar
                break
    
    # Renombrar columnas
    df = df.rename(columns=columnas_nuevas)
    
    # Quedarnos solo con las columnas útiles
    cols_finales = [c for c in df.columns if c in MAPEO_INTELIGENTE.keys()]
    
    if cols_finales:
        df_final = df[cols_finales].copy()
        
        # --- AUTOMATIZACIÓN DE UBICACIÓN ---
        # Si el Excel no dice el curso, asumimos que el nombre del archivo ES el curso.
        if 'UBICACION' not in df_final.columns:
            # Quitamos el ".xlsx" para que quede limpio (ej: "Primero A")
            nombre_limpio = nombre_archivo.replace('.xlsx', '').replace('.xls', '')
            df_final['UBICACION'] = nombre_limpio
            
        return df_final
    return pd.DataFrame()

# --- 2. LA INTERFAZ VISUAL ---
st.title("🏫 Inventario Digital Centralizado")

# Buscar archivos en el repositorio
archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos:
    st.error("⚠️ No encontré archivos Excel. Por favor súbelos al repositorio.")
else:
    df_consolidado = pd.DataFrame()
    
    # Procesar cada archivo
    for archivo in archivos:
        try:
            df_temp = pd.read_excel(archivo)
            df_limpio = normalizar_dataframe(df_temp, archivo)
            
            if not df_limpio.empty:
                df_consolidado = pd.concat([df_consolidado, df_limpio], ignore_index=True)
        except Exception as e:
            st.warning(f"No se pudo leer el archivo {archivo}: {e}")

    # Mostrar Resultados y Filtros
    if not df_consolidado.empty:
        st.sidebar.header("🔍 Filtros")
        
        # 1. Filtro por Curso (Basado en el nombre de tus archivos)
        lista_lugares = sorted(df_consolidado['UBICACION'].astype(str).unique().tolist())
        filtro_lugar = st.sidebar.selectbox("Seleccionar Curso / Aula:", ['Todos'] + lista_lugares)
        
        # 2. Buscador General
        busqueda = st.sidebar.text_input("Buscar (Escribe serie, marca o nombre):")

        # Lógica de Filtrado
        df_view = df_consolidado.copy()
        
        if filtro_lugar != 'Todos':
            df_view = df_view[df_view['UBICACION'].astype(str) == filtro_lugar]
        
        if busqueda:
            df_view = df_view[
                df_view.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            ]

        # Tabla Final
        st.metric("Total de Activos", len(df_view))
        st.dataframe(df_view, use_container_width=True)
    else:
        st.error("⚠️ Error de Formato: No se detectaron las columnas 'DESCRIPCIÓN DEL BIEN' o 'SERIE'.")
        st.info("Asegúrate de que los encabezados estén en la PRIMERA fila del Excel.")
