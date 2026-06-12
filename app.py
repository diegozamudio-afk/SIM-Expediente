import streamlit as st
import gspread
import pandas as pd
import json

@st.cache_data(ttl=60)
def conectar_datos():
    # 1. Definimos el diccionario directamente desde los secretos
    # Usamos dict() para convertir el AttrDict en un diccionario normal
    raw_secrets = dict(st.secrets["gcp_service_account"])
    
    # 2. Creamos el diccionario que espera gspread
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
    
    # 3. Conectamos
    cliente = gspread.service_account_from_dict(credenciales_dict)
    hoja = cliente.open("ISAAC - Expedientes").sheet1
    return pd.DataFrame(hoja.get_all_records())
