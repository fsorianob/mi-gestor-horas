import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import date

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="LifeTracker Cloud",
    page_icon="🚀",
    layout="wide"
)

# Constante para el archivo de datos
# NOTA: En Streamlit Community Cloud, los archivos locales (CSV) son efímeros.
# Se reinician si la app se "duerme". Para persistencia real a largo plazo,
# en el futuro deberás conectar Google Sheets o una Base de Datos.
DB_FILE = "datos_horas.csv"

# --- FUNCIONES DE GESTIÓN DE DATOS ---
def cargar_datos():
    """Carga los datos asegurando los tipos correctos."""
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # Convertir fecha a datetime y luego a date para evitar problemas de hora
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
            return df
        except Exception as e:
            st.error(f"Error leyendo el archivo: {e}")
            return pd.DataFrame(columns=['Fecha', 'Categoria', 'Horas'])
    return pd.DataFrame(columns=['Fecha', 'Categoria', 'Horas'])

def guardar_datos(df):
    """Guarda el dataframe en CSV."""
    df.to_csv(DB_FILE, index=False)

# --- INTERFAZ PRINCIPAL ---
st.title("🚀 Mi Gestor de Vida (Cloud Edition)")
st.markdown("---")

# Cargar estado inicial
if 'df_datos' not in st.session_state:
    st.session_state.df_datos = cargar_datos()

df_datos = st.session_state.df_datos

# --- SIDEBAR: REGISTRO ---
with st.sidebar:
    st.header("📝 Nuevo Registro")
    with st.form("formulario_registro", clear_on_submit=True):
        fecha = st.date_input("Fecha:", date.today())
        categoria = st.selectbox("Categoría:", ["Trabajo", "Estudio", "Sueño", "Gimnasio", "Ocio", "Transporte"])
        horas = st.number_input("Horas:", min_value=0.1, max_value=24.0, step=0.5)
        
        submitted = st.form_submit_button("💾 Guardar Actividad")
        
        if submitted:
            nuevo_registro = pd.DataFrame([[fecha, categoria, horas]], columns=['Fecha', 'Categoria', 'Horas'])
            # Actualizar estado y guardar
            st.session_state.df_datos = pd.concat([df_datos, nuevo_registro], ignore_index=True)
            guardar_datos(st.session_state.df_datos)
            st.success("¡Registro añadido!")
            st.rerun()

# --- DASHBOARD PRINCIPAL ---
if not df_datos.empty:
    # 1. KPIs (Indicadores Clave)
    col1, col2, col3 = st.columns(3)
    total_horas = df_datos['Horas'].sum()
    cat_mas_frecuente = df_datos['Categoria'].mode()[0] if not df_datos['Categoria'].empty else "N/A"
    promedio_diario = df_datos.groupby('Fecha')['Horas'].sum().mean()

    col1.metric("Total Horas Registradas", f"{total_horas:.1f} h")
    col2.metric("Enfoque Principal", cat_mas_frecuente)
    col3.metric("Promedio Diario", f"{promedio_diario:.1f} h")

    st.markdown("---")

    # 2. Pestañas de Visualización y Edición
    tab1, tab2 = st.tabs(["📊 Análisis Visual", "📋 Edición de Datos"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            # Gráfico de Torta
            fig_pie = px.pie(df_datos, values='Horas', names='Categoria', title='Distribución de tu Tiempo', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            # Gráfico de Barras por Día
            df_diario = df_datos.groupby('Fecha')['Horas'].sum().reset_index()
            fig_bar = px.bar(df_diario, x='Fecha', y='Horas', title='Evolución Diaria')
            # Línea de referencia de 24h
            fig_bar.add_hline(y=24, line_dash="dot", annotation_text="Límite 24h")
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.info("💡 Puedes editar las celdas directamente. Usa la tecla 'Supr' para borrar filas seleccionadas.")
        
        # Data Editor: Permite editar el DataFrame visualmente
        df_editado = st.data_editor(
            df_datos,
            num_rows="dynamic", # Permite añadir y borrar filas
            column_config={
                "Fecha": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
                "Categoria": st.column_config.SelectboxColumn("Categoría", options=["Trabajo", "Estudio", "Sueño", "Gimnasio", "Ocio", "Transporte"]),
                "Horas": st.column_config.NumberColumn("Horas", format="%.1f h")
            },
            use_container_width=True,
            key="editor_datos"
        )

        # Botón para guardar cambios manuales de la tabla
        if st.button("🔄 Actualizar Tabla"):
            st.session_state.df_datos = df_editado
            guardar_datos(df_editado)
            st.success("Tabla actualizada correctamente")
            st.rerun()

else:
    st.info("👋 ¡Bienvenido! Usa la barra lateral para registrar tu primera actividad.")