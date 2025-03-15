import time
import tkinter as tk
from tkinter import messagebox
from agents import Agent, Runner, function_tool
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Configuración de Selenium para abrir el navegador
def iniciar_navegador():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Quitar comentario si quieres modo sin interfaz
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
    time.sleep(3)  # Esperar a que cargue la página
    
    # Obtener los primeros resultados de búsqueda
    resultados = driver.find_elements(By.CSS_SELECTOR, "h3")[:5]  # Extraer títulos
    enlaces = driver.find_elements(By.CSS_SELECTOR, ".tF2Cxc a")[:5]  # Extraer enlaces

    info_resultados = []
    for titulo, enlace in zip(resultados, enlaces):
        info_resultados.append(f"{titulo.text}: {enlace.get_attribute('href')}")

    driver.quit()
    
    return "\n".join(info_resultados) if info_resultados else "No se encontraron resultados."


# Función para mostrar una ventana de confirmación visual
def confirmar_reserva_gui(url_reserva, destino, fecha_entrada, fecha_salida, personas):
    ventana = tk.Tk()
    ventana.title("Confirmación de Reserva")
    ventana.geometry("400x300")

    tk.Label(ventana, text="Detalles de la reserva:", font=("Arial", 14)).pack(pady=10)
    tk.Label(ventana, text=f"Sitio: {url_reserva}").pack()
    tk.Label(ventana, text=f"Destino: {destino}").pack()
    tk.Label(ventana, text=f"Fecha de entrada: {fecha_entrada}").pack()
    tk.Label(ventana, text=f"Fecha de salida: {fecha_salida}").pack()
    tk.Label(ventana, text=f"Personas: {personas}").pack()

    resultado = tk.StringVar(value="pendiente")

    def aceptar():
        resultado.set("aceptado")
        ventana.destroy()

    def cancelar():
        resultado.set("cancelado")
        ventana.destroy()

    tk.Button(ventana, text="Aceptar", command=aceptar, bg="green", fg="white").pack(pady=10)
    tk.Button(ventana, text="Cancelar", command=cancelar, bg="red", fg="white").pack(pady=10)

    ventana.mainloop()
    
    return resultado.get() == "aceptado"


# Función para realizar reservas automáticamente con confirmación visual
@function_tool
def realizar_reserva(url_reserva: str, destino: str, fecha_entrada: str, fecha_salida: str, personas: int):
    confirmacion = confirmar_reserva_gui(url_reserva, destino, fecha_entrada, fecha_salida, personas)
    if not confirmacion:
        return "Reserva cancelada por el usuario."

    driver = iniciar_navegador()
    driver.get(url_reserva)
    time.sleep(3)  # Esperar a que cargue la página

    mensaje = "No se pudo completar la reserva automáticamente."

    if "booking.com" in url_reserva:
        try:
            search_box = driver.find_element(By.NAME, "ss")  # Caja de búsqueda en Booking
            search_box.clear()
            search_box.send_keys(destino)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)

            # Seleccionar fecha de entrada y salida
            date_inputs = driver.find_elements(By.CSS_SELECTOR, 'td[data-date]')
            for date in date_inputs:
                if date.get_attribute("data-date") == fecha_entrada:
                    date.click()
                    time.sleep(1)
                if date.get_attribute("data-date") == fecha_salida:
                    date.click()
                    time.sleep(1)

            # Configurar número de personas
            guests_button = driver.find_element(By.ID, "xp__guests__toggle")
            guests_button.click()
            time.sleep(1)

            adult_count = driver.find_element(By.ID, "group_adults")
            adult_count.clear()
            adult_count.send_keys(str(personas))

            # Buscar habitaciones
            search_button = driver.find_element(By.CLASS_NAME, "sb-searchbox__button")
            search_button.click()

            mensaje = "Reserva en Booking casi completada. Revisa los detalles y confirma."

        except Exception as e:
            mensaje = f"Error en Booking: {e}"

    else:
        mensaje = "Este sitio aún no es compatible con la reserva automática."

    driver.quit()
    return mensaje


# Crear el agente con interfaz gráfica
navegador_web_agente = Agent(
    name="Navegador de Reservas con Confirmación Visual",
    instructions="Eres un agente que busca vuelos, hoteles, restaurantes, ropa y comida en Internet. También puedes hacer reservas con confirmación visual del usuario.",
    tools=[buscar_servicio, realizar_reserva],
)

# Ejecutar prueba
print("=== PRUEBA DE BÚSQUEDA ===")
resultado_busqueda = Runner.run_sync(navegador_web_agente, "Buscar hoteles en Madrid")
print(resultado_busqueda.final_output)

print("\n=== PRUEBA DE RESERVA ===")
resultado_reserva = Runner.run_sync(navegador_web_agente, "realizar_reserva", 
                                    url_reserva="https://www.booking.com", 
                                    destino="Madrid", 
                                    fecha_entrada="2024-04-15", 
                                    fecha_salida="2024-04-20", 
                                    personas=2)
print(resultado_reserva.final_output)
