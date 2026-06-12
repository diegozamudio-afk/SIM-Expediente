import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# 1. DEFINIMOS LA FUNCIÓN PRIMERO
@st.cache_data(ttl=60)
def conectar_datos():
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
    cliente = gspread.service_account_from_dict(credenciales_dict)
    hoja = cliente.open("ISAAC - Expedientes").sheet1
    return pd.DataFrame(hoja.get_all_records())

# 2. LUEGO HACEMOS LA LÓGICA DE INTERFAZ
st.title("🚦 ISAAC - Gestión de Expedientes")

try:
    # AQUÍ LLAMAMOS A LA FUNCIÓN QUE YA DEFINIMOS ARRIBA
    df = conectar_datos()
    
    if not df.empty:
        # Procesamiento
        df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'], dayfirst=True, errors='coerce')
        hoy = pd.Timestamp.now()
        df['Dias_Demora'] = (hoy - df['Fecha_Ingreso']).dt.days.abs()
        
        def get_semaforo(dias):
            if pd.isna(dias): return '⚪'
            if dias <= 3: return '🟢'
            elif dias <= 5: return '🟡'
            else: return '🔴'
        
        df['Estado'] = df['Dias_Demora'].apply(get_semaforo)
        
        # Mostrar
        columnas_a_mostrar = ['Estado', 'Nro_Expediente', 'Asunto', 'Solicitante', 'Responsable', 'Dias_Demora']
        columnas_existentes = [c for c in columnas_a_mostrar if c in df.columns]
        
        st.dataframe(df[columnas_existentes], use_container_width=True, hide_index=True)
    else:
        st.warning("La planilla está conectada pero no tiene datos.")

except Exception as e:
    st.error(f"Error al ejecutar: {e}")
