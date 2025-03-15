import time
from agents import Agent, Runner, function_tool
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Configuración de Selenium para abrir el navegador
def iniciar_navegador():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Ejecutar en segundo plano
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# Función para buscar servicios en Google
@function_tool
def buscar_servicio(tipo_servicio: str, ubicacion: str):
    driver = iniciar_navegador()
    url_busqueda = f"https://www.google.com/search?q={tipo_servicio}+en+{ubicacion}"
    
    driver.get(url_busqueda)
    time.sleep(2)  # Esperar a que cargue la página
    
    # Obtener los primeros resultados de búsqueda
    resultados = driver.find_elements(By.CSS_SELECTOR, "h3")[:5]  # Extraer títulos
    enlaces = driver.find_elements(By.CSS_SELECTOR, ".tF2Cxc a")[:5]  # Extraer enlaces

    info_resultados = []
    for titulo, enlace in zip(resultados, enlaces):
        info_resultados.append(f"{titulo.text}: {enlace.get_attribute('href')}")

    driver.quit()
    
    return "\n".join(info_resultados) if info_resultados else "No se encontraron resultados."


# Crear el agente de navegación web
navegador_web_agente = Agent(
    name="Navegador Web",
    instructions="Eres un agente que busca información de vuelos, hoteles, restaurantes, ropa y comida en Internet.",
    tools=[buscar_servicio],
)


# Ejecutar una prueba de búsqueda
resultado = Runner.run_sync(navegador_web_agente, "Buscar hoteles en Madrid")
print(resultado.final_output)
