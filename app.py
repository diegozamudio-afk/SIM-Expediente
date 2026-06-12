import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="ISAAC - Gestión Gaman", layout="wide")

# Función de conexión simplificada
def obtener_hoja():
    raw_secrets = dict(st.secrets["gcp_service_account"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(raw_secrets, scopes=scopes)
    cliente = gspread.authorize(creds)
    return cliente.open("ISAAC - Expedientes").sheet1

st.title("🚦 ISAAC - Gestión de Expedientes")

# Formulario de carga
with st.expander("➕ Cargar Nuevo Expediente"):
    with st.form("form_carga", clear_on_submit=True):
        col1, col2 = st.columns(2)
        fecha_expediente = col1.date_input("Fecha del Expediente", datetime.now())
        responsable = col2.selectbox("Responsable", ["Juan Pérez", "Ana García", "Diego Lopez", "Lucía Martínez"])
        nro_expediente = st.text_input("Nro. de Expediente")
        solicitante = st.text_input("Solicitante")
        asunto = st.text_area("Asunto")
        
        if st.form_submit_button("Guardar Expediente"):
            try:
                # CONEXIÓN DENTRO DEL BOTÓN (Se abre y cierra al instante)
                hoja = obtener_hoja()
                fecha_ingreso = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                # Guardar
                hoja.append_row([str(fecha_expediente), fecha_ingreso, nro_expediente, solicitante, "🟢", responsable, asunto])
                
                st.success("Expediente guardado con éxito")
                # No usar st.rerun() aquí si sigue fallando, probemos primero sin él
            except Exception as e:
                st.error(f"Error técnico al guardar: {e}")

# Visualización (Conexión separada para leer)
try:
    hoja = obtener_hoja()
    df = pd.DataFrame(hoja.get_all_records())
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
except:
    st.warning("No se pudieron cargar los datos.")
