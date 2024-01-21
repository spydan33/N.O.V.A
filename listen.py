import speech_recognition as sr #pip install speechRecognition
class voice:
    def active(activate_word,keepListening,useOffline):
        rec = sr.Recognizer()
        activation = False
        voice_string = ''
        with sr.Microphone() as source:
            rec.adjust_for_ambient_noise(source, duration=0.2)
            audio = rec.listen(source)
            if (useOffline == True):
                try:
                    voice_string = rec.recognize_sphinx(audio)
                    print('\nstring heard:' + voice_string)
                except sr.UnknownValueError:
                    pass
                print('\n string heard:' + voice_string)
            else:
                try:
                    voice_string = rec.recognize_google(audio)
                    print('\n string heard:' + voice_string)
                except sr.UnknownValueError:
                    pass
            try:
                check_variable = voice_string
            except UnboundLocalError:
                voice_string = ''
            if(activate_word in voice_string):
                    print('\n activate word heard')
                    activation = True
            elif(keepListening == True):
                try:
                    voice.active(activate_word,keepListening,useOffline)
                except sr.UnknownValueError:
                    voice.active(activate_word, keepListening, useOffline)
            class return_object():
                def __init__(self):
                    self.activation = activation
                    self.voice_string = voice_string
            ret = return_object()
            return ret
    def listen(useOffline):
        rec = sr.Recognizer()
        with sr.Microphone() as source:
            print('\n listening')
            audio = rec.listen(source)
            if (useOffline == True):
                try:
                    voice_string = rec.recognize_sphinx(audio)
                    print('\n string heard:' + voice_string)
                except sr.UnknownValueError:
                    voice_string = False
                print('\n string heard:' + voice_string)
            else:
                try:
                    voice_string = rec.recognize_google(audio)
                    print('\n string heard:' + voice_string)
                except sr.UnknownValueError:
                    voice_string = False
            return voice_string


