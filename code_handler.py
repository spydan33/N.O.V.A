import re
import traceback
class code_handler():
    def __init__(self,nova):
        self.code  = []
        self.nova = nova

    def strip(self,input_str):
        try:
            non_code_strings = []
            split_string = input_str.split("```")
            count_code = 1
            print(split_string)
            for i in range(len(split_string)):
                if(i == 0):  
                    self.code.append(split_string[i+1])
                    print("-------------------------------------------------- Code -------------------------------------------")
                    print(f"Code Snippet {count_code}: \n {split_string[i+1]}")
                    non_code_strings.append(split_string[i]+split_string[i+2])
                    count_code = count_code + 1
                else:
                    if((i % 2 == 0 and i != 2) or i in [0,1,2]):
                        continue
                    else:
                        self.code.append(split_string[i])
                        print("-------------------------------------------------- Code -------------------------------------------")
                        print(f"Code Snippet {count_code}: \n {split_string[i]}")
                        count_code = count_code + 1
                        if 0 <= i+2 < len(split_string):
                            non_code_strings.append(split_string[i+1]+f" Code Snippet {count_code}:")
            return " ".join(non_code_strings)
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred in code strip: {e}")
            traceback.print_exc()
            return ''
        

    def save(self):
        filename = 'code/output_code.txt'
        try:
            with open(filename, 'w') as file:
                file.write(join("\n".join(self.code)))
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")
            traceback.print_exc()
            return False