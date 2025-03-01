import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(page_title="BioInsights AI", layout="wide")

# Título de la aplicación
st.title("BioInsights AI 🧪")
st.markdown("Interpreta resultados bioquímicos y genera informes personalizados con IA.")

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

    # Preparar datos para análisis con Gemini
    data_summary = df.describe().to_string()
    gemini_input = f"Analiza los siguientes datos bioquímicos y proporciona interpretaciones clínicas relevantes:\n{data_summary}"

    # Botón para generar análisis con Gemini
    if st.button("Generar Análisis con Gemini"):
        # Obtener la API Key desde los secretos de Streamlit
        api_key = st.secrets["GEMINI_API_KEY"]

        # Endpoint de Gemini 2.0 Flash
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

        # Datos a enviar
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": gemini_input
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
                "responseMimeType": "text/plain"
            }
        }

        # Encabezados
        headers = {
            "Content-Type": "application/json"
        }

        # Realizar la solicitud POST
        response = requests.post(
            f"{url}?key={api_key}",
            headers=headers,
            data=json.dumps(payload)
        )

        # Procesar la respuesta
        if response.status_code == 200:
            gemini_response = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            st.subheader("Análisis generado por Gemini:")
            st.write(gemini_response)
        else:
            st.error(f"Error al comunicarse con Gemini: {response.status_code} - {response.text}")

# Chatbot de consultas científicas
st.subheader("Chatbot de Consultas Bioquímicas")
user_question = st.text_input("Haz una pregunta sobre bioquímica o resultados de laboratorio:")

if user_question:
    # Obtener la API Key desde los secretos de Streamlit
    api_key = st.secrets["GEMINI_API_KEY"]

    # Endpoint de Gemini 2.0 Flash
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    # Datos a enviar
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": user_question
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
            "responseMimeType": "text/plain"
        }
    }

    # Encabezados
    headers = {
        "Content-Type": "application/json"
    }

    # Realizar la solicitud POST
    response = requests.post(
        f"{url}?key={api_key}",
        headers=headers,
        data=json.dumps(payload)
    )

    # Procesar la respuesta
    if response.status_code == 200:
        gemini_response = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        st.subheader("Respuesta de Gemini:")
        st.write(gemini_response)
    else:
        st.error(f"Error al comunicarse con Gemini: {response.status_code} - {response.text}")
