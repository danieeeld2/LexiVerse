import speech_recognition as sr
import sounddevice
import pyaudio
import time

def comporbar_transcripcion(transcripcion):
    clave = "modo"
    if transcripcion is not None:
        if clave in transcripcion or transcripcion[0].isupper():
            return True
        elif "español" in transcripcion or "inglés" in transcripcion or "francés" in transcripcion:
            return True
        elif "cerrar sesión" in transcripcion:
            return True
    
    return False

def escuchar(cola1, evento1, evento2):
    r = sr.Recognizer()
    while True:
        if evento1.is_set() and not evento2.is_set():
            with sr.Microphone() as source:
                audio = r.listen(source, phrase_time_limit=4)
            try:
                transcripcion = r.recognize_google(audio, language='es-ES')
            except sr.UnknownValueError:
                transcripcion = None
            except sr.RequestError:
                transcripcion = None
            if transcripcion is not None:
                print("Google Speech Recognition thinks you said " + transcripcion)
            if comporbar_transcripcion(transcripcion):
                cola1.put(transcripcion)
                time.sleep(2)


def test():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source, phrase_time_limit=2)

    try:
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio, language='es-ES'))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

if __name__ == "__main__":
    test()