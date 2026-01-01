import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Reporte de Inventario", layout="wide")

# --- 1. FUNCIÓN DE RASTREO (Detecta dónde empieza lo bueno) ---
CLAVES_CABECERA = ['serie', 'modelo', 'descripción', 'descripcion', 'bien', 'item', 'marca', 'cant']

def encontrar_fila_cabecera(archivo):
    """
    Escanea las primeras 20 filas para encontrar la línea exacta de los títulos.
    """
    try:
        # Leemos sin cabecera para escanear texto puro
        df_temp = pd.read_excel(archivo, header=None, nrows=20)
        
        for i, row in df_temp.iterrows():
            # Convertimos la fila a texto minúscula
            fila_texto = [str(celda).lower() for celda in row.tolist()]
            
            # Si una fila tiene "serie" Y "modelo" (o variantes), esa es la cabecera.
            coincidencias = 0
            for clave in CLAVES_CABECERA:
                if any(clave in celda for celda in fila_texto):
                    coincidencias += 1
            
            # Si encontramos al menos 2 palabras clave en la misma fila, es la correcta
            if coincidencias >= 2:
                return i
    except Exception:
        return 0
    return 0

# --- 2. INTERFAZ DE USUARIO ---
st.title("📂 Visor de Inventario por Curso")
st.markdown("Selecciona un archivo de la lista para ver su contenido limpio.")

archivos_disponibles = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]

if not archivos_disponibles:
    st.error("⚠️ No hay archivos Excel cargados en el repositorio.")
else:
    # --- MENÚ LATERAL ---
    with st.sidebar:
        st.header("Navegación")
        archivo_seleccionado = st.selectbox(
            "📍 Selecciona el Curso:", 
            archivos_disponibles
        )
        st.info("👆 Cambia de archivo aquí para ver otro curso.")

    # --- ÁREA PRINCIPAL ---
    if archivo_seleccionado:
        try:
            # 1. Detectar fila de títulos
            fila_inicio = encontrar_fila_cabecera(archivo_seleccionado)
            
            # 2. Leer el Excel DESDE esa fila (Ignora lo de arriba)
            df = pd.read_excel(archivo_seleccionado, header=fila_inicio)
            
            # --- 3. LIMPIEZA VISUAL (LA MAGIA) ---
            
            # A. Eliminar columnas que se llamen "Unnamed" (Columnas vacías)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            # B. Eliminar filas que estén totalmente vacías
            df = df.dropna(how='all')
            
            # C. Blindaje: Convertir todo a texto para evitar error rojo
            df = df.astype(str)
            df = df.replace('nan', '') # Quitar los 'nan' feos y dejar vacío
            
            # --- 4. MOSTRAR RESULTADOS ---
            st.divider()
            st.subheader(f"📋 Reporte: {archivo_seleccionado.replace('.xlsx', '')}")
            
            # Métricas
            col1, col2 = st.columns(2)
            col1.metric("Total de Ítems", len(df))
            col2.caption(f"Datos detectados a partir de la fila {fila_inicio + 1}")

            # Buscador
            busqueda = st.text_input("🔍 Filtro Rápido (Escribe serie, nombre o modelo):", placeholder="Ej: Silla, CP-100...")
            
            df_visible = df.copy()
            if busqueda:
                df_visible = df_visible[
                    df_visible.apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)
                ]

            # TABLA FINAL LIMPIA
            # hide_index=True quita los números 0,1,2 de la izquierda para que parezca un reporte oficial
            st.dataframe(df_visible, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"❌ Ocurrió un error leyendo el archivo: {e}")
