import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

# Configuración de página
st.set_page_config(page_title="ISAAC - Gaman", layout="wide")

# 1. Función de Conexión
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

with st.expander("➕ Cargar Nuevo Expediente"):
    with st.form("form_carga"):
        # La fecha ya no se pide, se toma automático al guardar
        agentes = ["Juan Pérez", "Ana García", "Diego Lopez", "Lucía Martínez"]
        responsable = st.selectbox("Responsable", agentes)
        nro_expediente = st.text_input("Nro. de Expediente")
        asunto = st.text_area("Asunto")
        
        submit = st.form_submit_button("Guardar Expediente")
        if submit:
            try:
                # Obtenemos la fecha ACTUAL del sistema en el momento del click
                fecha_actual = datetime.now().strftime("%d/%m/%Y")
                hoja, _ = conectar_datos()
                # Se guarda la fecha automática
                hoja.append_row([fecha_actual, nro_expediente, asunto, "Solicitante", responsable])
                st.success(f"Expediente guardado con fecha {fecha_actual}")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# Visualización
try:
    _, df = conectar_datos()
    if not df.empty:
        # Importante: dayfirst=True para que tome el formato DD/MM/AAAA correctamente
        df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'], dayfirst=True, errors='coerce')
        df['Dias_Demora'] = (pd.Timestamp.now() - df['Fecha_Ingreso']).dt.days.abs()
        
        def get_semaforo(dias):
            if pd.isna(dias): return '⚪'
            if dias <= 3: return '🟢'
            elif dias <= 5: return '🟡'
            else: return '🔴'
        
        df['Estado'] = df['Dias_Demora'].apply(get_semaforo)
        columnas = ['Estado', 'Nro_Expediente', 'Asunto', 'Solicitante', 'Responsable', 'Dias_Demora']
        st.dataframe(df[[c for c in columnas if c in df.columns]], use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
