import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(page_title="BioInsights AI", layout="wide")

# Título de la aplicación
st.title("BioInsights AI 🧪")
st.markdown("Interpreta resultados bioquímicos y genera informes personalizados con IA.")

# Barra lateral para ofrecer el archivo de muestra
with st.sidebar:
    st.header("Descarga un archivo de muestra")
    st.markdown("Si no estás seguro del formato de los datos, puedes descargar un archivo de muestra:")
    
    # Contenido del archivo de muestra (CSV)
    sample_data = """Paciente,Glucosa,Colesterol,Hemoglobina,Ferritina
Paciente1,95,200,14.5,80
Paciente2,110,220,13.8,65
Paciente3,100,190,15.2,70
Paciente4,120,240,12.9,50
Paciente5,90,180,14.0,90"""
    
    # Convertir el contenido a un archivo descargable
    st.download_button(
        label="Descargar archivo de muestra (CSV)",
        data=sample_data,
        file_name="datos_bioquimicos_ejemplo.csv",
        mime="text/csv"
    )

# Cargar archivo CSV o Excel
uploaded_file = st.file_uploader("Carga un archivo CSV o Excel con los resultados del laboratorio:", type=["csv", "xlsx"])

if uploaded_file:
    # Leer el archivo
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Mostrar los datos cargados
    st.subheader("Datos cargados:")
    st.dataframe(df)

    # Generar gráficos interactivos
    st.subheader("Visualización de datos:")
    selected_column = st.selectbox("Selecciona una columna para visualizar:", df.columns)
    fig = px.histogram(df, x=selected_column, title=f"Distribución de {selected_column}")
    st.plotly_chart(fig)

    # Preparar datos para análisis con OpenRouter
    data_summary = df.describe().to_string()
    openrouter_input = f"Analiza los siguientes datos bioquímicos y proporciona interpretaciones clínicas relevantes:\n{data_summary}"

    # Botón para generar análisis con OpenRouter
    if st.button("Generar Análisis con OpenRouter"):
        # Obtener la API Key desde los secretos de Streamlit
        api_key = st.secrets["OPENROUTER_API_KEY"]

        # Endpoint de OpenRouter
        url = "https://openrouter.ai/api/v1/chat/completions"

        # Datos a enviar
        payload = {
            "model": "amazon/nova-lite-v1",
            "messages": [
                {
                    "role": "user",
                    "content": openrouter_input
                }
            ]
        }

        # Encabezados
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Realizar la solicitud POST
        response = requests.post(url, headers=headers, json=payload)

        # Procesar la respuesta
        if response.status_code == 200:
            openrouter_response = response.json()["choices"][0]["message"]["content"]
            st.subheader("Análisis generado por OpenRouter:")
            st.write(openrouter_response)
        else:
            st.error(f"Error al comunicarse con OpenRouter: {response.status_code} - {response.text}")

# Chatbot de consultas científicas
st.subheader("Chatbot de Consultas Bioquímicas")
user_question = st.text_input("Haz una pregunta sobre bioquímica o resultados de laboratorio:")

if user_question:
    # Obtener la API Key desde los secretos de Streamlit
    api_key = st.secrets["OPENROUTER_API_KEY"]

    # Endpoint de OpenRouter
    url = "https://openrouter.ai/api/v1/chat/completions"

    # Datos a enviar
    payload = {
        "model": "amazon/nova-lite-v1",
        "messages": [
            {
                "role": "user",
                "content": user_question
            }
        ]
    }

    # Encabezados
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Realizar la solicitud POST
    response = requests.post(url, headers=headers, json=payload)

    # Procesar la respuesta
    if response.status_code == 200:
        openrouter_response = response.json()["choices"][0]["message"]["content"]
        st.subheader("Respuesta de OpenRouter:")
        st.write(openrouter_response)
    else:
        st.error(f"Error al comunicarse con OpenRouter: {response.status_code} - {response.text}")
