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
from hebras import preguntar_modo
import time

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
    modo_juego = "Prueba"   # Variable que determina el modo de juego

    # Verificar si la cámara está disponible
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara")
        return
    
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
                    engine.setProperty('voice', 'spanish')
                else:
                    # Crear perfil de usuario (Pendiente)
                    time.sleep(1)
        else:
            if modo_juego is None:
                # Preguntar al usuario el modo de juego (Pendiente)
                time.sleep(1)
            else:
                detectarAruco(detector, frame, mapa_cartas, mapa_palabras)

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
