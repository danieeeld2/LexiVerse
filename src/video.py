import cv2

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

    # Bucle para capturar video
    while True:
        # Leer un frame del video
        ret, frame = cap.read()

        # Verificar si se ha leído un frame
        if not ret:
            print("Error: No se puede leer el frame")
            break

        # Convertir el frame a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar marcadores ArUco en el frame
        corners, ids, _ = detector.detectMarkers(frame)

        # Dibujar los marcadores detectados en el frame
        frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)

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
