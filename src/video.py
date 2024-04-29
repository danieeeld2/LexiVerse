import cv2
from identificar_carta import identificar_carta, cargar_mapa
import numpy as np
import pyttsx3
import threading

# Función para decir una palabra
def decir_palabra(texto):
    engine = pyttsx3.init()
    engine.say(texto)
    engine.runAndWait()

# Función para capturar video desde la cámara y detectar marcadores ArUco
def capturar_video_y_detectar_arucos():
    # Inicializar la captura de video
    cap = cv2.VideoCapture(0)

    # Verificar si la cámara está disponible
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara")
        return
    
    # Crear un diccionario con los parámetros de detección de marcadores ArUco
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)

    # Crear un objeto de detección de marcadores ArUco
    detector = cv2.aruco.ArucoDetector(aruco_dict)

    carta_anterior = None
    carta = None

    # Bucle para capturar video
    while True:
        # Leer un frame del video
        ret, frame = cap.read()

        # Verificar si se ha leído un frame
        if not ret:
            print("Error: No se puede leer el frame")
            break

        # Detectar marcadores ArUco en el frame
        corners, ids, _ = detector.detectMarkers(frame)

        # Dibujar los marcadores detectados en el frame
        frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        if ids is not None:
            mapa_cartas = cargar_mapa("./data/map.json") # Cargar el mapa de cartas
            list_ids = [id[0] for id in ids] # Convertir los ids a una lista
            carta_anterior = carta
            carta = identificar_carta(list_ids, mapa_cartas)
            mapa_palabras = cargar_mapa("./data/cartas.json") # Cargar el mapa de palabras
            texto = mapa_palabras[carta]["ingles"] if carta is not None else "Carta no identificada"

            if carta is not None:
                # Decir la palabra correspondiente a la carta
                if carta_anterior != carta:
                    threading.Thread(target=decir_palabra, args=(texto,)).start()

                # Calcular el ancho y la altura del texto
                (text_width, text_height), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)

                # Calcular la posición para centrar el texto en la parte inferior del frame
                text_x = int((frame.shape[1] - text_width) / 2)
                text_y = frame.shape[0] - 30  # Posición en la parte inferior

                # Dibujar un cuadro de fondo azul detrás del texto
                cv2.rectangle(frame, (text_x - 10, text_y - text_height - 10), (text_x + text_width + 10, text_y + 10), (255, 0, 0), -1)

                # Dibujar el texto en blanco sobre el cuadro de fondo azul
                cv2.putText(frame, texto, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Mostrar el frame en una ventana
        cv2.imshow("Video", frame)

        # Esperar 1 milisegundo y verificar si se ha presionado la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar la captura de video y cerrar todas las ventanas
    cap.release()
    cv2.destroyAllWindows()

# Función principal
def main():
    # Capturar video y detectar marcadores ArUco
    capturar_video_y_detectar_arucos()

# Verificar si este archivo se está ejecutando como script
if __name__ == "__main__":
    main()
