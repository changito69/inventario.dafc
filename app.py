import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Inventario Unificado", layout="wide")

# --- 1. DICCIONARIO DE DATOS (Lo que buscamos) ---
MAPEO_INTELIGENTE = {
    'NOMBRE': ['descripción', 'descripcion', 'nombre', 'detalle', 'bien', 'item'],
    'CANTIDAD': ['cant', 'cantidad', 'stock'],
    'CODIGO': ['serie', 'código', 'codigo', 's/n'],
    'MODELO': ['modelo'],
    'MARCA': ['marca'],
    'UBICACION': ['ubicación', 'ubicacion', 'lugar', 'curso', 'aula', 'departamento']
}

def encontrar_fila_cabecera(archivo):
    """
    Busca en las primeras 20 filas dónde diablos están los encabezados reales.
    """
    try:
        # Leemos el archivo sin asumir cabeceras todavía
        df_temp = pd.read_excel(archivo, header=None, nrows=20)
        
        for i, row in df_temp.iterrows():
            # Convertimos toda la fila a texto minúscula para buscar palabras clave
            fila_texto = [str(celda).lower() for celda in row.tolist()]
            
            # Si una fila tiene "descripción" Y TAMBIÉN "serie" o "modelo", ¡Esa es la buena!
            tiene_desc = any('descripción' in x or 'descripcion' in x for x in fila_texto)
            tiene_serie = any('serie' in x for x in fila_texto)
            tiene_marca = any('marca' in x for x in fila_texto)
            
            if (tiene_desc and tiene_serie) or (tiene_desc and tiene_marca):
                return i # Retorna el número de fila correcta
                
    except Exception:
        return 0 # Si falla, intenta desde el principio
    return 0

def procesar_excel(archivo):
    # 1. Encontrar dónde empiezan los datos
    fila_inicio = encontrar_fila_cabecera(archivo)
    
    # 2. Leer el Excel desde esa fila correcta
    df = pd.read_excel(archivo, header=fila_inicio)
    
    # 3. Normalizar columnas (Limpieza)
    df.columns = [str(col).strip().lower() for col in df.columns]
    columnas_nuevas = {}
    
    for col_actual in df.columns:
        for estandar, variantes in MAPEO_INTELIGENTE.items():
            if any(v in col_actual for v in variantes):
                columnas_nuevas[col_actual] = estandar
                break
                
    df = df.rename(columns=columnas_nuevas)
    
    # 4. Filtrar solo columnas útiles
    cols_finales = [c for c in df.columns if c in MAPEO_INTELIGENTE.keys()]
    
    if cols_finales:
        df_final = df[cols_finales].copy()
        
        # Asignar ubicación basada en el nombre del archivo si no existe columna
        if 'UBICACION' not in df_final.columns:
            nombre_limpio = archivo.replace('.xlsx', '').replace('.xls', '')
            df_final['UBICACION'] = nombre_limpio
            
        return df_final
    return pd.DataFrame()

# --- INTERFAZ ---
st.title("🏫 Inventario Digital Centralizado")

archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos:
    st.error("⚠️ No hay archivos Excel en el repositorio.")
else:
    df_consolidado = pd.DataFrame()
    
    # Barra de progreso para dar feedback visual
    progreso = st.progress(0)
    
    for i, archivo in enumerate(archivos):
        try:
            df_limpio = procesar_excel(archivo)
            if not df_limpio.empty:
                df_consolidado = pd.concat([df_consolidado, df_limpio], ignore_index=True)
        except Exception as e:
            st.warning(f"Error en {archivo}: {e}")
        progreso.progress((i + 1) / len(archivos))

    progreso.empty() # Ocultar barra al finalizar

    if not df_consolidado.empty:
        # Filtros
        st.sidebar.header("🔍 Filtros")
        
        lista_lugares = sorted(df_consolidado['UBICACION'].astype(str).unique().tolist())
        filtro_lugar = st.sidebar.selectbox("Seleccionar Curso / Aula:", ['Todos'] + lista_lugares)
        
        busqueda = st.sidebar.text_input("Buscar Activo:")

        df_view = df_consolidado.copy()
        
        if filtro_lugar != 'Todos':
            df_view = df_view[df_view['UBICACION'].astype(str) == filtro_lugar]
        
        if busqueda:
            df_view = df_view[
                df_view.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            ]

        # Tabla con formato ancho
        st.metric("Total Activos", len(df_view))
        st.dataframe(df_view, use_container_width=True)
    else:
        st.error("❌ Sigue sin detectar columnas. Por favor revisa que los Excel no estén protegidos con contraseña.")
