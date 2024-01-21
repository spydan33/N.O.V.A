import traceback
class events:
    def __init__(self):
        self.list = []
        self._events = {}
        self.verbose = True

    def on(self,name,do_function,data = '#1234NoDataInEvents1234#'):
        self._events[name].on(do_function,data,'NA')

    def post(self,name,data = '#1234NoDataInEvents1234#'):
        if(self.verbose):
            print(f"NEW EVENT: {name}")
        self._events[name].post(data)

    def add(self,name):
        if(name not in self.list):
            new_event = self.event(name)
            self._events[name] = new_event
            self.list.append(name)
            setattr(self, name, new_event)
    class event():
        def __init__(self,name):
            self.name = name
            self.subscribers = []

        def on(self,do_function,data,listener_name = 'NA'):
            if(data == '#1234NoDataInEvents1234#'):
               do_this = {
                "name": listener_name,
                "function_to_call" : do_function
                } 
            else:
                do_this = {
                "name": listener_name,
                "function_to_call" : do_function,
                "data": data
                } 
            self.subscribers.append(do_this)

        def post(self,data = '#1234NoDataInEvents1234#'):
            for sub in self.subscribers:
                try:
                    if isinstance(sub["function_to_call"], bool):
                        sub["function_to_call"] = not sub["function_to_call"]
                    else:
                        if(data == '#1234NoDataInEvents1234#'):
                            if('data' in sub):
                                sub["function_to_call"](sub["data"])
                            else:
                                sub["function_to_call"]()
                        else:
                            sub["function_to_call"](data)
                except Exception as e:
                    # Handle other exceptions
                    print(f"An error occurred in event:{self.name} post: {e}")
                    traceback.print_exc()
                    return False
        def remove(self,sub_name):
            for i in range(len(self.subscribers)):
                try:
                    if(self.subscribers[i].name == sub_name):
                        self.subscribers.pop(i)
                except Exception as e:
                    # Handle other exceptions
                    print(f"An error occurred in event:{self.name} remove: {e}")
                    traceback.print_exc()
                    return False

