from flask import Flask, render_template, Response, jsonify, request
import json
import time
import os
import logging
import subprocess
from nova import nova
#url for flask is 'http://127.0.0.1:5000'

#logging all server events
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
class NoLoggingFilter(logging.Filter):
    def filter(self, record):
        return 0


app = Flask(__name__)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(NoLoggingFilter())
#end server events

new_event = ''
@app.route('/')
def index():
    """ current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    print("Current dir path:", current_directory) """
    return render_template('jarvis_ui.html')

@app.route('/gpt_ui')
def gpt_ui():
    return render_template('gpt_ui.html')

@app.route('/reverify')
def reverify():
    nova.face.verify_face = True
    return 'true'

@app.route('/get_updates', methods=['POST'])
def get_updates():
    data = {
        "capture_face": nova.capture_face,
        "listening_for_name": nova.listening_for_name,
        "talk": nova.talk,
        "messages": nova.OAI.messages,
        "responding": nova.responding,
        "verified_face_count": nova.face.verified_face_count,
        "face_count": nova.face.face_count,
        "smooth_functions": nova.smooth_functions,
        "show_vision": nova.face.show_vision,
        "last_code": nova.last_code,
        "new_event": nova.events.last_event
    }
    if(nova.face.verified_face_count > 0):
        users = nova.users_api.get_verified()
        data["users"] = ''
        for user in users:
            data["users"] += f'{user["name"]}, '
    """ "cpu_temp": get_cpu_temperature() """
    return jsonify(data)

@app.route('/load_once')
def load_once():
    nova.calendar.update_nova_on_upcoming()
    nova.attention.start()
    nova.prompted("greeting_events")
    return 'true'

@app.route('/verify_user')
def verify_user():
    nova.face.verify_face = True
    return 'true'

@app.route('/save_chats')
def save_chats():
    nova.save_chats()
    return 'true'

@app.route('/start_vision')
def start_vision():
    nova.detect_face()
    return 'true'

@app.route('/stop_vision')
def stop_vision():
    nova.face.stop_detect()
    return 'true'

@app.route('/show_vision_off')
def show_vision_off():
    nova.face.show_vision = False
    nova.face.draw_face = False
    return 'true'

@app.route('/show_vision_on')
def show_vision_on():
    nova.face.show_vision = True
    nova.face.draw_face = True
    return 'true'

@app.route('/talk_on')
def stop_talk():
    nova.talk = True
    return 'true'

@app.route('/talk_off')
def start_talk():
    nova.talk = False
    return 'true'

@app.route('/start_listening_for_name')
def start_listening_for_name():
    nova.listen_for_name()
    return 'true'

@app.route('/stop_listening_for_name')
def stop_listening_for_name():
    nova.listening_for_name = False
    return 'true'

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    ret = nova.send_text(data["text"])
    print(ret)
    return jsonify({"ret_text":ret})

@app.route('/python_command', methods=['POST'])
def python_command():
    data = request.json
    print(data["text"])
    try:
        # Execute the code using exec
        exec(data["text"])
        return jsonify({"ret_text":'true'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"ret_text":'failed'})

if __name__ == '__main__':
    nova = nova()
    """ def update_event(name):
        print("new event in f main")
        print(name)
        new_event = name
    nova.events.on("new_event",update_event) """
    app.run(debug=False)