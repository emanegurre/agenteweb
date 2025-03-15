import time
import tkinter as tk
import pandas as pd
from tkinter import messagebox
from agents import Agent, Runner, function_tool
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
            time
