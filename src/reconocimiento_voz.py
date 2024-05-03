import speech_recognition as sr
import sounddevice
import pyaudio

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source, phrase_time_limit=5)

try:
    print("Google Speech Recognition thinks you said " + r.recognize_google(audio, language='es-ES'))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))