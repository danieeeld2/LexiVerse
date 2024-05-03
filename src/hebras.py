import speech_recognition as sr
import sounddevice
import pyaudio
import pyttsx3

def preguntar_modo(modo_juego, r, engine):
    # Preguntar al usuario el modo de juego
    engine.say("¿Qué modo de juego desea jugar?")
    engine.runAndWait()
    while modo_juego is None:
        with sr.Microphone() as source:
            print("Di el modo de juego")
            audio = r.listen(source, phrase_time_limit=3)
        try:
            transcript = r.recognize_google(audio, language='es-ES')
            if transcript == "Aprender" or transcript == "modo 2":
                modo_juego = transcript
            else:
                engine.say("No te he entendido, por favor repite")
                engine.runAndWait()
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))