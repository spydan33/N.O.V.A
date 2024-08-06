import time
import os
import pygame
from elevenlabs import set_api_key
import requests
import pyttsx3
from gtts import gTTS
import subprocess
from subprocess import CREATE_NO_WINDOW
import os
# Sleep for 5 seconds
class speak():
    def __init__(self,nova,TTS_model = '_google'):
        self.nova = nova
        self.elevenlabs_api_key = os.getenv("ELEVEN_LABS_API_KEY")
        self.OAI_api_key = nova.OAI.api_key
        self.TTS_model = TTS_model
        if(TTS_model == '_pytts'):
            self.engine = pyttsx3.init()
            self.engine.setProperty('voice',  "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0")
        self.processing = False
    def say_coqui(self,text):
        self.tts.tts_to_file(text=text, file_path="output.wav")

        self.speak("output.wav")
        if os.path.exists('output.wav'):
            os.remove('output.wav')
        return True
    
    def say_elleven(self,text):
        import requests

        CHUNK_SIZE = 1024
        url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"

        headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": self.elevenlabs_api_key
        }

        data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
        }

        response = requests.post(url, json=data, headers=headers)
        with open('output.mp3', 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        self.speak('output.mp3')
        return True

    def say_pytts(self,text):
        
        self.engine.say(text)
        
        self.engine.startLoop(False)
        return True
    
    def say_google(self,text):
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save("output.mp3")
        self.speak("output.mp3")
        return True


    def say_OAI(self,text):
        if(self.nova.OAI.say_OAI(text)):
            self.speak("output.mp3")
        else:
            self.nova.talk = False
        return True
     
    def speak(self,file_path):
        count = 0
        while not os.path.exists('output.mp3'):
            if os.path.exists('output.mp3') or count == 20:
                break
            else:
                time.sleep(1)
                count = count + 1

        # Initialize pygame
        pygame.init()

        # Load the audio file
        pygame.mixer.music.load(file_path)


        # Play the audio
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Adjust the tick value as needed
        # Quit pygame
        pygame.quit()
        self.processing = False
        return True

    def say(self,text):
        self.processing = True
        getattr(self, "say"+self.TTS_model)(text)
