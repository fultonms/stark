import speech_recognition as sr
from test import audiotests

# obtain audio from the microphone
r = sr.Recognizer()
m = sr.Microphone()

try:
    print("Quiet please!")
    with m as source: r.adjust_for_ambient_noise(source)
    print("Ambient levels detected.")
    while True:
        print("Listening...")
        with m as source: audio = r.listen(source)
        try:
            print"Recognizing..."
            command = r.recognize_sphinx(audio)
            print("You said: {0}".format(value))
        except sr.UnknownValueError:
            print ("Didn't catch that")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
            
except KeyboardInterrupt:
    pass            