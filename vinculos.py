import streamlit as st
import pandas as pd
import io
#from supabase import create_client
from supabase import Client, create_client

# Configuración de la página
st.set_page_config(page_title="Búsqueda de Vínculos", page_icon="🔍", layout="centered")

# Estilos mejorados
st.markdown(
    """
    <style>
        /* Ajustes generales */
        body {
            background-color: #f4f6f9;
        }

        /* Título */
        .title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
        }

        /* Contenedor de búsqueda */
        .search-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            margin: auto;
            max-width: 600px;
            padding: 10px;
        }

        /* Input de búsqueda */
        div[data-testid="stTextInput"] {
            width: 100%;
        }

        div[data-testid="stTextInput"] input {
            width: 100%;
            border: 2px solid #ccc;
            outline: none;
            font-size: 18px;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
            background: #f0f0f0 !important;  /* GRIS CLARO */
            color: #333 !important;
            box-shadow: none !important;
        }

        /* Evitar que se vuelva azul al escribir */
        div[data-testid="stTextInput"] input:focus {
            background: #f0f0f0 !important;
            border: 2px solid #4CAF50 !important;  /* Verde */
        }

        /* Botón de búsqueda */
        div[data-testid="stButton"] button {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            padding: 5px;
        }
        
        div[data-testid="stButton"] button:hover {
            color: #2e7d32;
        }

        /* Tabla estilizada con color verde */
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 16px;
            text-align: left;
            margin-top: 10px;
        }

        .styled-table th, .styled-table td {
            padding: 10px;
            border: 1px solid #ddd;
        }

        .styled-table th {
            background-color: #4CAF50;  /* VERDE */
            color: white;
            text-align: center;
        }

        .styled-table tr:nth-child(even) {
            background-color: #e8f5e9;  /* Verde claro */
        }

        /* Nombre resaltado */
        .nombre-box {
            font-size: 20px;
            font-weight: bold;
            color: #2e7d32;
            margin-top: 10px;
            text-align: center;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

# Conectar con Supabase
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "rcivil"

# Función para descargar archivos desde Supabase
def download_file_from_supabase(bucket, file_name):
    try:
        response = supabase.storage.from_(bucket).download(file_name)
        if response:
            return io.BytesIO(response)
        else:
            st.error(f"No se pudo descargar el archivo {file_name}")
            return None
    except Exception as e:
        st.error(f"Error al descargar {file_name}: {str(e)}")
        return None

# Función para cargar datos desde Supabase
def load_data_from_supabase():
    file = download_file_from_supabase(BUCKET_NAME, "vinculos.xlsx")
    if file:
        return pd.read_excel(file)
    return None

# Cargar datos
df_vinculos = load_data_from_supabase()

# Interfaz de usuario
if df_vinculos is not None:
    st.markdown('<p class="title"> Buscador de Vínculos Familiares</p><br>', unsafe_allow_html=True)

    # Contenedor de búsqueda
    col1, col2 = st.columns([10, 1])  # Hacer más ancho el input
    with col1:
        nro_documento = st.text_input("", key="dni", max_chars=8, label_visibility="collapsed", placeholder="Ingrese el DNI...")

    with col2:
        buscar = st.button("🔍", key="search_button")  # Solo muestra la lupa

    # Validar entrada
    nro_documento = nro_documento.replace(".", "").strip()

    # Mostrar el nombre si el DNI es válido
    if nro_documento.isdigit() and nro_documento:
        resultado_nombre = df_vinculos[df_vinculos["NRO_DOCUMENTO"].astype(str) == nro_documento]["APELLIDO_NOMBRE"]
        if not resultado_nombre.empty:
            st.markdown(f'<p class="nombre-box">{resultado_nombre.values[0]}</p>', unsafe_allow_html=True)

    # Buscar vínculos si se presiona el botón
    if buscar:
        if not nro_documento.isdigit():
            st.warning("⚠️ Ingrese solo números sin puntos ni espacios.")
        else:
            try:
                resultados = df_vinculos[df_vinculos["NRO_DOCUMENTO"].astype(str) == nro_documento][
                    ["APELLIDO_NOMBRE_VINCULO", "VINCULO", "NRO_DOC_VINCULO"]
                ]

                if not resultados.empty:
                    resultados["NRO_DOC_VINCULO"] = resultados["NRO_DOC_VINCULO"].astype("Int64")  
                    
                    st.markdown(f'<p class="result-box">Se encontraron {len(resultados)} resultados:</p>', unsafe_allow_html=True)
                    
                    st.markdown(resultados.to_html(index=False, classes="styled-table"), unsafe_allow_html=True)
                else:
                    st.warning("⚠️ No se encontraron resultados para el DNI ingresado.")
            except Exception as e:
                st.error(f"Error al realizar la búsqueda: {str(e)}")
