import random
from identificar_carta import identificar_carta

def seleccionar_carta(perfil):
    # Obtener las cartas y sus freciencias de acierto
    cartas = list(perfil["frecuencia"].keys())
    frecuencias = list(perfil["frecuencia"].values())

    # Invertir las frecuencias para dar mayor probabilidades a las cartas menos acertadas
    max_frecuencia = max(frecuencias) + 1
    probabilidades = [max_frecuencia - f for f in frecuencias]

    # Seleccionar una carta aleatoria basada en las probabilidades
    carta_seleccionada = random.choices(cartas, weights=probabilidades, k=1)[0]
    return carta_seleccionada

def mostrar_carta_y_detectar_carta(cv2, frame, texto, detector, mapa_cartas, mapa_palabras, idioma, puntuacion):
    # Detectar marcadores ArUco en el frame
    corners, ids, _ = detector.detectMarkers(frame)
    if ids is not None and len(ids) >= 3:
        list_ids = [id[0] for id in ids]
        # Identificar la carta correspondiente a los marcadores detectados
        carta = identificar_carta(list_ids, mapa_cartas)
        texto_carta = mapa_palabras[carta][idioma] if carta is not None else "Carta no identificada"
        if texto_carta == texto:
            return True
        else:
            return False

    (text_width, text_height), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_x = int((frame.shape[1] - text_width) / 2)
    text_y = frame.shape[0] - 30
    cv2.rectangle(frame, (text_x - 10, text_y - text_height - 10), (text_x + text_width + 10, text_y + 10), (255, 0, 0), -1)
    cv2.putText(frame, texto, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    pintar_puntuacion(cv2, frame, puntuacion)
    return None

def carta_acertada(cv2, frame, texto):
    (text_width, text_height), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_x = int((frame.shape[1] - text_width) / 2)
    text_y = frame.shape[0] - 30
    cv2.rectangle(frame, (text_x - 10, text_y - text_height - 10), (text_x + text_width + 10, text_y + 10), (0, 255, 0), -1)
    cv2.putText(frame, texto, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

def carta_no_acertada(cv2, frame, texto):
    (text_width, text_height), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_x = int((frame.shape[1] - text_width) / 2)
    text_y = frame.shape[0] - 30
    cv2.rectangle(frame, (text_x - 10, text_y - text_height - 10), (text_x + text_width + 10, text_y + 10), (0, 0, 255), -1)
    cv2.putText(frame, texto, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

def pintar_puntuacion(cv2, frame, puntuacion):
    # Definir el texto a mostrar
    texto = str(puntuacion)
    
    # Definir la fuente y parámetros del texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    escala = 1
    grosor = 2
    color_texto = (0, 0, 0)  # Negro

    # Obtener el tamaño del texto
    (ancho_texto, alto_texto), _ = cv2.getTextSize(texto, font, escala, grosor)
    
    # Definir la posición del texto (esquina superior derecha)
    margen = 10  # Margen desde el borde
    x = frame.shape[1] - ancho_texto - margen
    y = margen + alto_texto
    
    # Definir las coordenadas del rectángulo de fondo blanco
    rect_top_left = (x - margen, margen)
    rect_bottom_right = (x + ancho_texto + margen, y + margen)
    
    # Dibujar el rectángulo blanco
    cv2.rectangle(frame, rect_top_left, rect_bottom_right, (255, 255, 255), cv2.FILLED)
    
    # Dibujar el texto negro sobre el rectángulo blanco
    cv2.putText(frame, texto, (x, y), font, escala, color_texto, grosor)

