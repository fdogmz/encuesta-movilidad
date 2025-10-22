import streamlit as st
from streamlit_folium import st_folium
import folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

import json
#from streamlit.runtime.secrets import secrets

# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Encuesta de movilidad", page_icon="🚌", layout="centered")

st.title("🚌 Registro de punto de partida")

st.markdown("""
Esta información complementa la **encuesta principal sobre movilidad universitaria**  
y nos ayudará a identificar los puntos de origen más comunes de nuestra comunidad universitaria.

Por favor sigue estos pasos:

1. **Ingresa tu matrícula** si eres estudiante.  
   Si eres **personal administrativo o docente**, escribe tu **nombre de usuario institucional**,  
   es decir, la parte anterior a `@ucaribe.edu.mx` en tu correo universitario.  
   *(Ejemplo: si tu correo es `mlopez@ucaribe.edu.mx`, tu usuario es `mlopez`.)*

2. **Selecciona en el mapa** el **cruce más cercano a tu casa** o punto de partida habitual hacia la universidad.

3. **Haz clic en el botón “Enviar ubicación”** para registrar tus datos en el sistema.
""")


# ==========================================
# ENTRADA DE DATOS
# ==========================================
matricula = st.text_input("Matrícula (o nombre de usuario si eres parte del personal docente o administrativo)", placeholder="Ejemplo: 250301234 (estudiante) o fgomez (personal docente o administrativo)")

# Mapa inicial (Cancún como referencia)
mapa = folium.Map(location=[21.1619, -86.8515], zoom_start=12)
mapa.add_child(folium.LatLngPopup())

# Mostrar mapa interactivo
map_data = st_folium(mapa, height=400, width=700)

coords = None
if map_data and map_data.get("last_clicked"):
    coords = map_data["last_clicked"]
    st.success(f"Ubicación seleccionada: {coords['lat']:.5f}, {coords['lng']:.5f}")

# ==========================================
# ENVÍO DE DATOS A GOOGLE SHEETS
# ==========================================
if st.button("📍 Enviar ubicación"):
    if not matricula:
        st.error("Por favor ingresa tu matrícula antes de enviar.")
    elif not coords:
        st.error("Por favor selecciona una ubicación en el mapa.")
    else:
        try:
            # --- Configuración de acceso a Google Sheets ---
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]

            #creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)

            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                dict(st.secrets["gcp_service_account"]),
                scope
            )

            client = gspread.authorize(creds)

            # --- Abrir hoja de cálculo (asegúrate de crearla antes) ---
            sheet = client.open("Encuesta Movilidad Coordenadas").sheet1

            # --- Registrar fila con fecha, matrícula y coordenadas ---
            sheet.append_row([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                matricula,
                coords["lat"],
                coords["lng"]
            ])

            st.success("✅ Tu ubicación ha sido registrada correctamente. ¡Gracias por participar!")
            st.balloons()
        except Exception as e:
            st.error(f"Ocurrió un error al guardar los datos: {e}")
