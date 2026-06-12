import streamlit as st
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

# Configuración de página
st.set_page_config(page_title="ISAAC - Gaman", layout="wide")

# Función de conexión corregida (Autenticación robusta)
@st.cache_data(ttl=60)
def conectar_datos():
    # Obtener secretos de Streamlit (asegúrate de tenerlos configurados en tu repositorio)
    raw_secrets = dict(st.secrets["gcp_service_account"])
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Crear credenciales
    creds = Credentials.from_service_account_info(raw_secrets, scopes=scopes)
    cliente = gspread.authorize(creds)
    
    # Conexión al archivo
    hoja = cliente.open("ISAAC - Expedientes").sheet1
    return hoja, pd.DataFrame(hoja.get_all_records())

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
                hoja, _ = conectar_datos()
                fecha_ingreso = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                # Insertar fila (Asegúrate de que las columnas en Sheets coincidan exactamente con este orden)
                hoja.append_row([str(fecha_expediente), fecha_ingreso, nro_expediente, solicitante, "🟢", responsable, asunto])
                
                st.success("Expediente guardado con éxito")
                st.rerun() # Refresca para mostrar el dato nuevo
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# Visualización y Semáforo
try:
    _, df = conectar_datos()
    if not df.empty:
        # Procesamiento para semáforo visual
        df['Fecha_Expediente'] = pd.to_datetime(df['Fecha_Expediente'], errors='coerce')
        df['Dias'] = (pd.Timestamp.now() - df['Fecha_Expediente']).dt.days.abs()
        df['Estado'] = df['Dias'].apply(lambda d: '🔴' if d > 5 else ('🟡' if d > 3 else '🟢'))
        
        st.dataframe(df[['Estado', 'Fecha_Expediente', 'Fecha_Ingreso', 'Nro_Expediente', 'Solicitante', 'Responsable', 'Asunto']], 
                     use_container_width=True, hide_index=True)
    else:
        st.warning("No hay datos cargados en la hoja de cálculo.")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
