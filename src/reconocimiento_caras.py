import os
import cv2
import face_recognition
import numpy as np
import json

def leerCaras(directory):
    known_faces = []
    known_names = []
    for filename in os.listdir(directory):
        if filename.endswith(".npy"):
            encode_file = os.path.join(directory, filename)
            encoding = np.load(encode_file)
            known_faces.append(encoding)
            known_names.append(os.path.splitext(filename)[0])
    return known_faces, known_names


def crearPerfil(nombre, idioma, archivo):
    with open(archivo, "r") as file:
        data = json.load(file)

    # Añadir el nuevo perfil al diccionario
    data[nombre] = {
        "idioma": idioma,
        "puntos" : 0,
        "frecuencia" : {
            "Carta1" : 0,
            "Carta2" : 0,
            "Carta3" : 0,
            "Carta4" : 0,
            "Carta5" : 0,
            "Carta6" : 0,
            "Carta7" : 0,
            "Carta8" : 0,
            "Carta9" : 0,
            "Carta10" : 0,
            "Carta11" : 0,
            "Carta12" : 0
        }
    }

    # Guardar el diccionario actualizado en el archivo
    with open(archivo, "w") as file:
        json.dump(data, file, indent=4)

def crearCodificacion(cola, known_faces, known_names):
    while True:
        if not cola.empty():
            nombre, frames, idioma, archivo = cola.get()
            encodings = []  # Lista para almacenar las codificaciones de todas las caras detectadas en todos los frames
    
            for frame in frames:
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                
                if len(face_encodings) == 0:
                    print("No se ha detectado ninguna cara en un frame.")
                    continue  # Continuar con el siguiente frame si no se detecta ninguna cara en este frame

                for encoding in face_encodings:
                    encodings.append(encoding)  # Agregar las codificaciones de las caras detectadas en este frame a la lista
            
            if len(encodings) == 0:
                print("No se ha detectado ninguna cara en ninguno de los frames.")
                return None
            
            # Calcular la codificación promedio
            avg_encoding = np.mean(encodings, axis=0)
            # Guardar la codificación promedio en un archivo numpy
            np.save(f"face_encodes/{nombre}.npy", avg_encoding)
            print("Cara guardada")
            known_faces.append(avg_encoding)
            known_names.append(nombre)
            crearPerfil(nombre, idioma, archivo)
    

def reconocerCaras(known_faces, known_names, image):
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    if len(face_encodings) == 0:
        print("No se ha detectado ninguna cara")
        return None
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]
            print("Encontrado a", name)
            return name   
        print("Desconocido")
        return "Desconocido"

def main():
    known_faces, known_names = leerCaras("caras/")
    # inicializar la cámara
    cap = cv2.VideoCapture(0)
    
    # Precargar el modelo de reconocimiento facial
    while True:
        ret, frame = cap.read()
        if ret:
            break
    reconocerCaras(known_faces, known_names, frame)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Reducir la resolución del cuadro a la mitad
        copia_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        reconocerCaras(known_faces, known_names, copia_frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()