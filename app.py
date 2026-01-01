import streamlit as st
import pandas as pd
import os

# CONFIGURACIÓN
st.set_page_config(page_title="Inventario Unificado", layout="wide")

# DICCIONARIO DE SINÓNIMOS (El cerebro que une los formatos)
MAPEO_INTELIGENTE = {
    'NOMBRE': ['nombre', 'item', 'descripción', 'descripcion', 'detalle', 'equipo', 'activo'],
    'UBICACION': ['ubicación', 'ubicacion', 'lugar', 'curso', 'aula', 'departamento', 'area'],
    'CANTIDAD': ['cant', 'cantidad', 'stock', 'total', 'numero'],
    'ESTADO': ['estado', 'condicion', 'situacion', 'funcionalidad'],
    'CODIGO': ['id', 'codigo', 'código', 'inventario', 'etiqueta']
}

def normalizar_dataframe(df, nombre_archivo):
    df.columns = [str(col).strip().lower() for col in df.columns]
    columnas_nuevas = {}
    for col_actual in df.columns:
        encontrado = False
        for estandar, variantes in MAPEO_INTELIGENTE.items():
            if any(v in col_actual for v in variantes):
                columnas_nuevas[col_actual] = estandar
                encontrado = True
                break
    
    df = df.rename(columns=columnas_nuevas)
    cols_finales = [c for c in df.columns if c in MAPEO_INTELIGENTE.keys()]
    
    if cols_finales:
        df_final = df[cols_finales].copy()
        df_final['FUENTE'] = nombre_archivo
        return df_final
    return pd.DataFrame()

# INTERFAZ
st.title("🏫 Inventario Digital Centralizado")

# Buscar archivos en la carpeta actual
archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos:
    st.error("⚠️ No encontré archivos Excel. Por favor súbelos al repositorio.")
else:
    df_consolidado = pd.DataFrame()
    
    # Cargar datos
    for archivo in archivos:
        try:
            df_temp = pd.read_excel(archivo)
            df_limpio = normalizar_dataframe(df_temp, archivo)
            if not df_limpio.empty:
                df_consolidado = pd.concat([df_consolidado, df_limpio], ignore_index=True)
        except Exception as e:
            st.warning(f"No se pudo leer {archivo}: {e}")

    if not df_consolidado.empty:
        # Filtros
        st.sidebar.header("🔍 Filtros de Búsqueda")
        
        filtro_lugar = "Todos"
        if 'UBICACION' in df_consolidado.columns:
            lugares = ['Todos'] + sorted(df_consolidado['UBICACION'].astype(str).unique().tolist())
            filtro_lugar = st.sidebar.selectbox("Filtrar por Curso/Aula:", lugares)
            
        busqueda = st.sidebar.text_input("Buscar por palabra clave:")

        # Aplicar filtros
        df_view = df_consolidado.copy()
        if filtro_lugar != 'Todos':
            df_view = df_view[df_view['UBICACION'].astype(str) == filtro_lugar]
        
        if busqueda:
            df_view = df_view[df_view.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)]

        st.metric(label="Total de Activos Encontrados", value=len(df_view))
        st.dataframe(df_view, use_container_width=True)
    else:
        st.info("Se encontraron archivos pero las columnas no coinciden con el estándar esperado.")
