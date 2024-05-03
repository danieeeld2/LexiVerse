import os
import cv2
import face_recognition
import numpy as np

def leerCaras(directory):
    known_faces = []
    known_names = []
    for filename in os.listdir(directory):
        image_path = os.path.join(directory, filename)
        encode_file = os.path.join("face_encodes", os.path.splitext(filename)[0] + ".npy")
        if os.path.exists(encode_file):
            encoding = np.load(encode_file)
        else:
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            np.save(encode_file, encoding)
        known_faces.append(encoding)
        known_names.append(os.path.splitext(filename)[0])
    return known_faces, known_names

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