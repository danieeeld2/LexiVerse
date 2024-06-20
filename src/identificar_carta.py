import json
import cv2
import numpy as np
import pyttsx3
import threading

# Funcion para cargar un mapa en formato JSON
def cargar_mapa(filename):
    # Cargar el archivo JSON con el mapa 
    with open(filename, "r") as file:
        mapa = json.load(file)
    
    # Retornar el mapa 
    return mapa

# Funcion para sobreescribir un mapa
def guardar_mapa(mapa, filename):
    # Guardar el mapa en el archivo JSON
    with open(filename, "w") as file:
        json.dump(mapa, file, indent=4)


# Funcion para identificar una carta basada en los marcadores
def identificar_carta(marcadores_detectados, mapa_cartas, umbral_coincidencia=3):
    # Convertir los identificadores de los marcadores en una tupla ordenada
    ids_marcadores = tuple(sorted(marcadores_detectados))
    print(ids_marcadores)

    # Recorrer el mapa de cartas
    for marcadores, carta in mapa_cartas.items():
        # Convertir la cadena de marcadores en una tupla de enteros
        marcadores_enteros = tuple(map(int, marcadores.strip('()').split(',')))
        # Calcular la intersección entre los marcadores detectados y los marcadores del mapa
        interseccion = set(ids_marcadores) & set(marcadores_enteros)
        # Verificar si la intersección tiene al menos 3 elementos
        if len(interseccion) >= umbral_coincidencia:
            # Retornar la carta correspondiente
            return carta
        
    # Retornar None si no se ha identificado ninguna carta
    return None

def detectarAruco(detector, frame, mapa_cartas, mapa_palabras, idioma):
    # Detectar marcadores ArUco en el frame
    corners, ids, _ = detector.detectMarkers(frame)
    # Dibujar los marcadores detectados en el frame
    frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    if ids is not None:
        list_ids = [id[0] for id in ids]
        # Identificar la carta correspondiente a los marcadores detectados
        carta = identificar_carta(list_ids, mapa_cartas)
        texto = mapa_palabras[carta][idioma] if carta is not None else "Carta no identificada"

        if carta is not None:
            # Calcular el centro de la carta utilizando los marcadores
            num_markers = len(corners)
            if num_markers >= 3:  # Asegurarse de que hay al menos 3 marcadores
                # Calcular el centro basado en los marcadores visibles
                center_x = int(np.mean([corner[0][:, 0].mean() for corner in corners]))
                center_y = int(np.mean([corner[0][:, 1].mean() for corner in corners]))

                # Obtener las dimensiones del texto
                (text_width, text_height), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                text_x = center_x - text_width // 2
                text_y = center_y + text_height // 2

                # Dibujar el rectángulo de fondo para el texto
                cv2.rectangle(frame, (text_x - 10, text_y - text_height - 10), 
                              (text_x + text_width + 10, text_y + 10), (255, 0, 0), -1)

                # Poner el texto centrado en la carta
                cv2.putText(frame, texto, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            return texto
    return None            

# Función principal
def test():
    # Cargar el mapa de cartas
    mapa_cartas = cargar_mapa("./data/map.json")
    
    # Crear un diccionario con los marcadores detectados
    marcadores_detectados = {1, 21, 23, 22}
    
    # Identificar la carta correspondiente a los marcadores detectados
    carta = identificar_carta(marcadores_detectados, mapa_cartas)
    
    # Imprimir la carta identificada
    print(f"Carta identificada: {carta}")

# Verificar si este archivo se está ejecutando como script
if __name__ == "__main__":
    test()