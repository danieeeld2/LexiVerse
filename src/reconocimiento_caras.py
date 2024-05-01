import os
import cv2
import face_recognition

def leerCaras(directory):
    known_faces = []
    known_names = []
    for filename in os.listdir(directory):
        image = face_recognition.load_image_file(directory + filename)
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(os.path.splitext(filename)[0])
    return known_faces, known_names

def reconocerCaras(known_faces, known_names, image):
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        name = "Desconocido"
        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]
        print("Encontrado a", name)

def main():
    known_faces, known_names = leerCaras("caras/")
    # inicializar la cámara
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        reconocerCaras(known_faces, known_names, frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

