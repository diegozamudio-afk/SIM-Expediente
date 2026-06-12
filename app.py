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
                fecha_exp_str = fecha_expediente.strftime("%d/%m/%Y")
                fecha_ingreso = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                hoja.append_row([fecha_exp_str, fecha_ingreso, nro_expediente, solicitante, "Pendiente", responsable, asunto])
                st.success("Expediente guardado correctamente.")
            except Exception as e:
                st.error(f"Error técnico: {e}")

# --- VISUALIZACIÓN Y SEMÁFORO AUTOMÁTICO ---
try:
    hoja = obtener_hoja()
    data = hoja.get_all_records()
    if data:
        df = pd.DataFrame(data)
        
        # 1. Limpieza de fechas
        df['Fecha_Expediente'] = pd.to_datetime(df['Fecha_Expediente'].astype(str).str.strip(), dayfirst=True, errors='coerce')
        
        mask = df['Fecha_Expediente'].isna()
        if mask.any():
            df.loc[mask, 'Fecha_Expediente'] = pd.to_datetime(df.loc[mask, 'Fecha_Expediente'].astype(str), errors='coerce')

        # 2. Cálculo de días
        hoy = pd.Timestamp.now().normalize()
        df['Dias_Demora'] = (hoy - df['Fecha_Expediente'].dt.normalize()).dt.days
        
        # 3. Lógica semáforo (Indentación corregida)
        def get_semaforo(dias):
            if pd.isna(dias): return '⚪'
            if dias <= 0: return '⚪'
            if dias <= 3: return '🟢'
            elif dias <= 5: return '🟡'
            else: return '🔴'
        
        df['Estado'] = df['Dias_Demora'].apply(get_semaforo)
        
        # 4. Formateo visual
        df['Fecha_Visual'] = df['Fecha_Expediente'].dt.strftime('%d/%m/%Y')
        
        # 5. Mostrar tabla
        cols = ['Estado', 'Fecha_Visual', 'Fecha_Ingreso', 'Nro_Expediente', 'Solicitante', 'Responsable', 'Asunto']
        st.dataframe(df[[c for c in cols if c in df.columns]], use_container_width=True, hide_index=True)
    else:
        st.warning("No hay datos cargados.")
except Exception as e
