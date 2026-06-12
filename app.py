import streamlit as st
import gspread
import pandas as pd
import json
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="ISAAC - Expedientes", layout="wide")

@st.cache_data(ttl=60)
def conectar_datos():
    # Cargamos credenciales
    raw_secrets = dict(st.secrets["gcp_service_account"])
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
    
    # Conexión
    cliente = gspread.service_account_from_dict(credenciales_dict)
    hoja = cliente.open("ISAAC - Expedientes").sheet1
    return pd.DataFrame(hoja.get_all_records())

# --- Interfaz ---
st.title("🚦 ISAAC - Gestión de Expedientes")

try:
    df = conectar_datos()
    
    if not df.empty:
        # Convertimos columna de fecha a formato datetime (asegúrate que en Sheets se llame 'Fecha_Ingreso')
        df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'], errors='coerce')
        
        # Calculamos demora
        hoy = pd.Timestamp.now()
        df['Dias_Demora'] = (hoy - df['Fecha_Ingreso']).dt.days
        
        # Lógica del Semáforo
        def get_semaforo(dias):
            if pd.isna(dias): return '⚪' # Sin fecha
            if dias <= 3: return '🟢'
            elif dias <= 5: return '🟡'
            else: return '🔴'
        
        df['Estado'] = df['Dias_Demora'].apply(get_semaforo)
        
        # Mostramos la tabla con el semáforo al principio
        columnas_a_mostrar = ['Estado', 'Nro_Expediente', 'Solicitante', 'Responsable', 'Dias_Demora']
        st.dataframe(df[columnas_a_mostrar], use_container_width=True, hide_index=True)
    else:
        st.warning("El archivo tiene encabezados pero no tiene filas de datos.")

except Exception as e:
    st.error(f"Error: {e}")
