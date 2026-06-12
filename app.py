import streamlit as st
import pandas as pd
import gspread
import json
from datetime import datetime

st.set_page_config(page_title="ISAAC - Gestión de Expedientes", layout="wide")

@st.cache_data(ttl=60)
def conectar_datos():
    # 1. Accedemos a los secretos y lo convertimos a un dict común
    secrets_dict = dict(st.secrets["gcp_service_account"])
    
    # 2. Convertimos el diccionario a un JSON string y luego lo cargamos
    # Esto soluciona el problema de que sea un 'AttrDict'
    credenciales_dict = json.loads(json.dumps(secrets_dict))
    
    # 3. Corregimos el salto de línea en la clave privada
    credenciales_dict["private_key"] = credenciales_dict["private_key"].replace("\\n", "\n")
    
    cliente = gspread.service_account_from_dict(credenciales_dict)
    hoja = cliente.open("ISAAC - Expedientes").sheet1
    return pd.DataFrame(hoja.get_all_records())

st.title("🚦 ISAAC - Gestión y Control de Expedientes")

try:
    df = conectar_datos()
    if not df.empty:
        # Convertimos ambas fechas
        df['Fecha_Expediente'] = pd.to_datetime(df['Fecha_Expediente'])
        df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'])
        
        # Calculamos antigüedad respecto al ingreso actual para el semáforo
        df['Dias_Demora'] = (datetime.now() - df['Fecha_Ingreso']).dt.days
        
        # Lógica de Semáforo
        def obtener_color(dias):
            if dias <= 3: return '🟢'
            elif dias <= 5: return '🟡'
            else: return '🔴'
        
        df['Estado_Semaforo'] = df['Dias_Demora'].apply(obtener_color)

        # Alertas críticas
        criticos = df[df['Dias_Demora'] > 5]
        if not criticos.empty:
            st.error(f"⚠️ ¡ATENCIÓN! {len(criticos)} expedientes críticos.")
            st.warning("Revisar responsables de expedientes en ROJO.")

        # Tabla con ambas fechas
        st.subheader("📋 Detalle General")
        st.dataframe(
            df[['Estado_Semaforo', 'Nro_Expediente', 'Fecha_Expediente', 'Fecha_Ingreso', 'Dias_Demora', 'Responsable', 'Estado']],
            use_container_width=True, hide_index=True
        )
    else:
        st.warning("La planilla está vacía.")
except Exception as e:
    st.error(f"Error al conectar: {e}")
