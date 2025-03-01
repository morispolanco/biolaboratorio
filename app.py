import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
import base64
from io import BytesIO
import sqlite3

# Configuración inicial
st.set_page_config(page_title="BioLab Manager - Premium", layout="wide")

# Datos de usuario (en producción, usa un sistema más seguro)
USERS = {
    "admin": "admin123",
    "laboratorio": "lab456"
}

# Autenticación
def authenticate():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("Iniciar Sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.success("Inicio de sesión exitoso.")
                st.experimental_rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
        st.stop()

# Base de datos
def init_db():
    conn = sqlite3.connect("biolab_manager.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            test_name TEXT,
            result REAL,
            status TEXT
        )
    """)
    conn.commit()
    return conn

def insert_data(conn, patient_id, test_name, result, status):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO results (patient_id, test_name, result, status)
        VALUES (?, ?, ?, ?)
    """, (patient_id, test_name, result, status))
    conn.commit()

def fetch_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM results")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    return pd.DataFrame(rows, columns=columns)

# Inicializar autenticación y base de datos
authenticate()
conn = init_db()

# Título de la aplicación
st.title("BioLab Manager - Versión Premium")
st.markdown("Gestión inteligente de datos y resultados de laboratorio.")

# Cargar datos
data = fetch_data(conn)

# Análisis automatizado
def analyze_data(data):
    st.subheader("Análisis Automatizado de Resultados")
    normal_ranges = {
        "Glucosa": (70, 100),
        "Colesterol": (120, 200),
        "Triglicéridos": (50, 150),
    }
    for column in data.columns:
        if column in normal_ranges:
            min_val, max_val = normal_ranges[column]
            data[f"{column} - Estado"] = np.where(
                (data[column] >= min_val) & (data[column] <= max_val), "Normal", "Anormal"
            )
    st.dataframe(data.style.applymap(lambda x: "background-color: red" if x == "Anormal" else ""))
    return data

analyzed_data = analyze_data(data)

# Guardar datos en la base de datos
if st.button("Guardar Resultados en la Base de Datos"):
    for _, row in analyzed_data.iterrows():
        insert_data(conn, row["ID Paciente"], row["Prueba"], row["Resultado"], row["Estado"])
    st.success("Datos guardados en la base de datos.")
