from listen import voice
from open_ai_handler import open_ai
from speak import speak
from process_string import process_string
from face import face
from force_responce import force_responce
from users import users
from events import events
from calender_nova import calendar
from attention import attention
from email_handler import email_handler
import json
import traceback
import threading
import time
import sys        
import sqlite3
from datetime import datetime
import random
import os

class nova:
    def __init__(self):
        self.running = True

        cn = sqlite3.connect('nova.db')
        c = cn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            users TEXT,
            date DATE NOT NULL
        );
        ''')
        cn.commit()
        
        self.root_path = os.path.dirname(os.path.abspath(__file__))
        self.tick_time = 0.2
        self.events = events()
        self.OAI = open_ai(self,False)
        #self.speak = speak(self,'_OAI')
        self.speak = speak(self)
        self.users_api = users() 
        self.face = face(self.tick_time,self)
        self.calendar = calendar(self)
        self.capture_face = False
        self.talk = False
        self.offline = False
        self.use_text = True
        self.responding = False
        self.face_thread = False
        self.text_thread = False
        self.listening_for_name = False
        self.name = "Nova"
        self.non_activation_strings = []
        self.smooth_functions = False
        self.running_do_once = False
        self.last_code = []
        self.button_listen_noise = True
        self.use_calender = True
        self.email = email_handler()
        self.attention = attention(self)

        n_emails = 20
        emails = self.email.get(n_emails)
        counter = 0
        for email_obj in emails:
            with open(f'json_data/fuzzy_data/email/email{counter}.json', 'w') as file:
                json.dump(email_obj.dump(), file)
            counter = counter + 1

        self.events.add('offline')
        self.events.add('listening_for_name_start')
        self.events.add('listening_for_name_stop')
        self.events.add('running')
        self.events.add('talk')
        self.events.add('talk_stop')
        self.events.add('sleep')
        self.events.add('quit')
        self.events.add('wake')
        self.events.add('new_context')
        self.events.add('code_in_response')

        #event listeners
        self.events.on('face_looking_at_camera',self.__do_once,'listen')
        self.events.on('code_in_response',self.__get_code)

    def __get_code(self,code_input):
        self.last_code = code_input
    def __do_once(self,method):
        if(not self.running_do_once):
            self.running_do_once = True
            if(method == 'listen'):
                if(self.button_listen_noise):
                    self.speak.speak("sounds/listening_noise.mp3")
                else:
                    responces = ["sounds/yes_question.mp3","sounds/sir_question.mp3"]
                    self.speak.speak(responces[random.randint(0, 1)])

            getattr(self, method)()
            self.running_do_once = False

    def nova_unprompted(self,unprompted_string):
        self.responding = True
        print("------------------------------------------NOVA---------------------------------------\n")
        print(unprompted_string+"\n") 
        print("--------------------------------------------------------------------------------------\n")
        if(self.talk):
            self.speak.say(unprompted_string)
        self.responding = False
        return unprompted_string

    def prompted(self,prompted_name):
        prompt = force_responce.prompted(prompted_name)
        print(prompt)
        answer = self.OAI.prompted_responce(prompt)
        if(self.talk):
            self.speak.say(answer)
    def start(self):
        try:
            self.running = True
            
            self.attention.start()
            face_started = False
            text_started = False
            while self.running:
                reset = False
                if(self.capture_face):
                    self.detect_face()
                    face_started = True
                if(self.use_text):
                    self.start_text_input()
                    text_started = True
                if(self.listening_for_name):
                    self.listen_for_name()
                    text_started = True
                change_state = False

                while self.running: #State Machine
                    if(self.capture_face):
                        if(not face_started):
                            change_state = True
                        if(self.face.face_change):
                            self.OAI.context_change(self.users_api,self.face.face_count)
                            self.face.face_change = False
                        if(self.face.listen_now and not self.responding):
                            self.listen()
                    else:
                        if(face_started):
                            change_state = True

                    if(not self.use_text and text_started):
                        change_state = True

                    if(change_state):
                        self.face.detect_running = False
                        temp_face = self.capture_face
                        temp_text = self.use_text
                        self.face.stop_detect()
                        self.use_text = False
                        if(self.face_thread != False):
                            self.face_thread.join(timeout=5)
                        if(self.face_thread != False):
                            self.text_thread.join(timeout=5)
                        self.capture_face = temp_face
                        self.use_text = temp_text
                        face_started = False
                        text_started = False
                        break
                    time.sleep(self.tick_time)
                time.sleep(self.tick_time)

        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            traceback.print_exc()
            return False

    def listen(self):
        try:
            voice_string = voice.listen(self.offline)
            if(voice_string == False):
                return True
            if(not self.responding):
                self.send_text(voice_string)
            return True
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            traceback.print_exc()
            return False

    

    def send_text(self,voice_string):
        processed_string = ''
        def functionality(self,the_str,relisten = False):
            if(the_str):
                self.responding = True
                continue_listen = process_string.input_string(the_str,self)
                if(continue_listen == "quit"):
                    self.quit()
                if(continue_listen == False):
                    return True
                if(self.listening_for_name and len(self.non_activation_strings) > 0):
                    messages_append = [{"role": "system", "content": "*Nova heard this: "+" ".join(self.non_activation_strings)+" :but its clear it was not directed at her"}]
                    self.non_activation_strings = []
                else:
                    messages_append = False
                if(self.smooth_functions):
                    ret_1 = self.OAI.ask_functions(the_str,True,messages_append)
                else:
                    ret_1 = self.OAI.ask(the_str,True,messages_append)
                ret_processed = process_string.ret_string(ret_1,self)
                explain = ret_processed[0]
                processed_string = ret_processed[1]
                if(explain):
                    print("------------------------------------------NOVA---------------------------------------\n")
                    print(processed_string+"\n")
                    print("--------------------------------------------------------------------------------------\n")
                    if(self.talk):
                        self.speak.say(processed_string)
                if(relisten):
                    return True
                else:
                    return False
        functionality(self,voice_string)
        if(self.listening_for_name):
            while(functionality(self,voice.listen_quick(self.offline),True)):
                functionality(self,voice.listen_quick(self.offline),True)
        self.responding = False
        return processed_string

    def listen_for_name(self):
        def listening():
            self.listening_for_name = True
            while self.listening_for_name:
                ret = voice.active(self.name,False,self.offline)
                if(ret.activation == False and not self.responding):
                    if(ret.voice_string != ''):
                        if(len(self.non_activation_strings) < 3):
                            self.non_activation_strings.append(ret.voice_string)
                        else:
                            self.non_activation_strings.append(ret.voice_string)
                            self.non_activation_strings.pop(0)
                    continue
                if(not self.responding):
                    self.send_text(ret.voice_string)
                time.sleep(self.tick_time)
        self.name_thread = threading.Thread(target = listening)
        self.name_thread.start()
        return True

    def command_handler(self,command,reply,smooth_function):
        if(not smooth_function):
            if(command["class_name"] == "nova"):
                if(reply):
                    force_responce.predefined(command["preset_responce"])
                else:
                    print("done")
                getattr(self, command["method_name"])()
            elif(command["class_name"] == "calender"):
                getattr(self.calender, command["method_name"])(params)
                quit()
        else:
            print("___command handler____")
            print(command["action"],command["model_name"])
        return
    def sleep(self):
        self.set_talk_off()
        self.change_to_text()
    
    def change_to_text(self):
        self.capture_face = False
        self.face.stop_detect()
        self.use_text = True
        return

    def start_text_input(self):
        self.use_text = True
        self.text_thread = threading.Thread(target = self.text_input)
        self.text_thread.start()
        """ while self.use_text:
            pass
        self.text_thread.join(timeout = 0.5) """
        return True

    def text_input(self):
        while self.use_text:
            user_input = input("Please Type Somthing:")
            if(user_input == False):
                continue
            self.send_text(user_input)
            time.sleep(self.tick_time)
        return True

    def set_talk_off(self):
        self.talk = False
        return True

    def set_talk_on(self):
        self.talk = True
        return True

    def detect_face(self):
        try:
            self.capture_face = True 
            self.face = face(self.tick_time,self)
            self.face_thread = threading.Thread(target = self.face.start_detecting)
            self.face_thread.start()
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred in Nova Detect face: {e}")
            traceback.print_exc()
            return False
        #self.use_text = False
        return True

    def wake_up(self):
        self.capture_face = True
        self.talk = True
        return True

    def quit(self):
        self.running = False
        self.capture_face = False
        self.use_text = True
        if(self.face_thread != False):
            self.face_thread.join(timeout=5)
        if(self.face_thread != False):
            self.text_thread.join(timeout=5)
        print("quiting...")
        sys.exit()

    def save_chats(self):
        # Connect to the database
        
        cn = sqlite3.connect('nova.db')
        cursor = cn.cursor()

        # Get the current date
        now = datetime.now().date()

        # Iterate over the messages and save them to the database
        cursor.execute("DELETE FROM messages where date = ?", (now,))
        for message in self.OAI.messages:
            role = message['role']
            content = message['content']
            # Insert the message into the database
            query = "INSERT INTO messages (role, date, content, users) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (role, now, content, ''))

        # Commit the changes and close the connection
        cn.commit()
        cn.close()

    def start_gui():
        pass

    def identify_user(self):
        self.face.verify_face = True

    def upscale_intellegence(self):
       self.OAI.upscale_intellegence()
    
    def downscale_intelligence(self):
       self.OAI.downscale_intelligence()

    def smooth_function_on(self):
        self.smooth_function = True
    
    def smooth_function_off(self):
        self.smooth_function = False

        