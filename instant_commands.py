import json
import traceback
import sys
class instant_commands:
    protocols = ["alpha","bravo"]
        
    def check(voice_string,nova):
        #trying to make dynamic
        voice_string = voice_string.lower()
        if("--quit" in voice_string or "protocol force quit" in voice_string):
            print(voice_string)
            print("quit message sent")
            return "quit"
        if("protocol" in voice_string or "--" in voice_string):
            for protocol in instant_commands.protocols:
                if(protocol+" protocol" in voice_string or "protocol "+protocol in voice_string or "--"+protocol in voice_string):
                    json_file_path = 'json_data/protocol_'+protocol+'.json'
                    try:
                        with open(json_file_path, 'r') as json_file:
                            # Load the JSON data from the file
                            data = json.load(json_file)
                            for command_name in data.keys():
                                if(command_name in voice_string):
                                    command = data[command_name]
                                    if(command["permission_level"] == "general"):
                                        if("no reply" in voice_string):
                                            reply = False
                                        else:
                                            reply = True
                                            nova.command_handler(command,reply,False)
                                        return True
                                    else:
                                        if(instant_commands.permission_check(nova.users_api,command)):
                                            nova.command_handler(command,reply,False)
                                            return True
                                        else:
                                            return True
                            return False
                                    
                    except FileNotFoundError:
                        print(f"File not found: {json_file_path}")
                    except json.JSONDecodeError as e:
                        print(f"JSON decoding error: {e}")
                    except Exception as e:
                        traceback.print_exc()
                        print(f"An error occurred: {e}")
            return False
        else:
            return False

    def permission_check(users_api,command):
        verified_users = users_api.get_verified()
        
        ret = False
        for i in range(len(verified_users)):
            if(verified_users[i]["permission_level"] == "root"):
                ret = True
                print("Access Granted")
                break
            elif(int(verified_users[i]["permission_level"]) > command["permission_level"]):
                ret = True
                print("Access Granted")
                break
        if(not ret):
                print("Access Denied")
        return ret


