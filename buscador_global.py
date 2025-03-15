import time
import tkinter as tk
import pandas as pd
from tkinter import messagebox
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
import webbrowser


# Configuración de Selenium para abrir el navegador
def iniciar_navegador():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def obtener_resultados_google_con_reintento(consulta, max_intentos=3):
    intentos = 0
    while intentos < max_intentos:
        try:
            resultados =
            for resultado in search(consulta, num_results=5):
                resultados.append(resultado)
            return resultados if resultados else "No se encontraron resultados."
        except Exception as e:
            intentos += 1
            time.sleep(2)
    return "No se encontraron resultados después de varios intentos."


# Función para buscar información en todo Internet
@function_tool
def buscar_en_internet(consulta: str):
    return obtener_resultados_google_con_reintento(consulta)


def obtener_precio_con_reintento(driver, xpath, max_intentos=3):
    intentos = 0
    while intentos < max_intentos:
        try:
            precio_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return precio_element.text
        except (NoSuchElementException, TimeoutException):
            intentos += 1
            time.sleep(2)  # Esperar antes de reintentar
    return "No disponible después de varios intentos."


# Función para buscar en sitios de reservas
@function_tool
def buscar_en_sitios_reservas(destino: str):
    plataformas = {
        "Booking": {"url": f"https://www.booking.com/searchresults.html?ss={destino}",
                     "xpath": "//div[@class='bui-price-display__value']/div[@class='bui-price-display__text']/span[@class='bui-price-display__value']"},
        "Airbnb": {"url": f"https://www.airbnb.com/s/{destino}/homes",
                   "xpath": "//div[@class='_1fwiw8gv']"},
        "Expedia": {"url": f"https://www.expedia.com/Hotel-Search?destination={destino}",
                    "xpath": "//span[@class='uitk-lockup-price']"},
        "Skyscanner": {"url": f"https://www.skyscanner.com/hotels/{destino}",
                       "xpath": "//div[@class='Price__Value']"},
        "Kayak": {"url": f"https://www.kayak.com/hotels/{destino}",
                  "xpath": "//div[@class='price-text']"},
        "Trivago": {"url": f"https://www.trivago.com/en-US/s/{destino}",
                     "xpath": "//span[@class='deal-price']"},
        "Despegar": {"url": f"https://www.despegar.com/hotels/{destino}",
                      "xpath": "//span[@class='fare-price']"}
    }

    precios =

    for plataforma, detalles in plataformas.items():
        driver = iniciar_navegador()
        try:
            driver.get(detalles["url"])
            precio = obtener_precio_con_reintento(driver, detalles["xpath"])
        except Exception as e:
            precio = f"Error al procesar {plataforma}: {e}"
        finally:
            driver.quit()  # Asegurar que el driver se cierre siempre

        precios.append({"Plataforma": plataforma, "Precio": precio, "URL": detalles["url"]})

    return precios


# Función para mostrar resultados en una ventana gráfica
def mostrar_resultados(resultados):
    ventana = tk.Tk()
    ventana.title("Resultados de Búsqueda")
    ventana.geometry("600x400")

    tk.Label(ventana, text="Resultados Encontrados", font=("Arial", 14)).pack(pady=10)

    for resultado in resultados:
        tk.Label(ventana, text=resultado, font=("Arial", 12)).pack()

    ventana.mainloop()


# Función para mostrar la comparación de precios en reservas
def mostrar_comparacion_precios(precios):
    ventana = tk.Tk()
    ventana.title("Comparación de Precios")
    ventana.geometry("600x400")  # Aumentar el tamaño

    tk.Label(ventana, text="Comparación de Precios", font=("Arial", 16, "bold")).pack(pady=10)  # Título más grande y en negrita

    df = pd.DataFrame(precios)
    
    for index, row in df.iterrows():
        label_text = f"{row['Plataforma']}: {row['Precio']} - "
        label_frame = tk.Frame(ventana)  # Usar un Frame para organizar los elementos en la fila
        label_frame.pack(fill=tk.X, padx=10, pady=5)  # Expandir horizontalmente y agregar padding

        label = tk.Label(label_frame, text=label_text, font=("Arial", 12), anchor=tk.W)  # Texto del label
        label.pack(side=tk.LEFT)

        url_label = tk.Label(label_frame, text="Ver en la web", font=("Arial", 10, "underline"), fg="blue", cursor="hand2")  # Label para el enlace
        url_label.pack(side=tk.LEFT, padx=5)
        url_label.bind("<Button-1>", lambda e, url=row['URL']: webbrowser.open_new_tab(url))  # Abrir la URL en el navegador

    seleccion = tk.StringVar(value="")

    def seleccionar_plataforma(plataforma):
        seleccion.set(plataforma)
        ventana.destroy()

    button_frame = tk.Frame(ventana)  # Frame para los botones
    button_frame.pack(pady=10)

    for row in df.itertuples():
        tk.Button(button_frame, text=f"Reservar en {row.Plataforma}", command=lambda r=row: seleccionar_plataforma(r.Plataforma)).pack(side=tk.LEFT, padx=5)  # Botones en el mismo Frame

    ventana.mainloop()

    return seleccion.get()


# Función para realizar reservas en la mejor opción
@function_tool
def realizar_reserva(destino: str):
    precios = buscar_en_sitios_reservas(destino)
    plataforma_seleccionada = mostrar_comparacion_precios(precios)

    if not plataforma_seleccionada:
        return "Reserva cancelada."

    url_reserva = next(item["URL"] for item in precios if item["Plataforma"] == plataforma_seleccionada)
    
    driver = iniciar_navegador()
    try:
        driver.get(url_reserva)
        time.sleep(3)

        mensaje = f"Reserva iniciada en {plataforma_seleccionada}. Por favor, completa los detalles manualmente."
        return mensaje
    except Exception as e:
        return f"Error al iniciar la reserva: {e}"
    finally:
        driver.quit()

# Crear el agente con funciones de búsqueda global
navegador_web_agente = Agent(
    name="Buscador Global de Internet",
    instructions="Eres un agente que busca información en todo Internet y encuentra las mejores opciones de vuelos, hoteles, restaurantes y servicios en diversas plataformas.",
    tools=[buscar_en_internet, buscar_en_sitios_reservas, realizar_reserva],
)

# Ejecutar prueba
print("=== PRUEBA DE BÚSQUEDA EN INTERNET ===")
resultados_web = buscar_en_internet("Mejores hoteles en Madrid")
mostrar_resultados(resultados_web)

print("\n=== PRUEBA DE COMPARACIÓN DE PRECIOS ===")
precios = buscar_en_sitios_reservas("Madrid")
for p in precios:
    print(f"{p['Plataforma']}: {p['Precio']} - {p['URL']}")

print("\n=== PRUEBA DE RESERVA ===")
resultado_reserva = Runner.run_sync(navegador_web_agente, "realizar_reserva", destino="Madrid")
print(resultado_reserva.final_output)