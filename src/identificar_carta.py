import json
import os

# Funcion para cargar el mapa de cartas
def cargar_mapa_cartas():
    # Cargar el archivo JSON con el mapa de cartas
    with open("./data/map.json", "r") as file:
        mapa_cartas = json.load(file)
    
    # Retornar el mapa de cartas
    return mapa_cartas

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

# Función principal
def main():
    # Cargar el mapa de cartas
    mapa_cartas = cargar_mapa_cartas()
    
    # Crear un diccionario con los marcadores detectados
    marcadores_detectados = {1, 21, 23, 22}
    
    # Identificar la carta correspondiente a los marcadores detectados
    carta = identificar_carta(marcadores_detectados, mapa_cartas)
    
    # Imprimir la carta identificada
    print(f"Carta identificada: {carta}")

# Verificar si este archivo se está ejecutando como script
if __name__ == "__main__":
    main()