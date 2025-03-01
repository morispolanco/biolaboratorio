import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from fpdf import FPDF
import os
import hashlib

# Configuración inicial de la página
st.set_page_config(page_title="BioInsights AI", layout="wide")

# Título de la aplicación
st.title("BioInsights AI 🧪")
st.markdown("Interpreta resultados bioquímicos y genera informes personalizados con IA.")

# Seguridad: Autenticación básica
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Simulación de usuarios autorizados
AUTHORIZED_USERS = {
    "admin": hash_password("password123"),
}

# Autenticación
def authenticate():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.sidebar:
            st.header("Iniciar Sesión")
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if username in AUTHORIZED_USERS and hash_password(password) == AUTHORIZED_USERS[username]:
                    st.session_state.logged_in = True
                    st.experimental_rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
        st.stop()

authenticate()

# Barra lateral para ofrecer el archivo de muestra
with st.sidebar:
    st.header("Descarga un archivo de muestra")
    st.markdown("Si no estás seguro del formato de los datos, puedes descargar un archivo de muestra:")
    
    # Contenido del archivo de muestra (CSV)
    sample_data = """Paciente,Glucosa,Colesterol,Hemoglobina,Ferritina,Fecha
Paciente1,95,200,14.5,80,2023-01-01
Paciente2,110,220,13.8,65,2023-02-01
Paciente3,100,190,15.2,70,2023-03-01
Paciente4,120,240,12.9,50,2023-04-01
Paciente5,90,180,14.0,90,2023-05-01"""
    
    # Convertir el contenido a un archivo descargable
    st.download_button(
        label="Descargar archivo de muestra (CSV)",
        data=sample_data,
        file_name="datos_bioquimicos_ejemplo.csv",
        mime="text/csv"
    )

# Cargar archivo CSV, Excel o JSON
uploaded_file = st.file_uploader("Carga un archivo CSV, Excel o JSON con los resultados del laboratorio:", type=["csv", "xlsx", "json"])

if uploaded_file:
    # Leer el archivo
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.json'):
        df = pd.read_json(uploaded_file)

    # Mostrar los datos cargados
    st.subheader("Datos cargados:")
    st.dataframe(df)

    # Filtrar y buscar resultados específicos
    st.subheader("Filtrar Resultados")
    filtro_paciente = st.selectbox("Selecciona un paciente:", ["Todos"] + list(df["Paciente"].unique()))
    if filtro_paciente != "Todos":
        df_filtrado = df[df["Paciente"] == filtro_paciente]
    else:
        df_filtrado = df

    st.dataframe(df_filtrado)

    # Análisis Automatizado de Resultados
    st.subheader("Análisis Automatizado de Resultados")
    rangos_normales = {
        "Glucosa": (70, 100),
        "Colesterol": (120, 200),
        "Hemoglobina": (12, 16),
        "Ferritina": (15, 150),
    }

    def analizar_resultados(row):
        resultados = {}
        for columna, rango in rangos_normales.items():
            valor = row[columna]
            if valor < rango[0]:
                resultados[columna] = "Bajo"
            elif valor > rango[1]:
                resultados[columna] = "Alto"
            else:
                resultados[columna] = "Normal"
        return pd.Series(resultados)

    df["Estado"] = df.apply(analizar_resultados, axis=1).apply(lambda x: ", ".join(x), axis=1)
    st.dataframe(df.style.applymap(lambda x: "background-color: red" if "Alto" in str(x) else ("background-color: yellow" if "Bajo" in str(x) else ""), subset=["Estado"]))

    # Gráficos Dinámicos
    st.subheader("Gráficos Dinámicos")
    selected_column = st.selectbox("Selecciona una columna para visualizar:", df.columns)
    fig = px.line(df, x="Fecha", y=selected_column, title=f"Tendencia de {selected_column} por Paciente", color="Paciente")
    st.plotly_chart(fig)

    # Generación de Informes Personalizados
    st.subheader("Generar Informe Personalizado")
    if st.button("Generar Informe PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        # Encabezado
        pdf.cell(200, 10, txt="Informe Bioquímico", ln=True, align="C")
        pdf.ln(10)

        # Datos del paciente
        for _, row in df.iterrows():
            pdf.cell(200, 10, txt=f"Paciente: {row['Paciente']}", ln=True)
            pdf.cell(200, 10, txt=f"Fecha: {row['Fecha']}", ln=True)
            pdf.cell(200, 10, txt=f"Estado: {row['Estado']}", ln=True)
            pdf.ln(10)

        # Guardar el archivo
        pdf_file = "informe_bioquimico.pdf"
        pdf.output(pdf_file)

        # Descargar el archivo
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="Descargar Informe PDF",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )
        os.remove(pdf_file)

    # Predicción de Resultados Futuros
    st.subheader("Predicción de Resultados Futuros")
    from sklearn.linear_model import LinearRegression

    predictor_column = st.selectbox("Selecciona una columna para predecir:", df.columns)
    if st.button("Predecir Resultados Futuros"):
        X = pd.to_datetime(df["Fecha"]).astype(int).values.reshape(-1, 1)
        y = df[predictor_column].values
        model = LinearRegression()
        model.fit(X, y)
        future_date = pd.to_datetime("2024-01-01").astype(int)
        prediction = model.predict([[future_date]])[0]
        st.write(f"Predicción para {predictor_column} en 2024-01-01: {prediction:.2f}")

    # Panel de Control para Gestión de Pacientes
    st.subheader("Panel de Control")
    st.metric("Total de Pruebas Realizadas", len(df))
    st.metric("Pacientes Atendidos", df["Paciente"].nunique())
    st.metric("Resultados Anormales", df["Estado"].str.contains("Alto|Bajo").sum())

# Chatbot de Consultas Científicas
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
