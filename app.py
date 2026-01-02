import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Reporte Limpio", layout="wide")

# --- 1. DETECTIVE DE CABECERAS ---
# Buscamos dónde empieza la tabla real
CLAVES_CABECERA = ['serie', 'modelo', 'descripción', 'descripcion', 'bien', 'item', 'marca', 'cant']

def encontrar_fila_cabecera(archivo):
    try:
        df_temp = pd.read_excel(archivo, header=None, nrows=20)
        for i, row in df_temp.iterrows():
            fila_texto = [str(celda).lower() for celda in row.tolist()]
            # Si la fila tiene al menos 2 palabras clave (ej: "serie" y "modelo"), es la cabecera
            coincidencias = sum(1 for clave in CLAVES_CABECERA if any(clave in celda for celda in fila_texto))
            if coincidencias >= 2:
                return i
    except Exception:
        return 0
    return 0

# --- 2. LA ASPIRADORA DE DATOS (LIMPIEZA) ---
def limpiar_dataframe(df):
    # A. Eliminar columnas que se llamen "Unnamed" (Columnas vacías a la derecha)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False)]
    
    # B. Convertir todo a texto para evitar errores y facilitar la limpieza
    df = df.astype(str)
    
    # C. Eliminar filas "Administrativas" (Firmas, Títulos, Totales)
    # Palabras prohibidas en la primera columna válida
    PALABRAS_BASURA = ['acta', 'entrega', 'recepción', 'conforme', 'rector', 'custodio', 'total', 'firma', 'atentamente', 'unidad educativa', 'nan', 'none']
    
    def es_fila_basura(row):
        # Convertimos toda la fila a un solo texto largo
        texto_fila = " ".join(row.values).lower()
        # Si contiene palabras administrativas y NO parece un item (corto), es basura
        if any(basura in texto_fila for basura in PALABRAS_BASURA):
            # Excepción: Si dice "Total" pero parece un dato, cuidado. 
            # Pero para firmas y encabezados, esto funciona bien.
            return True
        return False

    # Filtramos las filas
    df = df[~df.apply(es_fila_basura, axis=1)]
    
    # D. Eliminar filas donde la descripción sea muy corta o vacía (ej: "-")
    # Asumimos que la columna 1 o 2 suele ser la descripción
    if len(df.columns) > 1:
        col_referencia = df.columns[1] # Tomamos la segunda columna como referencia
        df = df[df[col_referencia].str.len() > 1] # Si tiene 1 letra o es vacía, adiós

    # E. Reemplazar 'nan' por espacios vacíos visuales
    df = df.replace('nan', '')
    
    return df

# --- 3. INTERFAZ ---
st.title("📂 Visor de Inventario (Versión Limpia)")

archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos:
    st.error("⚠️ No hay archivos Excel cargados.")
else:
    with st.sidebar:
        st.header("Navegación")
        seleccion = st.selectbox("Selecciona el Curso:", archivos)

    if seleccion:
        try:
            # 1. Encontrar dónde empieza
            fila_inicio = encontrar_fila_cabecera(seleccion)
            
            # 2. Leer
            df = pd.read_excel(seleccion, header=fila_inicio)
            
            # 3. LIMPIAR (Aquí ocurre la magia)
            df_limpio = limpiar_dataframe(df)
            
            # 4. Mostrar
            st.divider()
            st.subheader(f"📋 Reporte: {seleccion.replace('.xlsx', '')}")
            
            col1, col2 = st.columns(2)
            col1.metric("Ítems Válidos", len(df_limpio))
            col2.caption("Se han eliminado filas de firmas y títulos automáticamente.")
            
            # Buscador
            busqueda = st.text_input("🔍 Buscar:", placeholder="Ej: Silla...")
            if busqueda:
                df_limpio = df_limpio[
                    df_limpio.apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)
                ]

            # Tabla sin índice numérico a la izquierda
            st.dataframe(df_limpio, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"Error: {e}")
