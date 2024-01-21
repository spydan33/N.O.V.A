import json
from speak import speak
from listen import voice
import traceback
class force_responce:
    def predefined(name):
        json_file_path = 'json_data/preset_responce.json'
        try:
            with open(json_file_path, 'r') as json_file:
                # Load the JSON data from the file
                data = json.load(json_file)
                forced = data[name]
                print(forced["text"])
                speech = speak()
                speech.speak(forced["sound"])
                if(forced["needs_responce"]):
                    ret = force_responce.handle_user_responce(forced["responce_type"])
                    return ret
                
                    
        except FileNotFoundError:
            print(f"File not found: {json_file_path}")
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred: {e}")
    def handle_user_responce(responce_type):
        affirmative = ["yes","yup","continue","please do","uhuh","yeah","do that"]
        voice_string = voice.listen(False)
        if(responce_type == "affirmative"):
            for affirm in affirmative:
                if(affirm in voice_string):
                    return True
                else:
                    return False

    def prompted(promp_name):
        json_file_path = 'json_data/responce_promps.json'
        try:
            with open(json_file_path, 'r') as json_file:
                # Load the JSON data from the file
                data = json.load(json_file)
                return data[promp_name]["prompt"]
                
                    
        except FileNotFoundError:
            print(f"File not found: {json_file_path}")
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred: {e}")

