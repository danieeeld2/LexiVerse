import cv2
import numpy as np
import threading
import json
import face_recognition
import speech_recognition as sr
import sounddevice
import pyaudio
import pyttsx3
from reconocimiento_caras import leerCaras, reconocerCaras, crearCodificacion
from identificar_carta import  cargar_mapa, detectarAruco, guardar_mapa
import time
import queue
from hablar import hablar
from reconocimiento_voz import  escuchar
from unidecode import unidecode

def main():
    # Inicializar las variables globales
    iniciado = False    # Variable que determina si se ha inciado sesión o no
    known_faces, known_names = leerCaras("face_encodes/")    # Cargar las caras conocidas
    r = sr.Recognizer()    # Inicializar el reconocedor de voz
    engine = pyttsx3.init()    # Inicializar el motor de texto a voz
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)   # Crear un diccionario de marcadores ArUco
    detector = cv2.aruco.ArucoDetector(aruco_dict)    # Crear un detector de marcadores ArUco
    mapa_cartas = cargar_mapa("./data/map.json")    # Cargar el mapa de cartas
    mapa_palabras = cargar_mapa("./data/cartas.json")    # Cargar el mapa de palabras
    cap = cv2.VideoCapture(0)    # Inicializar la cámara
    perfiles = cargar_mapa("./data/usuarios.json")    # Cargar los perfiles de usuario
    perfil_activo = None    # Variable que determina el perfil activo
    idioma = "español"    # Variable que determina el idioma activo
    modo_juego = None   # Variable que determina el modo de juego
    recien_iniciado = True    # Variable que determina si se ha iniciado recientemente un modo
    cola_hablar = queue.Queue()    # Crear una cola para almacenar los textos a leer
    cola_datos = queue.Queue()    # Crear una cola para almacenar los datos introducidos por voz
    cola_peticiones = queue.Queue()    # Crear una cola auxiliar para indicar peticiones al demonio de escucha
    cola_codificacion = queue.Queue()    # Crear una cola auxiliar para llamar a la función de codificación de caras

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
    hilo_datos = threading.Thread(target=escuchar, daemon=True, args=(cola_datos, cola_peticiones))
    hilo_datos.start()

    # Crear un hilo para procesar la codificación de caras
    hilo_codificacion = threading.Thread(target=crearCodificacion, daemon=True, args=(cola_codificacion, known_faces, known_names))
    hilo_codificacion.start()

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
            # Recargar JSON por si se crear un nuevo perfil
            perfiles = cargar_mapa("./data/usuarios.json")
            # Inicializar la sesión
            copia_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            nombre = reconocerCaras(known_faces, known_names, copia_frame)
            if nombre is not None:
                if nombre != "Desconocido" :
                    iniciado = True

                    # Cargar sesion si se ha reconocido la cara 
                    cola_hablar.put("Bienvenido, " + nombre)
                    perfil_activo = perfiles[nombre]
                    idioma = perfil_activo["idioma"]
                else:
                    # Crear perfil de usuario 
                    cola_hablar.put("No se ha reconocido tu cara, ¿Cómo te llamas?")
                    # Preguntar al usuario su nombre mediante voz
                    nombre = None
                    cola_peticiones.put("Procesar") # Indica al demonio de escucha que debe escuchar en segundo plano
                    while nombre is None:
                        if not cola_datos.empty():
                            nombre = cola_datos.get()
                            # Comrpobar que es un nombre válido (Empieza con mayúscula)
                            if nombre[0].isupper():
                                cola_peticiones.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar
                                cola_hablar.put("Se va a escanear tu cara, " + nombre + ". Por favor, mira al frente y no te muevas")
                                # Meter espera de 7 segundos donde sigue mostrando frames
                                start_time = time.time()
                                while time.time() - start_time < 7:
                                    cv2.imshow('frame', frame)
                                    if cv2.waitKey(1) & 0xFF == ord('q'):
                                        exit(0)
                                    ret, frame = cap.read()
                                # Tomar frames para crear la codificación de la cara durante 3 segundos
                                frames = []
                                start_time = time.time()
                                while time.time() - start_time < 3:
                                    cv2.imshow('frame', frame)
                                    if cv2.waitKey(1) & 0xFF == ord('q'):
                                        exit(0)
                                    ret, frame = cap.read()
                                    frames.append(frame)
                                # Guardar la codificación de la cara en un archivo numpy
                                cola_codificacion.put((nombre, frames, "español", "./data/usuarios.json")) # Se ejecuta en la hebra en segundo plano                                 
                            else:
                                nombre = None
                        
                        # Seguir mostrando frames en el video
                        cv2.imshow('frame', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            exit(0)
                        ret, frame = cap.read()

                    cola_hablar.put("Bienvenido, " + nombre + ". Tu perfil ha sido creado")
                    iniciado = True
                modo_juego = None
        else:
            if modo_juego is None:
                # Preguntar al usuario el modo de juego
                cola_hablar.put("¿Qué modo de juego deseas jugar?")
                cola_peticiones.put("Procesar") # Indica al demonio de escucha que debe escuchar en segundo plano
                while modo_juego is None:
                    # Ver la respuesta del usuario
                    if not cola_datos.empty():
                        modo_juego = cola_datos.get()
                        if "aprender" in modo_juego or "jugar" in modo_juego or "idioma" in modo_juego:
                            cola_peticiones.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar
                        elif "cerrar sesión" in modo_juego:
                            iniciado = False
                            nombre = None
                            cola_peticiones.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar
                            cola_hablar.put("Hasta luego")
                        else:
                            modo_juego = None

                    # Seguir mostrando frames en el video
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        exit(0)
                    ret, frame = cap.read()
            else:
                if modo_juego is not None:
                    if "aprender" in modo_juego:
                        if recien_iniciado:
                            cola_hablar.put("Modo de juego: " + modo_juego)
                            recien_iniciado = False
                            cola_peticiones.put("Procesar") # Indica al demonio de escucha que debe escuchar en segundo plano
                        # Procesar el modo de aprendizaje de cartas
                        detectarAruco(detector, frame, mapa_cartas, mapa_palabras, idioma)
                        # Procesar cambiar de modo o cerrar sesión
                        if not cola_datos.empty():
                            texto = cola_datos.get()
                            if "salir" in texto:
                                modo_juego = None
                                recien_iniciado = True
                                cola_peticiones.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar
                            elif "cerrar sesión" in texto:
                                iniciado = False
                                nombre = None
                                recien_iniciado = True
                                cola_hablar.put("Hasta luego")
                                cola_peticiones.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar

                if modo_juego is not None:
                    if "jugar" in modo_juego:
                        if recien_iniciado:
                            cola_hablar.put("Modo de juego: " + modo_juego)
                            recien_iniciado = False
                            cola_peticiones.put("Procesar") # Indica al demonio de escucha que debe escuchar en segundo plano
                        # Crear modo de juego (Pendiente)
                        # Procesar cambiar de modo o cerrar sesión
                        if not cola_datos.empty():
                            texto = cola_datos.get()
                            if "salir" in texto:
                                modo_juego = None
                                recien_iniciado = True
                                cola_peticiones.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar
                            elif "cerrar sesión" in texto:
                                iniciado = False
                                nombre = None
                                recien_iniciado = True
                                cola_hablar.put("Hasta luego")
                                cola_peticiones.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar

                if modo_juego is not None:
                    if "idioma" in modo_juego:
                        if recien_iniciado:
                            cola_hablar.put("Cambio de idioma activado. ¿Qué idioma deseas jugar?")
                            recien_iniciado = False
                            cola_peticiones.put("Procesar")
                        # Procesar el cambio de idioma
                        if not cola_datos.empty():
                            idioma = cola_datos.get()
                            if idioma == "español" or idioma == "inglés" or idioma == "francés":
                                cola_hablar.put("Idioma cambiado a " + idioma)
                                recien_iniciado = True
                                modo_juego = None
                                # Recargar JSON por si se crearon nuevos usuarios
                                perfiles = cargar_mapa("./data/usuarios.json")
                                idioma = unidecode(idioma)
                                perfiles[nombre]["idioma"] = idioma
                                guardar_mapa(perfiles, "./data/usuarios.json")
                                cola_peticiones.get() # Limpiar la cola de datos auxiliar para que el demonio deje de escuchar
                    

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
