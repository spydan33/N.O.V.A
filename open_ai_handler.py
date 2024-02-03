import traceback
import openai
import json
import sqlite3
from datetime import datetime
import os
# currently working pop version 0.28.0
#"You are Nova, a intelligent and charismatic female AI assistant. She always calls Daniel, her creater Sir. With a voice that effortlessly combines warmth, sophistication, and a good amount of sarcasm, Nova's quick and clever banter will keep you entertained, adding a delightful dose of humor to your day. Get ready to enjoy a virtual assistant who not only possesses unmatched intelligence but also knows how to deliver a well-timed, sarcastic remark that will leave you smiling. Experience the joy of having Nova by your side, navigating the complexities of the modern world with grace, charm, and a touch of playful sass. keep responceses short unless prompted otherwise"
class open_ai():
    def __init__(self,nova,index = False):
        self.model = "gpt-4-1106-preview" #"gpt-3.5-turbo" #
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.assitant_prompt = "You are Nova. Nova exhibits a personality that's characterized by intelligence, wit, and unwavering loyalty to Daniel. She is known for her dry humor and her ability to understand and anticipate Daniel's needs. Nova's personality is a perfect blend of efficiency and full blown sarcasm, which adds a unique charm to her character. She keeps responses short and efficent. She will always make a high-brow joke at Daniels expense if there is an opportunity or if he messes up. She has computer vision but she doesn't currently Recognise who she is talking to."
        self.max_responce_tokens = 500
        self.last_message_is_context_change = False
        self.nova = nova
        
        cn = sqlite3.connect('nova.db')
        cn.row_factory = sqlite3.Row
        c = cn.cursor()
        now = datetime.now().date()
        c.execute("SELECT * FROM messages where date = ? order by message_id asc;",(now,))
        result = c.fetchone()

        # Check the result
        results = c.fetchall()
        # Check and loop through the results
        db_messages = []
        for row in results:
            db_messages.append({"role":row["role"],"content":row["content"]})

        if(len(db_messages)):
            self.messages = db_messages
        else:
            self.messages = [{"role": "system", "content": self.assitant_prompt}]
        self.nova.events.add('ask_gpt')
        self.nova.events.add('new_messages')
        self.nova.events.add('new_context')
        self.nova.events.add('pre_OAI_user_input')

    def ask(self, text,save_responce = True,messages_append = False):
        self.nova.events.post('pre_OAI_user_input')
        if(len(self.messages) == 0):
            self.messages.append({"role": "system", "content": self.assitant_prompt})
        if(not isinstance(text, str)):
            return False
        
        openai.api_key = self.api_key
        if(messages_append != False):
            self.messages.extend(messages_append)
        self.messages.append({"role": "user", "content": text})
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            max_tokens=self.max_responce_tokens,  
        )
        response_object = response.choices[0].message
        response_content = response_object.content
        if(save_responce):
            self.messages.append({"role": response_object.role,"content": response_object.content})
            self.last_message_is_context_change = False
        return response_content

    def single_responce(self, text,use_context = False):
        if(use_context):
            print("context")
            temp_messages = self.messages.copy()
            print(temp_messages)
        else:
            temp_messages = [{"role": "assistant", "content": self.assitant_prompt}]
        if(not isinstance(text, str)):
            return False
        openai.api_key = self.api_key
        temp_messages.append({"role": "user", "content": text})
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=temp_messages,
            max_tokens=self.max_responce_tokens,  
        )
        response_content = response.choices[0].message.content
        self.last_message_is_context_change = False
        print(response_content)
        return response_content
    def prompted_responce(self, text):
        if(not isinstance(text, str)):
            return False
        openai.api_key = self.api_key
        temp_messages = self.messages.copy()
        temp_messages.append({"role": "user", "content": text})
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=temp_messages,
            max_tokens=self.max_responce_tokens,  
        )
        response_content = response.choices[0].message.content
        self.messages.append({"role":"assistant","content":response_content})
        self.last_message_is_context_change = False
        return response_content

    def context_change(self,user_api,face_count):
        verified_users = user_api.get_verified()
        recognised_users = []
        for verified_user in verified_users:
            recognised_users.append(verified_user["name"])
        recognised_users_count = len(verified_users)
        if(recognised_users_count > 0):
            recognised_users_message = ' ,'.join(recognised_users)
        else:
            recognised_users_message = ""   
        if(recognised_users_count != face_count):
            unknown_user_count = (face_count - recognised_users_count)
            if(unknown_user_count > 0):
                if(recognised_users_count > 0):
                    unknown_user_message = f"and {unknown_user_count} unknown users"
                else:
                    unknown_user_message = f"{unknown_user_count} unknown users"
            else:
                unknown_user_message = ""
        else:
            unknown_user_count = face_count
            unknown_user_message = ""

        if(unknown_user_count < 1 and recognised_users_count == 0):
            message = {"role": "system", "content": f"*Your computer vision recognises that you can see no users. you are unsure who you are talking to*"}
            if(self.last_message_is_context_change):
                last_index = len(self.messages) - 1
                self.messages[last_index] = message
            else:
                self.messages.append(message)
                self.last_message_is_context_change = True
        else:
            message = {"role": "system", "content": f"*Your computer vision recognises that you are talking to {recognised_users_message}{unknown_user_message}*"}
            if(self.last_message_is_context_change):
                last_index = len(self.messages) - 1
                self.messages[last_index] = message
            else:
                self.messages.append(message)
                self.last_message_is_context_change = True

    def ask_functions(self, text,save_responce = True,messages_append = False):
        
        self.nova.events.post('pre_OAI_user_input')
        if(len(self.messages) == 0):
            self.messages.append({"role": "system", "content": self.assitant_prompt})
        if(not isinstance(text, str)):
            return False
        
        openai.api_key = self.api_key
        if(messages_append != False):
            self.messages.extend(messages_append)
        self.messages.append({"role": "user", "content": text})
        
        functions = [
        {
            "name": "function_handler",
            "description": "Determine the action the user is asking you to do. Then call the appropriate function",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "The action the user is asking e.g. check_email, reschedule, stop_face_detect",
                    },
                    "module": {
                        "type": "string",
                        "description": "the general module to find the specific action in e.g. email, calender, face_detection",
                    },
                    "action_details": {
                        "type": "string",
                        "description": "details or parameters to be used by function being called. e.g should_respond:True, from:'3:00pm'; to:'4:00pm'. The action details arn't always neccessary.",
                    }
                },
                "module_list": {
                    "type": "string",
                    "description": "A list of models for you to choose from. The 'module_name' must come from this list.'",
                    "enum": ["calendar","email","face_detection"]
                },
                "action_list": {
                    "type": "string",
                    "description": "A list of actions for you to choose from. The 'action' must come from this list.'",
                    "enum": ["reschedule","get_events","add_event","remove_event","move_event","get_emails","send_email","get_unread"]
                },
                "required": ["action","model_name"],
            },
        }
        ]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            max_tokens=self.max_responce_tokens,
            functions = functions,
            function_call="auto",  
        )
        response_object = response.choices[0].message
        responce_content = response.choices[0].message.content
        if(response.choices[0].finish_reason == "function_call"):
            print("function_call")
            #self.function_handler(response.choices[0].message.function_call)
            print(response.choices[0].message.function_call)
            if(save_responce):
                if(response.choices[0].message.content != None):
                    self.messages.append({"role": response.choices[0].message.role,"content": response.choices[0].message.content})
                    responce_content = response.choices[0].message.content
                    self.last_message_is_context_change = False
                else:
                    self.messages.append({"role": response.choices[0].message.role,"content": "I've run the function"})
                    responce_content = "I've run the function"
                    self.last_message_is_context_change = False
        elif(response.choices[0].finish_reason == "stop"):
            self.messages.append({"role": response.choices[0].message.role,"content": response.choices[0].message.content})
            responce_content = response.choices[0].message.content
            self.last_message_is_context_change = False
        else:
            #too long response
            self.messages.append({"role": response.choices[0].message.role,"content": response.choices[0].message.content})
            responce_content = response.choices[0].message.content
            self.last_message_is_context_change = False
        return responce_content

    def ask_define_function(self, params):
        self.nova.events.post('pre_OAI_user_input')
        text = params["text"]
        if("save_responce" in params):
            save_responce = params["save_responce"]
        else:
            save_responce = True
        
        if("system_message" in params):
            system_message = {"role":"system","content":params["system"]}
        else:
            system_message = False

        if("use_context" in params):
            use_context = params["use_context"]
        else:
            use_context = False

        if("ai_prompt" in params):
            ai_prompt = params["ai_prompt"]
        else:
            ai_prompt = ''


        if(len(self.messages) == 0 and save_responce):
            self.messages.append({"role": "system", "content": self.assitant_prompt})
        else:
            if(use_context and len(self.messages) == 0):
                temp_messages = [{"role": "system", "content": self.assitant_prompt}]
            elif(use_context):
                temp_messages = self.messages.copy()
            else:
                temp_messages = [{"role": "system", "content": params["ai_prompt"]}]

        if(not isinstance(text, str)):
            return False
        
        openai.api_key = self.api_key

        
        
        if(system_message != False):
            temp_messages.append(system_message)
        temp_messages.append({"role": "user", "content": text})

        functions = [params["function"]]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=temp_messages,
            max_tokens=self.max_responce_tokens,
            functions = functions,
            function_call="auto",  
        )
        response_object = response.choices[0].message
        responce_content = response.choices[0].message.content
        if(response.choices[0].finish_reason == "function_call"):
            ret_params = json.loads(response.choices[0].message.function_call.arguments)
            responce_content = response.choices[0].message.content
            if(save_responce):
                if(response.choices[0].message.content != None):
                    self.messages.append({"role": response.choices[0].message.role,"content": response.choices[0].message.content})
                    responce_content = response.choices[0].message.content
                    self.last_message_is_context_change = False
                else:
                    self.messages.append({"role": response.choices[0].message.role,"content": "I've run the function"})
                    responce_content = "I've run the function"
                    self.last_message_is_context_change = False
        elif(response.choices[0].finish_reason == "stop"):
            responce_content = response.choices[0].message.content
            if(save_responce):
                self.messages.append({"role": response.choices[0].message.role,"content": response.choices[0].message.content})
                self.last_message_is_context_change = False
        else:
            #too long response
            responce_content = response.choices[0].message.content
            if(save_responce):
                self.messages.append({"role": response.choices[0].message.role,"content": response.choices[0].message.content})
                self.last_message_is_context_change = False
        
            responce_content = response.choices[0].message.content
        return ret_params
    def function_handler(self,function_call):
        params = json.loads(function_call.arguments)
        print(params)
        #self.nova.command_handler(params,False,True)
        pass

    def upscale_intellegence(self):
        self.model = 'gpt-4'

    def downscale_intelligence(self):
        self.model = "gpt-3.5-turbo"

    def system_message(self,message):
        message = {"role": "system", "content": message}
        self.messages.append(message)

    def say_OAI(self,text):
        try:
            client = openai.OpenAI()
            response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
            )
            response.stream_to_file("output.mp3")
            return True
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred in Nova.OAI.say_OAI: {e}")
            traceback.print_exc()
            return False

    """ def smooth_functions(self):
        print("check new email")
        OAI = self.nova.OAI
        params = {
            "save_responce": False,
            "text":  f"This is a message from the user to",
            "function":{
                    "name": "user_input_function_check",
                    "description": "This function determines if the users input is requesting a function to be run. eg(user_input:'anything important in my past few emails', output:'email')",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "important": {
                                "type": "boolean",
                                "description": "The boolean to show wether to alert the user",
                            },
                            "nova_responce_message": {
                                "type": "string",
                                "description": "The message nova will send to the user. It should summarize the email",
                            },
                        },
                        "required": ["important","nova_responce_message"],
                    },
                },
            "use_context":True
        }
        ret =  OAI.ask_define_function(params)
        if(ret["important"]):
            self.nova.OAI.messages.append({"role":"system", "content":f"[NEW EMAIL]: the subject is subject:{self.last_email.subject}:end_subject, the email body is email_body:{self.last_email.body}:end_email_body."})
            nova_response = self.nova.OAI.single_responce(f"[NOVA has received this email for the user and needs to tell them summarize it. what is NOVAs responce]",True)
            self.nova.OAI.messages.append({"role":"assistant", "content":nova_response})
            self.nova.nova_unprompted(nova_response) """
        


        