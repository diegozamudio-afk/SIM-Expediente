import streamlit as st
import gspread
import pandas as pd
from datetime import datetime

# --- Interfaz ---
st.title("🚦 ISAAC - Gestión de Expedientes")

try:
    df = conectar_datos() # (Tu función de conexión que ya funciona)
    
    if not df.empty:
        # 1. Aseguramos que la fecha sea real
        df['Fecha_Ingreso'] = pd.to_datetime(df['Fecha_Ingreso'], dayfirst=True, errors='coerce')
        
        # 2. Corregimos la resta: Absoluto para que no de negativo
        hoy = pd.Timestamp.now()
        df['Dias_Demora'] = (hoy - df['Fecha_Ingreso']).dt.days.abs()
        
        # 3. Lógica del Semáforo
        def get_semaforo(dias):
            if pd.isna(dias): return '⚪'
            if dias <= 3: return '🟢'
            elif dias <= 5: return '🟡'
            else: return '🔴'
        
        df['Estado'] = df['Dias_Demora'].apply(get_semaforo)
        
        # 4. Mostrar incluyendo el Asunto (Asegurate que el nombre en Sheets sea 'Asunto')
        columnas_a_mostrar = ['Estado', 'Nro_Expediente', 'Asunto', 'Solicitante', 'Responsable', 'Dias_Demora']
        
        # Filtramos solo las que existen para no romper la app
        columnas_existentes = [c for c in columnas_a_mostrar if c in df.columns]
        
        st.dataframe(df[columnas_existentes], use_container_width=True, hide_index=True)
    else:
        st.warning("La planilla está conectada pero no tiene datos.")

except Exception as e:
    st.error(f"Error: {e}")
