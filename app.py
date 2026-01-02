import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Inventario Limpio", layout="wide")

def cargar_excel_limpio(archivo):
    try:
        # 1. ESCANEO: Leemos el archivo "crudo" sin encabezados
        df_raw = pd.read_excel(archivo, header=None)
        
        # 2. BÚSQUEDA DEL PUNTO CERO (Donde empiezan los datos reales)
        fila_encabezado = -1
        
        # Recorremos las primeras 20 filas buscando las palabras sagradas
        for i, row in df_raw.head(20).iterrows():
            fila_texto = row.astype(str).str.lower().str.cat(sep=' ')
            
            # Condición estricta: Debe tener "serie" Y ("descrip" O "bien")
            if 'serie' in fila_texto and ('descrip' in fila_texto or 'bien' in fila_texto):
                fila_encabezado = i
                break
        
        if fila_encabezado == -1:
            return None, "No se encontró la fila de encabezados (Serie/Descripción)."

        # 3. RECARGA QUIRÚRGICA: Leemos de nuevo, pero empezando EXACTAMENTE en esa fila
        # Esto elimina automáticamente todo lo que está arriba (Ministerio, Unidad Educativa, etc.)
        df = pd.read_excel(archivo, header=fila_encabezado)
        
        # 4. LIMPIEZA DE COLUMNAS FANTASMA
        # Borramos cualquier columna que empiece por "Unnamed" (las vacías a la derecha)
        cols_validas = [c for c in df.columns if not str(c).startswith('Unnamed')]
        df = df[cols_validas]
        
        # 5. LIMPIEZA DE FILAS BASURA (Firmas y pies de página)
        # Convertimos a texto para buscar palabras de cierre
        df = df.astype(str)
        
        # Filtramos filas que contengan "Recibí conforme", "Rector", etc.
        palabras_cierre = ['conforme', 'rector', 'custodio', 'atentamente', 'total', 'firma']
        mask_basura = df.apply(lambda row: any(p in row.astype(str).str.lower().str.cat(sep=' ') for p in palabras_cierre), axis=1)
        df = df[~mask_basura]
        
        # 6. Limpiar celdas vacías que dicen 'nan'
        df = df.replace('nan', '')
        
        return df, None
        
    except Exception as e:
        return None, str(e)

# --- INTERFAZ ---
st.title("✨ Inventario Bloque 2")

archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos:
    st.error("No hay archivos en el repositorio.")
else:
    with st.sidebar:
        st.header("Archivos")
        seleccion = st.selectbox("Selecciona Curso:", archivos)

    if seleccion:
        st.subheader(f"Archivo: {seleccion.replace('.xlsx', '')}")
        
        df_limpio, error = cargar_excel_limpio(seleccion)
        
        if error:
            st.error(f"⚠️ Error: {error}")
            st.info("Asegúrate que el Excel tenga las columnas 'SERIE' y 'DESCRIPCIÓN' o 'BIEN'.")
        else:
            # Buscador
            busqueda = st.text_input("🔍 Buscar activo:", placeholder="Escribe serie o nombre...")
            
            if busqueda:
                df_limpio = df_limpio[
                    df_limpio.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
                ]

            # TABLA LIMPIA (hide_index=True quita los números de la izquierda)
            st.dataframe(df_limpio, use_container_width=True, hide_index=True)
            st.caption(f"Mostrando {len(df_limpio)} ítems válidos.")
