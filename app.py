import streamlit as st
import gspread
import pandas as pd
import json

# Configuración inicial de la página
st.set_page_config(page_title="ISAAC - Gestión de Expedientes", layout="wide")

@st.cache_data(ttl=60)
def conectar_datos():
    # 1. Cargamos el diccionario desde los Secrets de Streamlit
    raw_secrets = dict(st.secrets["gcp_service_account"])
    
    # 2. Reconstruimos el diccionario de credenciales correctamente
    credenciales_dict = {
        "type": raw_secrets["type"],
        "project_id": raw_secrets["project_id"],
        "private_key_id": raw_secrets["private_key_id"],
        "private_key": raw_secrets["private_key"].replace("\\n", "\n"),
        "client_email": raw_secrets["client_email"],
        "client_id": raw_secrets["client_id"],
        "auth_uri": raw_secrets["auth_uri"],
        "token_uri": raw_secrets["token_uri"],
        "auth_provider_x509_cert_url": raw_secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": raw_secrets["client_x509_cert_url"]
    }
    
    # 3. Autenticación y lectura
    cliente = gspread.service_account_from_dict(credenciales_dict)
    archivo = cliente.open("ISAAC - Expedientes")
    hoja = archivo.sheet1
    datos = hoja.get_all_records()
    
    # Debug visual: si sale en blanco, acá verás cuántas filas leyó
    st.sidebar.write(f"Filas encontradas: {len(datos)}")
    
    return pd.DataFrame(datos)

# --- Interfaz Principal ---
st.title("🚦 ISAAC - Gestión de Expedientes")

try:
    df = conectar_datos()
    
    if not df.empty:
        st.write("### Lista de Expedientes")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("El archivo 'ISAAC - Expedientes' no tiene datos. Revisá tu Google Sheets.")
        
except Exception as e:
    st.error(f"Error al conectar: {e}")
    st.info("Asegúrate de que el bot tenga permisos de Editor en el Google Sheets.")
