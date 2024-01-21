from code_handler import code_handler
from force_responce import force_responce
from instant_commands import instant_commands
class process_string:
    def input_string(input_str,nova):
        ret = instant_commands.check(input_str,nova)
        if(ret == 'quit'):
            return 'quit'
        if(ret):
            return False
        else:
            return True
    def ret_string(response_string,nova):
        if("```" in response_string):
            code = code_handler(nova)
            new_string = code.strip(response_string)
            nova.events.post('code_in_response',code.code)
            if(False): #nova talk
                if(ret):
                    code.save()
                    force_responce.predefined("code_save_done")
                ret = force_responce.predefined("explain")
                if(ret):
                    final_ret = [True,new_string]
                else:
                    final_ret = [False,new_string]
            else:
                final_ret = [True,new_string]
            return final_ret
        else:
            return [True,response_string]

