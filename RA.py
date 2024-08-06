#retreival augmented generation 
#pip install jq
import traceback
import os

class retreival_augmented_generation:
    class calendar:
        def __init__(self):
            self.index = False
            self.build_trees = ''
            self.body = ''
            self.subject = ''
            self.unread = False
            cn = sqlite3.connect('nova.db')
            c = cn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS calendar (
                message_id INTEGER,
                data JSON NOT NULL,
            );
            ''')
            cn.commit()
        
        def add(self,data)
            pass

        def build(self,data)
            pass
    
    
    class email:
        def __init__(self):
            self.index = False
            self.build_trees = ''
            self.body = ''
            self.subject = ''
            self.unread = False
            cn = sqlite3.connect('nova.db')
            c = cn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS email (
                message_id INTEGER,
                data JSON NOT NULL,
            );
            ''')
            cn.commit()

        
        def add(self,data)
            pass

        def build(self,data)
            pass

        
    def __init__(self,nova = False):
        self.nova = nova
        self.main_folder = os.path.dirname(os.path.abspath(__file__))
        self.tokens_used = 0
        self.email_index = None
        self.calendar_index = None
    
    def ask_email(self,question):
        return self.email_index.query(question, llm=ChatOpenAI())

    
    def ask_calendar(self,question):
        return self.calendar_index.query(question, llm=ChatOpenAI())

    #@lru_cache(maxsize=None)
    def email_index_load(self):
        pass

    #@lru_cache(maxsize=None)
    def calendar_index_load(self):
        cal_index = AnnoyIndex(params.dimensions + 2, 'euclidean')
        cal_index_path = "C:\\Users\\dmerg\\Documents\\Projects\\JARVIS\\data\\cal_index.ann"  # Replace with the actual file path
        if os.path.exists(cal_index_path):
            print("Loading cal...")
            index.load('cal_index.ann')
        else:
            print("building neurons...")
            index = MDNN.build(number_of_inputs,params.neuron_count)
            print("pruning outputs...")
            #MDNN.calc(inputs[0],params.n_outputs,index)
            print("Neurons ready")


            """ index.build(params.annoy_build_trees)
            index.save('neurons.ann') """
    
