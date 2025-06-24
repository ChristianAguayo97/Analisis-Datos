import requests
import zipfile
import io
from pathlib import Path

# Lista con las URLs de exportación CSV de Google Sheets
urls_csv = [
    "https://docs.google.com/spreadsheets/d/1-vy4P-LD4uIWvDo5pTIgTMYzu2IjCUStufATPAorRPk/export?format=csv",
    "https://docs.google.com/spreadsheets/d/1-OmX0o00qRFmfABPovDOn3_UGpIjJvxgzzc3fgDFIik/export?format=csv",
]

# Nombre de archivo ZIP a crear
nombre_zip = "mis_csvs.zip"

def descargar_csv(url):
    response = requests.get(url)
    response.raise_for_status()  # Para errores HTTP
    return response.content

def crear_zip_con_csvs(urls, nombre_zip):
    with zipfile.ZipFile(nombre_zip, 'w') as archivo_zip:
        for i, url in enumerate(urls, start=1):
            contenido_csv = descargar_csv(url)
            nombre_archivo = f"archivo_{i}.csv"  # Podés cambiar nombre si querés
            archivo_zip.writestr(nombre_archivo, contenido_csv)
            print(f"Agregado al ZIP: {nombre_archivo}")

if __name__ == "__main__":
    crear_zip_con_csvs(urls_csv, nombre_zip)
    print(f"\nArchivo ZIP creado: {nombre_zip}")
