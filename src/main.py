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
from juego import seleccionar_carta, mostrar_carta_y_detectar_carta, carta_acertada, carta_no_acertada
import random

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
    evento_hablar = threading.Event()    # Crear un evento para activar la lectura de texto
    cola_hablar = queue.Queue()    # Crear una cola para almacenar los textos a leer
    cola_datos = queue.Queue()    # Crear una cola para almacenar los datos introducidos por voz
    evento_procesar = threading.Event()    # Crear un evento para activar la escucha del microfono
    cola_codificacion = queue.Queue()    # Crear una cola auxiliar para llamar a la función de codificación de caras
    racha_aciertos = 0    # Variable que determina la racha de aciertos del usuario
    carta_detectada = None    # Variable que determina si se ha detectado una carta

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
    hilo_voz = threading.Thread(target=hablar, daemon=True, args=(cola_hablar, engine, evento_hablar))
    hilo_voz.start()

    # Crear un hilo para procesar los datos introducidos por voz
    hilo_datos = threading.Thread(target=escuchar, daemon=True, args=(cola_datos, evento_procesar, evento_hablar))
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
                    evento_procesar.set() # Activar la escucha del microfono
                    while nombre is None:
                        if not cola_datos.empty():
                            nombre = cola_datos.get()
                            # Comrpobar que es un nombre válido (Empieza con mayúscula)
                            if nombre[0].isupper():
                                evento_procesar.clear() # Desactivar la escucha del microfono
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
                evento_procesar.set() # Indica al demonio de escucha que debe escuchar en segundo plano
                while modo_juego is None:
                    # Ver la respuesta del usuario
                    if not cola_datos.empty():
                        modo_juego = cola_datos.get()
                        if "aprender" in modo_juego or "jugar" in modo_juego or "idioma" in modo_juego:
                            evento_procesar.clear() # Desactivar la escucha del microfono
                        elif "cerrar sesión" in modo_juego:
                            iniciado = False
                            nombre = None
                            evento_procesar.clear() # Desactivar la escucha del microfono
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
                            evento_procesar.set() # Indica al demonio de escucha que debe escuchar en segundo plano
                        # Procesar el modo de aprendizaje de cartas
                        nueva_carta_detectada = detectarAruco(detector, frame, mapa_cartas, mapa_palabras, idioma)
                        # if nueva_carta_detectada != carta_detectada:
                        #     carta_detectada = nueva_carta_detectada
                        #     if nueva_carta_detectada is not None:
                        #         cola_hablar.put(nueva_carta_detectada)
                        # Procesar cambiar de modo o cerrar sesión
                        if not cola_datos.empty():
                            texto = cola_datos.get()
                            if "salir" in texto:
                                modo_juego = None
                                recien_iniciado = True
                                evento_procesar.clear() # Desactivar la escucha del microfono
                            elif "cerrar sesión" in texto:
                                iniciado = False
                                nombre = None
                                recien_iniciado = True
                                cola_hablar.put("Hasta luego")
                                evento_procesar.clear() # Desactivar la escucha del microfono

                if modo_juego is not None:
                    if "jugar" in modo_juego:
                        if recien_iniciado:
                            cola_hablar.put("Modo de juego: " + modo_juego)
                            recien_iniciado = False
                            evento_procesar.set() # Indica al demonio de escucha que debe escuchar en segundo plano
                            # Recargar JSON por si es un usuario recien creado
                            perfiles = cargar_mapa("./data/usuarios.json")
                            perfil_activo = perfiles[nombre]
                            
                        # Procesamiento del modo de juego
                        # Elegir carta al azar basado en las estadísticas de acierto del usuario
                        carta_seleccionada = seleccionar_carta(perfil_activo)
                        # cola_hablar.put("Busca la carta: " + mapa_palabras[carta_seleccionada][idioma])
                        adivinando = True
                        while adivinando:
                            # Mostrar la palabra en la pantalla
                            respuesta = mostrar_carta_y_detectar_carta(cv2, frame, mapa_palabras[carta_seleccionada][idioma], detector, mapa_cartas, mapa_palabras, idioma, perfil_activo["puntos"])
                            if respuesta is not None:
                                adivinando = False
                                if respuesta:
                                    cola_hablar.put("¡Correcto, has acertado!")
                                    # Procesar la racha de aciertos
                                    racha_aciertos += 1
                                    # Actualizar la frecuencia de aciertos de la carta seleccionada
                                    perfil_activo["frecuencia"][carta_seleccionada] += 1
                                    # Sumar puntos
                                    puntos = random.randint(1, 10)*racha_aciertos
                                    perfil_activo["puntos"] += puntos
                                    guardar_mapa(perfiles, "./data/usuarios.json") # Guardar los cambios en el archivo JSON
                                    # Mostrar acierto durante 4 segundos
                                    time_start = time.time()
                                    while time.time() - time_start < 4:
                                        carta_acertada(cv2, frame, mapa_palabras[carta_seleccionada][idioma])
                                        # Seguir mostrando frames en el video
                                        cv2.imshow('frame', frame)
                                        if cv2.waitKey(1) & 0xFF == ord('q'):
                                            exit(0)
                                        ret, frame = cap.read()
                                else:
                                    cola_hablar.put("Lo siento, has fallado")
                                    racha_aciertos = 0 # Reiniciar la racha de aciertos
                                    # Mostrar error durante 4 segundos
                                    time_start = time.time()
                                    while time.time() - time_start < 4:
                                        carta_no_acertada(cv2, frame, mapa_palabras[carta_seleccionada][idioma])
                                        # Seguir mostrando frames en el video
                                        cv2.imshow('frame', frame)
                                        if cv2.waitKey(1) & 0xFF == ord('q'):
                                            exit(0)
                                        ret, frame = cap.read()
                            # Seguir mostrando frames en el video
                            cv2.imshow('frame', frame)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                exit(0)
                            ret, frame = cap.read()
                            # Procesar cambiar de modo o cerrar sesión
                            if not cola_datos.empty():
                                texto = cola_datos.get()
                                if "salir" in texto:
                                    guardar_mapa(perfiles, "./data/usuarios.json") # Guardar los cambios en el archivo JSON
                                    modo_juego = None
                                    adivinando = False
                                    recien_iniciado = True
                                    evento_procesar.clear() # Desactivar la escucha del microfono
                                elif "cerrar sesión" in texto:
                                    guardar_mapa(perfiles, "./data/usuarios.json") # Guardar los cambios en el archivo JSON
                                    iniciado = False
                                    nombre = None
                                    adivinando = False
                                    recien_iniciado = True
                                    cola_hablar.put("Hasta luego")
                                    evento_procesar.clear() # Desactivar la escucha del microfono

                if modo_juego is not None:
                    if "idioma" in modo_juego:
                        if recien_iniciado:
                            cola_hablar.put("Cambio de idioma activado. ¿Qué idioma deseas jugar?")
                            recien_iniciado = False
                            evento_procesar.set() # Indica al demonio de escucha que debe escuchar en segundo plano
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
                                if idioma == "espanol":
                                    idioma = "español"
                                perfiles[nombre]["idioma"] = idioma
                                guardar_mapa(perfiles, "./data/usuarios.json")
                                evento_procesar.clear()
                    

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
