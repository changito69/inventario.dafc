import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Inventario Unificado", layout="wide")

# --- 1. DICCIONARIO DE PALABRAS CLAVE ---
MAPEO_INTELIGENTE = {
    'NOMBRE': ['descripción', 'descripcion', 'descri', 'detalle', 'bien', 'item', 'nombre'],
    'CANTIDAD': ['cant.', 'cant', 'cantidad', 'stock'],
    'CODIGO': ['serie', 'código', 'codigo', 's/n'],
    'MODELO': ['modelo'],
    'MARCA': ['marca'],
    'ESTADO': ['estado', 'condición', 'situacion'],
    'UBICACION': ['ubicación', 'ubicacion', 'lugar', 'curso', 'aula']
}

def encontrar_fila_cabecera(archivo):
    """
    Busca la fila que contenga 'SERIE', 'MODELO' o 'DESCRI'.
    """
    try:
        df_temp = pd.read_excel(archivo, header=None, nrows=15)
        for i, row in df_temp.iterrows():
            fila_texto = [str(celda).lower() for celda in row.tolist()]
            if any('serie' in x for x in fila_texto) or any('modelo' in x for x in fila_texto) or any('descri' in x for x in fila_texto):
                return i 
    except Exception:
        return 0
    return 0

def procesar_excel(archivo):
    fila_inicio = encontrar_fila_cabecera(archivo)
    
    # Leemos el archivo
    df = pd.read_excel(archivo, header=fila_inicio)
    
    # Limpieza de nombres de columnas
    df.columns = [str(col).strip().lower() for col in df.columns]
    columnas_nuevas = {}
    
    for col_actual in df.columns:
        for estandar, variantes in MAPEO_INTELIGENTE.items():
            if any(v in col_actual for v in variantes):
                columnas_nuevas[col_actual] = estandar
                break
                
    df = df.rename(columns=columnas_nuevas)
    cols_finales = [c for c in df.columns if c in MAPEO_INTELIGENTE.keys()]
    
    if cols_finales:
        df_final = df[cols_finales].copy()
        
        # Asignar ubicación si no existe
        if 'UBICACION' not in df_final.columns:
            nombre_limpio = archivo.replace('.xlsx', '').replace('.xls', '')
            df_final['UBICACION'] = nombre_limpio
            
        return df_final
    return pd.DataFrame()

# --- INTERFAZ ---
st.title("🏫 Inventario Digital Centralizado")
st.markdown("---")

archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos:
    st.error("⚠️ No hay archivos Excel en el repositorio.")
else:
    df_consolidado = pd.DataFrame()
    
    barra = st.progress(0)
    for i, archivo in enumerate(archivos):
        try:
            df_limpio = procesar_excel(archivo)
            if not df_limpio.empty:
                df_consolidado = pd.concat([df_consolidado, df_limpio], ignore_index=True)
        except Exception as e:
            # Ignoramos errores silenciosamente para no ensuciar la pantalla
            pass
        barra.progress((i + 1) / len(archivos))
    barra.empty()

    if not df_consolidado.empty:
        # --- FILTROS ---
        st.sidebar.header("🔍 Buscador")
        
        # Convertimos a texto para ordenar los filtros
        lugares = sorted(df_consolidado['UBICACION'].astype(str).unique().tolist())
        filtro_lugar = st.sidebar.selectbox("Filtrar por Archivo/Curso:", ['Todos'] + lugares)
        
        busqueda = st.sidebar.text_input("Escribe para buscar (Serie, Bien, Modelo):")

        df_view = df_consolidado.copy()
        
        if filtro_lugar != 'Todos':
            df_view = df_view[df_view['UBICACION'].astype(str) == filtro_lugar]
            
        if busqueda:
            df_view = df_view[
                df_view.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            ]

        # --- RESULTADOS ---
        col1, col2 = st.columns(2)
        col1.metric("Activos Encontrados", len(df_view))
        col2.metric("Archivos Procesados", len(lugares))
        
        # --- EL FIX DEFINITIVO ---
        # Convertimos TODO a texto (String) antes de mostrarlo.
        # Esto evita el error de PyArrow (flecha roja)
        df_view = df_view.astype(str)
        
        st.dataframe(df_view, use_container_width=True)
        
    else:
        st.warning("⚠️ No se encontraron datos válidos. Verifica que los archivos tengan columnas como 'SERIE', 'MODELO' o 'DESCRIPCIÓN'.")
