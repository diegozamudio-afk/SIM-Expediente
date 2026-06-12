import streamlit as st
import pandas as pd
import gspread
import json
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="ISAAC - Expedientes", layout="wide")

# Conexión directa y simplificada
@st.cache_data(ttl=60)
def conectar_datos():
    credenciales_dict = json.loads(st.secrets["gcp_service_account"])
    cliente = gspread.service_account_from_dict(credenciales_dict)
    hoja = cliente.open("ISAAC - Expedientes").sheet1
    return pd.DataFrame(hoja.get_all_records())

st.title("🚦 ISAAC - Gestión y Control de Expedientes")

try:
    df = conectar_datos()
    
    if not df.empty:
        # Lógica de Semáforo
        df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'])
        df['Dias_Antiguedad'] = (datetime.now() - df['Fecha_Ingreso']).dt.days
        
        def obtener_color(dias):
            if dias <= 3: return '🟢'
            elif dias <= 5: return '🟡'
            else: return '🔴'
        
        df['Estado_Visual'] = df['Dias_Antiguedad'].apply(obtener_color)

        # KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Expedientes", len(df))
        c2.metric("En Alerta (Rojo)", len(df[df['Dias_Antiguedad'] > 5]))
        c3.metric("Al Día (Verde)", len(df[df['Dias_Antiguedad'] <= 3]))

        st.markdown("---")
        
        # Tabla Interactiva
        st.subheader("📋 Detalle de Expedientes")
        st.dataframe(
            df[['Estado_Visual', 'Nro_Expediente', 'Solicitante', 'Estado', 'Dias_Antiguedad']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("La planilla está vacía. Por favor, carga datos.")
        
except Exception as e:
    st.error(f"Error al conectar: {e}")

if st.button("🔄 Actualizar Datos"):
    st.rerun()
