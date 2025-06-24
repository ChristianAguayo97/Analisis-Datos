import streamlit as st
import pandas as pd
import requests
import io

from ydata.sdk.quality import quality_report
from streamlit.components.v1 import html

st.set_page_config(layout="wide", page_title="Informe de Calidad de Datos", page_icon="📊")
st.title("📊 Reportes de Calidad de Datos")

urls = {
    "Dataset 1": "https://docs.google.com/spreadsheets/d/1-vy4P-LD4uIWvDo5pTIgTMYzu2IjCUStufATPAorRPk/export?format=csv",
    "Dataset 2": "https://docs.google.com/spreadsheets/d/1-OmX0o00qRFmfABPovDOn3_UGpIjJvxgzzc3fgDFIik/export?format=csv",
    "Dataset 3": "https://docs.google.com/spreadsheets/d/1V59Bx9kBOvfgUMdEwgMye8qLtCg4hWsB36Jp-uxjkoY/export?format=csv",
}

def detectar_y_leer_csv(content, separador=",", max_filas=5):
    pre_df = pd.read_csv(io.StringIO(content), sep=separador, header=None, nrows=max_filas)
    for i in range(max_filas):
        posibles_columnas = pre_df.iloc[i]
        if posibles_columnas.notna().sum() >= 3 and posibles_columnas.astype(str).str.len().mean() > 3:
            return pd.read_csv(io.StringIO(content), sep=separador, header=i)
    return pd.read_csv(io.StringIO(content), sep=separador, header=None)

@st.cache_data(show_spinner=False)
def cargar_df(url):
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return detectar_y_leer_csv(respuesta.text)

@st.cache_data(show_spinner=True)
def generar_reporte(df, nombre):
    report = quality_report(df, name=nombre)
    return report.to_html()

nombre_dataset = st.selectbox("Selecciona un dataset:", list(urls.keys()))

if nombre_dataset:
    url = urls[nombre_dataset]
    st.info(f"Descargando datos desde Google Sheets: {nombre_dataset}")
    df = cargar_df(url)
    st.success(f"Datos cargados correctamente. Filas: {len(df)}, Columnas: {len(df.columns)}")

    html_string = generar_reporte(df, nombre_dataset)
    html(html_string, height=1000, scrolling=True)
