import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Inventario Unificado", layout="wide")

# --- 1. DICCIONARIO DE PALABRAS CLAVE ---
# Aquí le enseñamos a la computadora cómo se llaman tus columnas
MAPEO_INTELIGENTE = {
    # Agregué 'descri' porque en tu imagen se ve cortado, así aseguramos que lo detecte
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
    Escanea las primeras 15 filas buscando dónde están los títulos reales.
    Busca la fila que tenga la palabra 'SERIE' o 'MODELO' o 'CANT.'.
    """
    try:
        # Leemos las primeras 15 filas sin encabezado
        df_temp = pd.read_excel(archivo, header=None, nrows=15)
        
        for i, row in df_temp.iterrows():
            # Convertimos la fila a texto y minúsculas para buscar
            fila_texto = [str(celda).lower() for celda in row.tolist()]
            
            # Si la fila tiene "serie" O "modelo", es la fila ganadora
            # (Tu imagen muestra que 'serie' y 'modelo' están claros en la fila 7)
            if any('serie' in x for x in fila_texto) or any('modelo' in x for x in fila_texto):
                return i # Retorna el número 7 (o el que sea en cada archivo)
                
    except Exception:
        return 0
    return 0

def procesar_excel(archivo):
    # 1. Detectar automáticamente en qué fila empiezan los datos
    fila_inicio = encontrar_fila_cabecera(archivo)
    
    # 2. Leer el archivo saltándose las filas vacías de arriba
    df = pd.read_excel(archivo, header=fila_inicio)
    
    # 3. Limpieza de nombres de columnas
    df.columns = [str(col).strip().lower() for col in df.columns]
    columnas_nuevas = {}
    
    # 4. Renombrar columnas según el diccionario
    for col_actual in df.columns:
        for estandar, variantes in MAPEO_INTELIGENTE.items():
            if any(v in col_actual for v in variantes):
                columnas_nuevas[col_actual] = estandar
                break
                
    df = df.rename(columns=columnas_nuevas)
    
    # 5. Filtrar solo lo útil
    cols_finales = [c for c in df.columns if c in MAPEO_INTELIGENTE.keys()]
    
    if cols_finales:
        df_final = df[cols_finales].copy()
        
        # --- TRUCO DEL NOMBRE DE ARCHIVO ---
        # Como en tu imagen NO hay columna de "Curso", usamos el nombre del archivo.
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
    
    # Barra de carga
    barra = st.progress(0)
    
    for i, archivo in enumerate(archivos):
        try:
            df_limpio = procesar_excel(archivo)
            if not df_limpio.empty:
                df_consolidado = pd.concat([df_consolidado, df_limpio], ignore_index=True)
        except Exception as e:
            st.warning(f"Error leyendo {archivo}: {e}")
        barra.progress((i + 1) / len(archivos))
        
    barra.empty()

    if not df_consolidado.empty:
        # --- FILTROS LATERALES ---
        st.sidebar.header("🔍 Buscador")
        
        # Filtro 1: Ubicación (Basado en nombre de archivo)
        lugares = sorted(df_consolidado['UBICACION'].astype(str).unique().tolist())
        filtro_lugar = st.sidebar.selectbox("Filtrar por Archivo/Curso:", ['Todos'] + lugares)
        
        # Filtro 2: Texto
        busqueda = st.sidebar.text_input("Escribe para buscar (Serie, Bien, Modelo):")

        # --- APLICAR FILTROS ---
        df_view = df_consolidado.copy()
        
        if filtro_lugar != 'Todos':
            df_view = df_view[df_view['UBICACION'].astype(str) == filtro_lugar]
            
        if busqueda:
            # Busca el texto en cualquiera de las columnas
            df_view = df_view[
                df_view.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
            ]

        # --- RESULTADOS ---
        col1, col2 = st.columns(2)
        col1.metric("Activos Encontrados", len(df_view))
        col2.metric("Archivos Procesados", len(lugares))
        
        st.dataframe(df_view, use_container_width=True)
        
    else:
        st.error("❌ No se pudieron extraer datos. Verifica que el archivo tenga la columna 'SERIE' o 'MODELO'.")
