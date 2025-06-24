import streamlit as st
import pandas as pd
import requests
from ydata_profiling import ProfileReport
from streamlit.components.v1 import html
import io
import csv
import os
import hashlib

# Crear directorio para reportes si no existe
REPORT_DIR = "reportes_html"
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

st.set_page_config(layout="wide", page_title="Informe de Calidad de Datos", page_icon="📊")
st.title("📊 Reportes de Calidad de Datos")

urls = {
    "Dataset 1": "https://docs.google.com/spreadsheets/d/1-vy4P-LD4uIWvDo5pTIgTMYzu2IjCUStufATPAorRPk/export?format=csv",
    "Dataset 2": "https://docs.google.com/spreadsheets/d/1-OmX0o00qRFmfABPovDOn3_UGpIjJvxgzzc3fgDFIik/export?format=csv",
    "Dataset 3": "https://docs.google.com/spreadsheets/d/1V59Bx9kBOvfgUMdEwgMye8qLtCg4hWsB36Jp-uxjkoY/export?format=csv",
}

def generar_hash(url):
    """Genera hash único para identificar dataset"""
    return hashlib.md5(url.encode()).hexdigest()

def obtener_ruta_reporte(nombre):
    """Obtiene ruta del archivo HTML para el reporte"""
    hash_url = generar_hash(urls[nombre])
    return os.path.join(REPORT_DIR, f"{nombre}_{hash_url}.html")

def detectar_y_leer_csv(content, max_filas=10):
    try:
        dialect = csv.Sniffer().sniff(content[:1024])
        separator = dialect.delimiter
    except:
        separator = ","
    
    pre_df = pd.read_csv(io.StringIO(content), sep=separator, header=None, nrows=5)

    header_row = None
    for i in range(len(pre_df)):
        row = pre_df.iloc[i]
        non_empty = row.dropna()
        if len(non_empty) >= max(3, len(pre_df.columns) // 2):
            avg_len = non_empty.astype(str).str.len().mean()
            if avg_len > 4:
                header_row = i
                break

    if header_row is not None:
        df = pd.read_csv(io.StringIO(content), sep=separator, header=header_row)
    else:
        df = pd.read_csv(io.StringIO(content), sep=separator)
    
    # Limpiar columnas
    df.columns = df.columns.astype(str).str.strip().str.replace(r"\s+", "_", regex=True)
    return df

@st.cache_data(show_spinner="Cargando dataset...")
def cargar_df(url):
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return detectar_y_leer_csv(respuesta.text)

def generar_reporte(df, nombre):
    perfil = ProfileReport(df, title=f"Reporte para {nombre}", explorative=True)
    return perfil.to_html()

# Interfaz de usuario
nombre_dataset = st.selectbox("Selecciona un dataset:", list(urls.keys()))
actualizar = st.checkbox("Forzar actualización del reporte")

if nombre_dataset:
    url = urls[nombre_dataset]
    ruta_reporte = obtener_ruta_reporte(nombre_dataset)

    # Cargar desde caché si existe y no se fuerza actualización
    if os.path.exists(ruta_reporte) and not actualizar:
        st.info(f"📁 Cargando reporte previamente generado para {nombre_dataset}")
        with open(ruta_reporte, "r", encoding="utf-8") as f:
            html_string = f.read()
    else:
        try:
            with st.spinner(f"Procesando {nombre_dataset} (esto puede tomar unos minutos)..."):
                df = cargar_df(url)

                # Vista previa de datos
                st.subheader(f"Vista previa: {nombre_dataset}")
                vista_previa_n = st.slider("Filas a mostrar:", 1, 20, 3)
                st.dataframe(df.head(vista_previa_n))

                # Generar nuevo reporte
                html_string = generar_reporte(df, nombre_dataset)

                # Guardar reporte localmente
                with open(ruta_reporte, "w", encoding="utf-8") as f:
                    f.write(html_string)
                st.success("✅ Reporte generado y guardado localmente")
        except Exception as e:
            st.error(f"❌ Error al generar el reporte: {e}")
            st.stop()

    # Mostrar reporte
    html(html_string, height=1000, scrolling=True)

    # Opción para descargar el reporte
    with st.expander("📥 Descargar Reporte"):
        st.download_button(
            label="Descargar como HTML",
            data=html_string,
            file_name=f"reporte_{nombre_dataset.replace(' ', '_')}.html",
            mime="text/html"
        )

# Botón para limpiar reportes antiguos
with st.expander("🧹 Opciones avanzadas"):
    if st.button("Eliminar todos los reportes guardados"):
        for archivo in os.listdir(REPORT_DIR):
            os.remove(os.path.join(REPORT_DIR, archivo))
        st.success("Todos los reportes han sido eliminados.")
