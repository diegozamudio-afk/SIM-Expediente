import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="ISAAC - Gestión Gaman", layout="wide")

# --- CONEXIÓN BLINDADA ---
def obtener_hoja():
    raw_secrets = dict(st.secrets["gcp_service_account"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(raw_secrets, scopes=scopes)
    cliente = gspread.authorize(creds)
    return cliente.open("ISAAC - Expedientes").sheet1

st.title("🚦 ISAAC - Gestión de Expedientes")

# --- FORMULARIO DE CARGA ---
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
                hoja = obtener_hoja()
                fecha_ingreso = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                # GUARDAMOS "Pendiente" en lugar de un emoji fijo
                hoja.append_row([str(fecha_expediente), fecha_ingreso, nro_expediente, solicitante, "Pendiente", responsable, asunto])
                
                st.success("Expediente guardado correctamente.")
            except Exception as e:
                st.error(f"Error técnico: {e}")

# --- VISUALIZACIÓN Y SEMÁFORO AUTOMÁTICO ---
try:
    hoja = obtener_hoja()
    data = hoja.get_all_records()
    if data:
        df = pd.DataFrame(data)
        
        # Procesamiento de fechas
        df['Fecha_Expediente'] = pd.to_datetime(df['Fecha_Expediente'], dayfirst=True, errors='coerce').dt.normalize()
        hoy = pd.Timestamp.now().normalize()
        df['Dias_Demora'] = (hoy - df['Fecha_Expediente']).dt.days
        
        # Lógica del semáforo (Prioridad: Blanco para hoy)
        def get
