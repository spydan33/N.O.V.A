import json
class users:
    def __init__(self):
        json_file_path = 'json_data/users.json'
        try:
            with open(json_file_path, 'r') as json_file:
                # Load the JSON data from the file
                self.users = json.load(json_file)
        except FileNotFoundError:
            print(f"File not found: {json_file_path}")
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred: {e}")

        self.verified_face_count = 0
    def get_verified(self):
        verified_users = []
        try:
            for user_obj, prop in self.users.items():
                user = prop
                if(user["matched_face"]):
                    verified_users.append(user)
                    self.varified_face_count = len(verified_users)        
            return verified_users
        except Exception as e:
            traceback.print_exc()
            print(f"An error occurred: {e}")

