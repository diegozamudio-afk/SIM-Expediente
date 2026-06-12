import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

# Configuración de página
st.set_page_config(page_title="ISAAC - Gaman", layout="wide")

# 1. Función de Conexión (Autenticación Moderna)
@st.cache_data(ttl=60)
def conectar_datos():
    raw_secrets = dict(st.secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
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
    
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    hoja = cliente.open("ISAAC - Expedientes").sheet1
    return hoja, pd.DataFrame(hoja.get_all_records())

# 2. Interfaz Principal
st.title("🚦 ISAAC - Gestión de Expedientes")

# Formulario de Carga
with st.expander("➕ Cargar Nuevo Expediente"):
    with st.form("form_carga"):
        col1, col2 = st.columns(2)
        fecha_ingreso = col1.date_input("Fecha de Ingreso", datetime.now())
        # EDITÁ ESTA LISTA CON TUS AGENTES REALES
        agentes = ["Juan Pérez", "Ana García", "Diego Lopez", "Lucía Martínez"] 
        responsable = col2.selectbox("Responsable", agentes)
        nro_expediente = st.text_input("Nro. de Expediente")
        asunto = st.text_area("Asunto")
        
        submit = st.form_submit_button("Guardar Expediente")
        if submit:
            try:
                hoja, _ = conectar_datos()
                hoja.append_row([str(fecha_ingreso), nro_expediente, asunto, "Solicitante", responsable])
                st.success("¡Expediente guardado con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
