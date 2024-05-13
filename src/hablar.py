import pyttsx3

def hablar(cola, engine, evento):
    while True:
        texto = cola.get()
        if texto == "Salir":
            break
        if texto is not None:
            evento.set()
        engine.say(texto)
        engine.runAndWait()
        evento.clear()


if __name__ == "__main__":
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(voice)