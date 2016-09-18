import speech_recognition as sr
from test import audiotests

r = sr.Recognizer()
m = sr.Microphone()

def findSpeed(words):
    if('one' in words):
        return(.2)
    elif('three' in words):
        return(1)
    else:
        return(.5)

def control(words,ip):
    name = words[0]
    while('end' not in words):
        lspeed = 0
        aspeed = 0
        if('foreward' in words):
            lspeed = findSpeed(words)
        elif('backward' in words):
            lspeed = findSpeed(words) * -1
        elif('right' in words):
            aspeed = findSpeed(words) * 2
        elif('left' in words):
            aspeed = findSpeed(words) * -2
        print('linear: ' + str(lspeed) + " rotational: " + str(aspeed))
        print("Listening...")
        with m as source: audio = r.listen(source)
        try:
            print"Recognizing..."
            command = r.recognize_sphinx(audio)
            print("You said: {0}".format(command))
            words = command.split(' ')
        except sr.UnknownValueError:
            print ("Didn't catch that")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
        
# obtain audio from the microphone
botIp = {} #used as a dictionary for botIps
botIp['lou']  = '10.0.0.1'
botIp['raphael'] = '10.0.1.1'

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
            print("You said: {0}".format(command))
            words = command.split(' ')
            if(words[0] == 'lou' or words[0] == 'raphael'):
                control(words,botIp[words[0]])
            
        except sr.UnknownValueError:
            print ("Didn't catch that")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
            
except KeyboardInterrupt:
    pass            
