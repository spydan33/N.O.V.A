from listen import voice
import traceback
import math
import time
import os
import face_recognition
import threading
import cv2
class face():
    def __init__(self,tick_time,nova = False):
        self.nova = nova
        self.tick_time = tick_time
        self.users = nova.users_api.users
        self.show_cam = True
        self.detect_running = False
        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.listen_now = False
        self.draw_face = True
        self.draw_eyes = True
        self.show_vision = False
        self.face_count = 0
        self.verified_face_count = 0
        self.face_change = False
        self.verify_face = False
        self.reverify = False
        self.reverify_interval = 180000 #number in seconds to wait before reverifying users
        self.verify_then_interval = True
        folder_path = f"{nova.root_path}\\known_user_face"
        for filename in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, filename)):
                user_image = face_recognition.load_image_file(os.path.join(folder_path, filename))
                known_face = face_recognition.load_image_file(os.path.join(folder_path, filename))
                if(len(face_recognition.face_encodings(known_face)) > 0):
                    known_face_encoding = face_recognition.face_encodings(known_face)[0]
                #replace with dynamic data retreival -Daniel
                for user_obj, prop in self.users.items():
                    if(prop["name"] in filename):
                        self.users[prop["name"]]["face_encoding"].append(known_face_encoding)
        
        #make face events
        nova.events.add('face_count_change')
        nova.events.add('face_change')
        nova.events.add('face_looking_at_camera')
        nova.events.add('face_verifying')
        nova.events.add('face_verified')
        nova.events.add('capture_face_stop')
        nova.events.add('capture_face_start')
        nova.events.add('show_vision')
        nova.events.add('hide_vision')
        nova.events.add('verify_face')

        #event listeners
        nova.events.on('capture_face_stop',self.stop_detect)
        nova.events.on('show_vision',self.show_vision_func)
        nova.events.on('hide_vision',self.hide_vision)
        nova.events.on('verify_face',self.verify_face_func)
                
    def verify_face_func(self):
        if(self.detect_running):
            self.verify_face = True
        else:
            self.verify_face = True
            self.detect()

    def hide_vision(self):
        self.show_vision = False
        cv2.destroyAllWindows()
        
    def show_vision_func(self):
        self.show_vision = True
    
    def stop_detect(self):
        self.detect_running = False
        self.nova.capture_face = False
        self.cap.release()
        cv2.destroyAllWindows()

    def start_detecting(self):
        try:
            face_confirm_change_frames_amount = 5
            face_confirm_count = 0
            
            looking_confirm_change_frames_amount = 1
            looking_confirm_count = 0

            thread_reverify = threading.Thread(target = self.reverify_users,daemon = True)
            thread_reverify.start()
            self.detect_running = True
            while self.detect_running:
                ret = self.detect()
                if(ret == 'Failed capture'):
                    continue
                self.listen_now = ret["listen_now"]
                if(ret["face_change_detect"]):
                    face_confirm_count = face_confirm_count + 1
                    if(face_confirm_count == face_confirm_change_frames_amount):
                        self.face_count = ret["current_face_count"]
                        self.face_change = True
                        params = {"face_count":ret["current_face_count"],"verified_face_count":0}
                        self.nova.events.post('face_change',params)
                        face_confirm_count = 0
                else:
                    face_confirm_count = 0

                if(self.listen_now):
                    looking_confirm_count = looking_confirm_count + 1
                    if(looking_confirm_count == looking_confirm_change_frames_amount):
                        self.nova.events.post('face_looking_at_camera')
                        pass
                else:
                    looking_confirm_count = 0
                time.sleep(self.tick_time)
            self.detect_running = False
            self.reverify = False
            thread_reverify.join()
            return True
        except Exception as e:
            print(f"An error occurred in detection loop: {e}")
            traceback.print_exc()
            return False
    
    def reverify_users(self):
        while self.reverify:
            if(self.verify_then_interval):
                if(self.verified_face_count > 0):
                    time.sleep(self.reverify_interval)
                else:
                    self.verify_face = True
                    print("reverify")
                    self.nova.events.post('face_verifying')
                    time.sleep(2)
            else:
                time.sleep(self.reverify_interval)
            self.verify_face = True

    def detect(self):
        ret, frame = self.cap.read()
        if not ret:
            return Exception("Failed capture")

        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #detect faces
        ret1 = self.detect_faces(frame,gray_image)
        face_change_detect = False
        if(self.face_count != ret1[0]):
            face_change_detect = True
        frame = ret1[1]
        #detect eyes and calculate % difference in radius for listen activation
        ret2 = self.detect_eyes(frame,gray_image)
        radius_percent_diffs = ret2[0]
        frame = ret2[1]
        
        if(self.show_vision):
            cv2.imshow('Frame', frame)
            cv2.moveWindow('Frame', 100, 100)
        
        listen_now = False
        for i in range(len(radius_percent_diffs)):
            if radius_percent_diffs[i] < 0.05:
                listen_now = True
                #self.nova.events.post('face_looking_at_camera') //here
                break
            else:
                listen_now = False
        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass
        final_return = {
            "listen_now": listen_now,
            "face_change_detect": face_change_detect,
            "current_face_count": ret1[0]
        }
        return final_return
            # Break the loop on 'q' key press
    
    def detect_faces(self,frame,gray_image):
        faces = self.face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)
        
        if(self.verify_face):
            self.identify_faces(frame)
        for (x, y, w, h) in faces:
            name = "Unknown"
            known_names =[]
            if(self.draw_face):
                for user_obj, prop in self.users.items():
                    user = prop
                    if prop["matched_face"]:
                        known_names.append([user["name"],False])
            drew_known_face = False
            for name in known_names:
                if(not name[1] and self.draw_face):
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, name[0], (x + 6, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 1)
                    name[1] = True
                    drew_known_face = True
                    break
            if(not drew_known_face and self.draw_face):
                #unknown user
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frame, name, (x + 6,  y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 1)
        
        if(self.face_change):
            self.face_count = len(faces)
        return [len(faces),frame]

    def identify_faces(self,frame):
        #faces = self.face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)
        rgb_frame = frame[:, :, ::-1]
        try:
            small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                break_flag = False

                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                for user_obj, prop in self.users.items():
                    if(break_flag):
                        break
                    user = prop
                    if(user["has_face_image"]):
                        matches = face_recognition.compare_faces([user["face_encoding"]], face_encoding)
                        self.users[user["name"]]["matched_face"] = False
                        self.verified_face_count = 0
                        for match in matches:
                            if(break_flag):
                                break
                            if True in match:
                                if(not user["matched_face"]):
                                    self.face_change = True
                                    self.verified_face_count = self.verified_face_count + 1
                                    params = {"face_count":len(face_locations),"verified_face_count":0}
                                    self.nova.events.post('face_change',params)
                                self.users[user["name"]]["matched_face"] = True
                                params = {"user_name":user["name"]}
                                self.nova.events.post('face_verified',params)
                                break_flag = True
            
            
            if(len(face_locations) == 0):
                print("no faces")
                for user_obj, prop in self.users.items():
                    user = prop
                    self.users[user["name"]]["matched_face"] = False
                    if(user["matched_face"]):
                        self.face_change = True
                        params = {"face_count":ret["current_face_count"]}
            self.verify_face = False

        except Exception as e:
            print(f"An error occurred in face detection: {e}")
            traceback.print_exc()
            return frame
        return frame

    def detect_eyes(self,frame,gray_image):
        # Detect eyes in the image
        eyes = self.eye_cascade.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5)

        # Draw rectangles around the detected eyes and calculate distance
        radius_percent_diffs = []
        try:
            radius_array = []
            count = 0
            for (x, y, w, h) in eyes:
                count = count + 1
                eye_center_x = x + w // 2
                eye_center_y = y + h // 2
                radius = min(w, h) // 2
                
                # Draw a circle around the eye
                if(self.draw_eyes):
                    cv2.circle(frame, (eye_center_x, eye_center_y), radius, (0, 255, 0), 2)
                    cv2.putText(frame, f'Radius: {radius:.2f}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                radius_array.append(radius)
                if(count % 2 == 0):
                    absolute_difference = abs(radius_array[0] - radius_array[1])
                    average = (radius_array[0] + radius_array[1]) / 2
                    percent_difference = (absolute_difference / average)
                    radius_percent_diffs.append(percent_difference)
                    radius_array = []
        except Exception as e:
            pass
        return radius_percent_diffs,frame


