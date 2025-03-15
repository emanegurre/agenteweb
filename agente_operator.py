import time
import os
from agents import Agent, Runner, function_tool
from googlesearch import search
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


# Configuración de Selenium para Navegación Visual
def iniciar_navegador():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def obtener_resultados_google_con_reintento(consulta, max_intentos=3):
    intentos = 0
    while intentos < max_intentos:
        try:
            resultados = [r for r in search(consulta, num_results=5)]
            return resultados if resultados else "No se encontraron resultados."
        except Exception as e:
            intentos += 1
            time.sleep(2)
    return "No se encontraron resultados después de varios intentos."


# 🔎 **1. Búsqueda en Internet con Google**
@function_tool
def buscar_en_internet(consulta: str):
    return obtener_resultados_google_con_reintento(consulta)


# 🌍 **2. Búsqueda en Sitios de Reservas**
@function_tool
def buscar_en_sitios_reservas(destino: str):
    plataformas = {
        "Booking": f"https://www.booking.com/searchresults.html?ss={destino}",
        "Airbnb": f"https://www.airbnb.com/s/{destino}/homes",
        "Expedia": f"https://www.expedia.com/Hotel-Search?destination={destino}"
    }
    return plataformas


# 👁️ **3. Navegación Visual en la Web con Preguntas**
@function_tool
def navegar_visualmente(url: str):
    driver = iniciar_navegador()
    try:
        driver.get(url)
        time.sleep(2)
        return f"Se abrió el navegador en {url}. ¿Qué acción quieres realizar?"
    except Exception as e:
        return f"No se pudo abrir el navegador en {url}: {e}"
    finally:
        driver.quit()


# ✅ **4. Confirmación de Reserva con Preguntas**
@function_tool
def realizar_reserva(url_reserva: str):
    return f"¿Quieres hacer la reserva en {url_reserva}? Responde con 'sí' o 'no'."


# 🎯 **5. Agente Inteligente con OpenAI Agents SDK**
agente_operator = Agent(
    name="Operator Personalizado",
    instructions="""
    Eres un asistente avanzado que busca información en Internet, navega visualmente en sitios web y ayuda a realizar reservas con confirmación del usuario.
    - Si el usuario quiere buscar información, usa la función de búsqueda en Internet.
    - Si el usuario busca hoteles, vuelos u otro servicio, usa la función de búsqueda en sitios de reservas.
    - Si el usuario quiere ver una página, abre la navegación visual.
    - Antes de hacer una reserva, siempre confirma con el usuario.
    - Si el usuario tiene dudas, intenta responderlas antes de continuar.
    """,
    tools=[buscar_en_internet, buscar_en_sitios_reservas, navegar_visualmente, realizar_reserva],
)


# 🚀 **Ejecutar el Agente con OpenAI SDK**
def iniciar_operator():
    while True:
        consulta = input("\n📢 ¿Qué necesitas hacer? (o escribe 'salir' para terminar): ").strip().lower()
        if consulta == "salir":
            break

        resultado = Runner.run_sync(agente_operator, consulta)
        print("\n🤖 Operator: ", resultado.final_output)

        if "¿Quieres hacer la reserva?" in resultado.final_output:
            confirmacion = input("\n✍ Responde 'sí' o 'no': ").strip().lower()
            if confirmacion == "sí":
                print("\n🛒 Iniciando reserva en el navegador...")
                Runner.run_sync(agente_operator, f"navegar_visualmente {resultado.final_output.split()[-1]}")
            else:
                print("\n❌ Reserva cancelada.")


# 🔥 **Ejecutar el Agente**
if __name__ == "__main__":
    iniciar_operator()