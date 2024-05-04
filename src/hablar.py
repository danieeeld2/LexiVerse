import pyttsx3

def hablar(cola, engine):
    while True:
        texto = cola.get()
        if texto == "Salir":
            break
        engine.say(texto)
        engine.runAndWait()


if __name__ == "__main__":
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(voice)