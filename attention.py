import time
import threading
import traceback
from datetime import datetime
"""
# future of attention
#
# I would like this module to be the main function loop
# NOVA should loop through a list of action items to attend to based on priority and do them
#
# This module should also have her main context and allow for context based action. EG discussing a particular event for a couple of messages
# then saying "just move it to thursday." the LLM will not now what "it" is with enough accureacy to do anything(like knowing the event or email id)
# so as the context of the discussion changes those relevent details should be kept here.
#   *One possible idea for this is an in memory fuzzy search using vectors of her responce to determine the context.
#
"""
class attention:
    def __init__(self,nova):
        self.prompt_user = False
        self.tick_time = 30
        self.nova = nova
        self.thread = False
        self.items = [] #in future run attention through the items in the attention list perhaps add a prioity. this will help reduce the need for threads as she runs through her attention list
        self.last_email = nova.email.last()
        if(self.last_email is not False and self.last_email is not None):
            self.nova.OAI.messages.append({"role":"system", "content":f"[NEW EMAIL]: the subject is subject:{self.last_email.subject}:end_subject, the email body is email_body:{self.last_email.body}:end_email_body."})
        self.current_time = ''
        
        nova.events.add('new_email')
        nova.events.add('calander_event_reminder')
        nova.events.add('attention_respond')
        nova.events.add('email_not_important')

        nova.events.on('new_email',self.__check_new_email)
        nova.events.on('pre_OAI_user_input',self.__update_time)

    def start(self):
        self.thread = threading.Thread(target = self.__attention_loop)
        self.thread.start()
        
    def __attention_loop(self):
        try:
            while self.nova.running: #adjust to run through attention list
                self.__check_email()
                current_time = datetime.now().strftime("%H:%M:%S")
                self.current_time = f"[current time is: {current_time}]"
                time.sleep(self.tick_time)
        
        except HttpError as error:
            print('An error occurred: %s' % error)
            
            traceback.print_exc()
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            traceback.print_exc()

    def __check_email(self):
        try:
            last_email = self.nova.email.last()
            if(self.last_email == False and last_email != False and last_email is not None):
                self.last_email = last_email
                self.nova.events.post('new_email')
                return
            elif(last_email == False or last_email is None):
                return
            if(last_email.id != self.last_email.id ):
                self.last_email = last_email
                self.nova.events.post('new_email')
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            traceback.print_exc()
        

    def __check_calander(self):
        pass

    def __check_new_email(self):
        print("check new email")
        OAI = self.nova.OAI
        params = {
            "save_responce": False,
            "text":  f"nova received this email from the users email please determine if they should now about the new email or wether it's not that important. subject:{self.last_email.body}:end_subject email_body:{self.last_email.body}:end_email_body.",
            "function":{
                    "name": "important_email_check",
                    "description": "This function determines if the provided email is important and the user should be alerted that they received it or if It is usless and would waste their time. Generally marketing attempts are not important",
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
            self.nova.nova_unprompted(nova_response)
        else:
            self.nova.events.post('email_not_important')
            print("not important")
    def __update_time(self):
        self.nova.OAI.system_message(self.current_time)
