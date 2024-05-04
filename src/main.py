import cv2
import numpy as np
import threading
import json
import face_recognition
import speech_recognition as sr
import sounddevice
import pyaudio
import pyttsx3
from reconocimiento_caras import leerCaras, reconocerCaras
from identificar_carta import  cargar_mapa, detectarAruco
import time
import queue
from hablar import hablar
from reconocimiento_voz import  escuchar

def main():
    # Inicializar las variables globales
    iniciado = False    # Variable que determina si se ha inciado sesión o no
    known_faces, known_names = leerCaras("caras/")    # Cargar las caras conocidas
    r = sr.Recognizer()    # Inicializar el reconocedor de voz
    engine = pyttsx3.init()    # Inicializar el motor de texto a voz
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)   # Crear un diccionario de marcadores ArUco
    detector = cv2.aruco.ArucoDetector(aruco_dict)    # Crear un detector de marcadores ArUco
    mapa_cartas = cargar_mapa("./data/map.json")    # Cargar el mapa de cartas
    mapa_palabras = cargar_mapa("./data/cartas.json")    # Cargar el mapa de palabras
    cap = cv2.VideoCapture(0)    # Inicializar la cámara
    modo_juego = None   # Variable que determina el modo de juego
    recien_iniciado = True    # Variable que determina si se ha iniciado recientemente un modo
    cola_hablar = queue.Queue()    # Crear una cola para almacenar los textos a leer
    cola_datos1 = queue.Queue()    # Crear una cola para almacenar los datos introducidos por voz
    cola_datos2 = queue.Queue()    # Crear una cola auxiliar para el demonio de escucha

    # Verificar si la cámara está disponible
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara")
        return
    
    # Configurar motor de texto a voz
    engine.setProperty('voice', "spanish")
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 1)

    # Configurar nivel de ruidez del micrófono
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=3)
    
    # Crear un hilo para procesar los texto a voz
    hilo_voz = threading.Thread(target=hablar, daemon=True, args=(cola_hablar, engine))
    hilo_voz.start()

    # Crear un hilo para procesar los datos introducidos por voz
    hilo_datos = threading.Thread(target=escuchar, daemon=True, args=(cola_datos1, cola_datos2))
    hilo_datos.start()

    # Bucle para capturar video
    while True:
        # Leer un frame del video
        ret, frame = cap.read()

        # Verificar si se ha leído un frame
        if not ret:
            print("Error: No se puede leer el frame")
            break

        # Flujo principal del programa
        if not iniciado:
            # Inicializar la sesión
            copia_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            nombre = reconocerCaras(known_faces, known_names, copia_frame)
            if nombre is not None:
                if nombre != "Desconocido" :
                    iniciado = True

                    # Cargar sesion si se ha reconocido la cara (Pendiente)
                    cola_hablar.put("Bienvenido, " + nombre)
                else:
                    # Crear perfil de usuario (Pendiente)
                    cola_hablar.put("No se ha reconocido tu cara, ¿Cómo te llamas?")
                    # Preguntar al usuario su nombre mediante ventana emergente(Pendiente)

        else:
            if modo_juego is None:
                # Preguntar al usuario el modo de juego
                cola_hablar.put("¿Qué modo de juego deseas jugar?")
                cola_datos2.put("Procesar") # Indica al demonio de escucha que debe escuchar en segundo plano
                while modo_juego is None:
                    # Ver la respuesta del usuario
                    if not cola_datos1.empty():
                        modo_juego = cola_datos1.get()
                        if "aprender" in modo_juego or "jugar" in modo_juego:
                            cola_datos2.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar
                        else:
                            modo_juego = None

                    # Seguir mostrando frames en el video
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    ret, frame = cap.read()
            else:
                # Aquí habria que iniciar el modo de juego (Pendiente)
                if "aprender" in modo_juego:
                    if recien_iniciado:
                        cola_hablar.put("Modo de juego: " + modo_juego)
                        recien_iniciado = False
                        cola_datos2.put("Procesar") # Indica al demonio de escucha que debe escuchar en segundo plano
                    detectarAruco(detector, frame, mapa_cartas, mapa_palabras)
                    if not cola_datos1.empty():
                        texto = cola_datos1.get()
                        if "salir" in texto:
                            modo_juego = None
                            recien_iniciado = True
                            cola_datos2.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar


        # Mostrar el frame en una ventana
        cv2.imshow('frame', frame)

        # Esperar a que se presione la tecla 'q' para salir del bucle
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar la cámara y cerrar las ventanas
    cap.release()
    cv2.destroyAllWindows()

# Verificar si este archivo se está ejecutando como script
if __name__ == "__main__":
    main()
