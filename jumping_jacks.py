import numpy as np
import subprocess
import json
import random
from gtts import gTTS
import threading
from googletrans import Translator
import os
import subprocess
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(BASE_DIR)
rep_notif = parent_dir+"/data/videos/rep_completed.wav"
fin_notif = parent_dir+"/data/videos/finished.wav"

def UPDATE_PROGRESS(accuracy, reps, total_reps, message, status="alligned",username="default"):
        progress = {
            "reps_accuracy": accuracy,
            "reps_completed": reps,
            "total_reps": total_reps,
            "message": message,
            "status": status
        }
        
        # Define the path to the JSON file
        
        # Read the existing JSON data from the file
        try:
            with open(parent_dir+'/json/progress.json', 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {}

        # Update the user's progress
        data[username] = progress
        
        # Write the updated JSON data back to the file
        with open(parent_dir+'/json/progress.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print("Progress updated successfully.")

def generate_feedback(final_score, exercise_name):
    if final_score <= 0 or final_score > 100:
        return "Score out of range. Please provide a score between 1 and 100."
    
    feedback_messages = {
        (85, 100): [
            f"Outstanding performance on the {exercise_name}! You're are nailing it!",
            f"You're killing it with your {exercise_name}! Keep up the awesome work!",
            f"Amazing work with your {exercise_name}! You're really nailing the technique!",
            f"Solid performance! Your {exercise_name} form is looking very good."
        ],
        (75, 84): [
            f"Good job on the {exercise_name}! You're making progress, and it's showing!",
            f"Nice work! Your {exercise_name} is getting better. Keep practicing!",
            f"You're on the right path with your {exercise_name}. Your hard work is paying off!"
        ],
        (45, 74): [
            f"Decent attempt at the {exercise_name}. With a bit more practice, you'll improve quickly!",
            f"Your {exercise_name} has a good foundation, but let's aim higher. You can do it!",
            f"Not bad, but there's room to grow with your {exercise_name}. Keep at it!"
        ],
        (30, 44): [
            f"You've got the basics down for the {exercise_name}. Now, let's refine your technique!",
            f"A good start with the {exercise_name}, but let's work on your consistency.",
            f"You're getting the hang of the {exercise_name}. Focus on your form and you'll see great improvements!"
        ],
        (15, 29): [
            f"It's a start for your {exercise_name}. Remember, every expert was once a beginner!",
            f"Keep working on your {exercise_name}, and you'll see improvement. Practice makes perfect!",
            f"You're taking the first steps with your {exercise_name}. Stay persistent and the results will come!"
        ],
        (1, 14): [
            f"Every journey starts with a single step. Your {exercise_name} will only get better from here!",
            f"Your {exercise_name} is at the beginning stage, but that's where the growth starts. Keep going!",
            f"The {exercise_name} may seem tough now, but stick with it and you'll make strides!"
        ]
    }
    
    # Determine which message range the score falls into
    for score_range, messages in feedback_messages.items():
        if score_range[0] <= final_score <= score_range[1]:
            # Select a random message from the appropriate range
            feedback = random.choice(messages)
            return feedback

    return "An unexpected error occurred while generating feedback."

def translate(message,lang):
    translator = Translator()
    translation = translator.translate(message, dest=lang)
    message = translation.text
    return message

def text_to_speech_async(message,lang):
    tts = gTTS(text=message,tld="co.uk", lang=lang, slow=False)
    filename="output.wav"
    tts.save(filename)
    return filename
    
def play_audio_async(message,lang):
    # Load your audio file (replace '/path/to/your/audio/file.wav' with the actual file path)
    if lang!="en":
        message=translate(message,lang)
    audio_file_path = text_to_speech_async(message,lang)
    # process = subprocess.Popen(["afplay", audio_file_path])

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def calculate_angles(lmList):
    # Landmarks for Right Joints
    right_shoulder = lmList[12][1:3]
    right_elbow = lmList[14][1:3]
    right_wrist = lmList[16][1:3]
    right_hip = lmList[24][1:3]
    right_knee = lmList[26][1:3]
    right_ankle = lmList[28][1:3]
    right_foot = lmList[32][1:3]
    
    # Landmarks for Left Joints
    left_shoulder = lmList[11][1:3]
    left_elbow = lmList[13][1:3]
    left_wrist = lmList[15][1:3]
    left_hip = lmList[23][1:3]
    left_knee = lmList[25][1:3]
    left_ankle = lmList[27][1:3]
    left_foot = lmList[31][1:3]

    # Calculating joint angles
    angle_right_elbow = round(calculate_angle(right_shoulder, right_elbow, right_wrist), 2)
    angle_left_elbow = round(calculate_angle(left_shoulder, left_elbow, left_wrist), 2)
    angle_right_shoulder = round(calculate_angle(right_elbow, right_shoulder, right_hip), 2)
    angle_left_shoulder = round(calculate_angle(left_elbow, left_shoulder, left_hip), 2)
    angle_right_hip = round(calculate_angle(right_shoulder, right_hip, right_knee), 2)
    angle_left_hip = round(calculate_angle(left_shoulder, left_hip, left_knee), 2)
    angle_right_knee = round(calculate_angle(right_hip, right_knee, right_ankle), 2)
    angle_left_knee = round(calculate_angle(left_hip, left_knee, left_ankle), 2)
    angle_right_ankle = round(calculate_angle(right_knee, right_ankle, right_foot), 2)
    angle_left_ankle = round(calculate_angle(left_knee, left_ankle,left_foot), 2)

    return angle_right_elbow, angle_left_elbow, angle_right_shoulder, angle_left_shoulder, angle_left_hip, angle_right_hip, angle_right_knee, angle_left_knee, angle_right_ankle, angle_left_ankle

class jumping_jack():
    def __init__(self, username):
        self.username = username
        self.counter = 0
        self.stage = "down"  # Start assuming arms and legs are in the "down" position
        self.min_angle_arm_l = []
        self.min_angle_arm_r = []
        self.max_angle_arm_l = []  # Track maximum angles for the arm
        self.max_angle_arm_r = []
        self.min_angle_leg_l = []
        self.min_angle_leg_r = []
        self.max_angle_leg_l = []  # Track maximum angles for the legs
        self.max_angle_leg_r = []
        self.rep_accuracy = []
        self.total_accuracy = 0
        self.completed = False
        self.score = 0
        self.total_rep = 12
        self.lang = ""
        self.message = None
        UPDATE_PROGRESS(0, 0, 0, self.message, "alligned", self.username)

    def rep_count(self, lmList):
        # Calculate the angles for the shoulders and hips
        _, _, angle_right_shoulder, angle_left_shoulder, angle_left_hip, angle_right_hip, _, _, _, _ = calculate_angles(lmList)

        # Check if the movement is from down (arms down, legs together) to up (arms up, legs apart)
        if self.stage == "up" and (angle_right_shoulder <= 60 and angle_left_shoulder <= 60) and (angle_left_hip <= 70 and angle_right_hip <= 70):
            # Transition from up to down
            self.stage = "down"
            
        elif self.stage == "down" and (angle_right_shoulder >= 120 and angle_left_shoulder >= 120) and (angle_left_hip >= 140 and angle_right_hip >= 140):
            # Transition from down to up
            self.stage = "up"
            self.counter += 1
            self.analyze_form()  # Analyze form for accuracy

            if self.counter == self.total_rep:
                # End of the exercise session
                standing_wall_slide_data = {
                    "totalaccuracy": self.total_accuracy // self.total_rep,
                    "progress": max(self.rep_accuracy),
                    "calorie_burnt": self.counter * 0.5,  # Calories burned per rep
                    "repaccuracy": []
                }

                for i, accuracy in enumerate(self.rep_accuracy, start=1):
                    standing_wall_slide_data["repaccuracy"].append({"reps": i, "accuracy": accuracy})

                try:
                    with open(parent_dir + '/json/jumpingjack.json', 'r') as json_file:
                        data = json.load(json_file)
                except FileNotFoundError:
                    data = {}

                data[self.username] = standing_wall_slide_data

                with open(parent_dir + '/json/jumpingjack.json', 'w') as json_file:
                    json.dump(data, json_file, indent=4)

                self.message = generate_feedback(self.total_accuracy / self.counter, "Jumping Jack")
                UPDATE_PROGRESS(self.score, self.counter, self.total_rep, self.message, "completed", self.username)
                audio_thread = threading.Thread(target=play_audio_async, args=(self.message, self.lang,))
                audio_thread.start()
                self.completed = True
            else:
                audio_thread = threading.Thread(target=play_audio_async, args=(self.message, self.lang,))
                audio_thread.start()

            # Reset the angles for the next rep
            self.min_angle_arm_l = []
            self.min_angle_arm_r = []
            self.max_angle_arm_l = []
            self.max_angle_arm_r = []
            self.min_angle_leg_l = []
            self.min_angle_leg_r = []
            self.max_angle_leg_l = []
            self.max_angle_leg_r = []

        elif self.stage == "down":
            self.min_angle_arm_l.append(angle_left_shoulder)
            self.min_angle_arm_r.append(angle_right_shoulder)
            self.max_angle_arm_l.append(angle_left_shoulder)
            self.max_angle_arm_r.append(angle_right_shoulder)
            self.min_angle_leg_l.append(angle_left_hip)
            self.min_angle_leg_r.append(angle_right_hip)
            self.max_angle_leg_l.append(angle_left_hip)
            self.max_angle_leg_r.append(angle_right_hip)

    def analyze_form(self):
        # Similar form analysis as the previous exercise
        avg_min_angle_arm_l = np.mean(self.min_angle_arm_l) if self.min_angle_arm_l else 60
        avg_min_angle_arm_r = np.mean(self.min_angle_arm_r) if self.min_angle_arm_r else 60
        avg_max_angle_arm_l = np.mean(self.max_angle_arm_l) if self.max_angle_arm_l else 120
        avg_max_angle_arm_r = np.mean(self.max_angle_arm_r) if self.max_angle_arm_r else 120

        avg_min_angle_leg_l = np.mean(self.min_angle_leg_l) if self.min_angle_leg_l else 60
        avg_min_angle_leg_r = np.mean(self.min_angle_leg_r) if self.min_angle_leg_r else 60
        avg_max_angle_leg_l = np.mean(self.max_angle_leg_l) if self.max_angle_leg_l else 140
        avg_max_angle_leg_r = np.mean(self.max_angle_leg_r) if self.max_angle_leg_r else 140

        score = 100
        symmetry_tolerance = 5
        ideal_min_arm_angle = 60
        ideal_max_arm_angle = 120
        ideal_min_leg_angle = 60
        ideal_max_leg_angle = 140

        # Apply penalties for angle deviations
        if avg_min_angle_arm_l < ideal_min_arm_angle or avg_min_angle_arm_r < ideal_min_arm_angle:
            score -= 20  # Not raising arms enough
        if avg_max_angle_arm_l > ideal_max_arm_angle or avg_max_angle_arm_r > ideal_max_arm_angle:
            score -= 20  # Overextending arms

        if avg_min_angle_leg_l < ideal_min_leg_angle or avg_min_angle_leg_r < ideal_min_leg_angle:
            score -= 20  # Legs not wide enough
        if avg_max_angle_leg_l > ideal_max_leg_angle or avg_max_angle_leg_r > ideal_max_leg_angle:
            score -= 20  # Legs too wide

        # Symmetry check between arms and legs
        if abs(avg_min_angle_arm_l - avg_min_angle_arm_r) > symmetry_tolerance:
            score -= 10
        if abs(avg_max_angle_arm_l - avg_max_angle_arm_r) > symmetry_tolerance:
            score -= 10

        if abs(avg_min_angle_leg_l - avg_min_angle_leg_r) > symmetry_tolerance:
            score -= 10
        if abs(avg_max_angle_leg_l - avg_max_angle_leg_r) > symmetry_tolerance:
            score -= 10

        score = max(score, 0)

        # Provide feedback message based on form analysis (similar to previous logic)
        if score < 60:
            self.message = "Try to improve your form and keep your movements symmetrical."
        else:
            self.message = "Great form! Keep going!"

        self.rep_accuracy.append(score)
        self.total_accuracy += score

class leg_lift():
    def __init__(self, username):
        self.username = username
        self.counter = 0
        self.stage = "down"  # Start assuming legs are in the "down" position (on the ground)
        self.min_angle_leg_l = []
        self.min_angle_leg_r = []
        self.max_angle_leg_l = []  # Track maximum angles for the legs
        self.max_angle_leg_r = []
        self.rep_accuracy = []
        self.total_accuracy = 0
        self.completed = False
        self.score = 0
        self.total_rep = 15  # Example number of repetitions for leg lifts
        self.lang = ""
        self.message = None
        UPDATE_PROGRESS(0, 0, 0, self.message, "alligned", self.username)

    def rep_count(self, lmList):
        # Calculate the angles for the hips (leg lifting requires hip angle changes)
        _, _, _, _, angle_left_hip, angle_right_hip, _, _, _, _ = calculate_angles(lmList)

        # Check if the movement is from down (legs down) to up (legs raised)
        if self.stage == "up" and (angle_left_hip <= 20 and angle_right_hip <= 20):
            # Transition from up (legs lifted) to down (legs back down)
            self.stage = "down"
            
        elif self.stage == "down" and (angle_left_hip >= 80 and angle_right_hip >= 80):
            # Transition from down to up (legs lifted)
            self.stage = "up"
            self.counter += 1
            self.analyze_form()  # Analyze form for accuracy

            if self.counter == self.total_rep:
                # End of the exercise session
                leg_lift_data = {
                    "totalaccuracy": self.total_accuracy // self.total_rep,
                    "progress": max(self.rep_accuracy),
                    "calorie_burnt": self.counter * 0.4,  # Calories burned per rep
                    "repaccuracy": []
                }

                for i, accuracy in enumerate(self.rep_accuracy, start=1):
                    leg_lift_data["repaccuracy"].append({"reps": i, "accuracy": accuracy})

                try:
                    with open(parent_dir + '/json/leglift.json', 'r') as json_file:
                        data = json.load(json_file)
                except FileNotFoundError:
                    data = {}

                data[self.username] = leg_lift_data

                with open(parent_dir + '/json/leglift.json', 'w') as json_file:
                    json.dump(data, json_file, indent=4)

                self.message = generate_feedback(self.total_accuracy / self.counter, "Leg Lift")
                UPDATE_PROGRESS(self.score, self.counter, self.total_rep, self.message, "completed", self.username)
                audio_thread = threading.Thread(target=play_audio_async, args=(self.message, self.lang,))
                audio_thread.start()
                self.completed = True
            else:
                audio_thread = threading.Thread(target=play_audio_async, args=(self.message, self.lang,))
                audio_thread.start()

            # Reset the angles for the next rep
            self.min_angle_leg_l = []
            self.min_angle_leg_r = []
            self.max_angle_leg_l = []
            self.max_angle_leg_r = []

        elif self.stage == "down":
            self.min_angle_leg_l.append(angle_left_hip)
            self.min_angle_leg_r.append(angle_right_hip)
            self.max_angle_leg_l.append(angle_left_hip)
            self.max_angle_leg_r.append(angle_right_hip)

    def analyze_form(self):
        # Analyze the form based on hip angles for both legs
        avg_min_angle_leg_l = np.mean(self.min_angle_leg_l) if self.min_angle_leg_l else 20
        avg_min_angle_leg_r = np.mean(self.min_angle_leg_r) if self.min_angle_leg_r else 20
        avg_max_angle_leg_l = np.mean(self.max_angle_leg_l) if self.max_angle_leg_l else 80
        avg_max_angle_leg_r = np.mean(self.max_angle_leg_r) if self.max_angle_leg_r else 80

        score = 100
        symmetry_tolerance = 5
        ideal_min_leg_angle = 20  # Ideal angle when legs are fully raised
        ideal_max_leg_angle = 80  # Ideal angle when legs are fully lowered

        # Apply penalties for deviations
        if avg_min_angle_leg_l < ideal_min_leg_angle or avg_min_angle_leg_r < ideal_min_leg_angle:
            score -= 20  # Legs are not raised enough
        if avg_max_angle_leg_l > ideal_max_leg_angle or avg_max_angle_leg_r > ideal_max_leg_angle:
            score -= 20  # Legs are overextended

        # Symmetry check between legs
        if abs(avg_min_angle_leg_l - avg_min_angle_leg_r) > symmetry_tolerance:
            score -= 10
        if abs(avg_max_angle_leg_l - avg_max_angle_leg_r) > symmetry_tolerance:
            score -= 10

        score = max(score, 0)

        # Provide feedback message based on form analysis
        if score < 60:
            self.message = "Try to lift your legs higher and maintain symmetry."
        else:
            self.message = "Great form! Keep going!"

        self.rep_accuracy.append(score)
        self.total_accuracy += score

class mountain_climber():
    def __init__(self, username):
        self.username = username
        self.counter = 0
        self.stage = "left_up"  # Start by assuming the left knee is up
        self.min_angle_left_knee = []
        self.min_angle_right_knee = []
        self.rep_accuracy = []
        self.total_accuracy = 0
        self.completed = False
        self.score = 0
        self.total_rep = 20  # Total number of reps per leg
        self.lang = ""
        self.message = None
        UPDATE_PROGRESS(0, 0, 0, self.message, "alligned", self.username)

    def rep_count(self, lmList):
        # Calculate angles for knees and hips
        _, angle_left_knee, angle_right_knee, _, _, _, _, _, _, _ = calculate_angles(lmList)

        # Check for movement transitions between left and right knee
        if self.stage == "left_up" and angle_left_knee >= 120:
            # Transition from left knee up to down (left knee fully extended)
            self.stage = "right_up"
            
        elif self.stage == "right_up" and angle_right_knee >= 120:
            # Transition from right knee up to down (right knee fully extended)
            self.stage = "left_up"
            self.counter += 1  # One full rep (both legs) completed
            self.analyze_form()  # Analyze form for accuracy

            if self.counter == self.total_rep:
                # End of the exercise session
                mountain_climber_data = {
                    "totalaccuracy": self.total_accuracy // self.total_rep,
                    "progress": max(self.rep_accuracy),
                    "calorie_burnt": self.counter * 0.3,  # Calories burned per rep
                    "repaccuracy": []
                }

                for i, accuracy in enumerate(self.rep_accuracy, start=1):
                    mountain_climber_data["repaccuracy"].append({"reps": i, "accuracy": accuracy})

                try:
                    with open(parent_dir + '/json/mountainclimber.json', 'r') as json_file:
                        data = json.load(json_file)
                except FileNotFoundError:
                    data = {}

                data[self.username] = mountain_climber_data

                with open(parent_dir + '/json/mountainclimber.json', 'w') as json_file:
                    json.dump(data, json_file, indent=4)

                self.message = generate_feedback(self.total_accuracy / self.counter, "Mountain Climber")
                UPDATE_PROGRESS(self.score, self.counter, self.total_rep, self.message, "completed", self.username)
                audio_thread = threading.Thread(target=play_audio_async, args=(self.message, self.lang,))
                audio_thread.start()
                self.completed = True
            else:
                audio_thread = threading.Thread(target=play_audio_async, args=(self.message, self.lang,))
                audio_thread.start()

            # Reset knee angles for the next rep
            self.min_angle_left_knee = []
            self.min_angle_right_knee = []

        elif self.stage == "left_up":
            self.min_angle_left_knee.append(angle_left_knee)

        elif self.stage == "right_up":
            self.min_angle_right_knee.append(angle_right_knee)

    def analyze_form(self):
        # Analyze the form based on knee angles for both legs
        avg_min_angle_left_knee = np.mean(self.min_angle_left_knee) if self.min_angle_left_knee else 60
        avg_min_angle_right_knee = np.mean(self.min_angle_right_knee) if self.min_angle_right_knee else 60

        score = 100
        ideal_min_knee_angle = 60  # Ideal angle when knee is up and close to the chest

        # Apply penalties for deviations in knee lifts
        if avg_min_angle_left_knee > ideal_min_knee_angle:
            score -= 20  # Left knee not brought high enough
        if avg_min_angle_right_knee > ideal_min_knee_angle:
            score -= 20  # Right knee not brought high enough

        # Check if knee lifts are symmetrical
        if abs(avg_min_angle_left_knee - avg_min_angle_right_knee) > 10:
            score -= 10  # Penalty for lack of symmetry in knee lifts

        score = max(score, 0)

        # Provide feedback message based on form analysis
        if score < 60:
            self.message = "Lift your knees higher and keep your movements symmetrical."
        else:
            self.message = "Good form! Keep up the energy!"

        self.rep_accuracy.append(score)
        self.total_accuracy += score

class high_knees(): 
    def __init__(self, username):
        self.username = username
        self.counter = 0
        self.stage = "left_up"  # Start by assuming the left knee will go up first
        self.min_angle_left_knee = []
        self.min_angle_right_knee = []
        self.rep_accuracy = []
        self.total_accuracy = 0
        self.completed = False
        self.score = 0
        self.total_rep = 20  # Total reps per leg
        self.lang = ""
        self.message = None
        UPDATE_PROGRESS(0, 0, 0, self.message, "alligned", self.username)

    def rep_count(self, lmList):
        # Calculate angles for the knees
        _, angle_left_knee, angle_right_knee, _, _, _, _, _, _, _ = calculate_angles(lmList)

        # Check for movement transitions between left and right knee lifts
        if self.stage == "left_up" and angle_left_knee >= 120:
            # Transition from left knee up to down
            self.stage = "right_up"
            
        elif self.stage == "right_up" and angle_right_knee >= 120:
            # Transition from right knee up to down
            self.stage = "left_up"
            self.counter += 1  # One full rep (both legs) completed
            self.analyze_form()  # Analyze form for accuracy

            if self.counter == self.total_rep:
                # End of the exercise session
                high_knees_data = {
                    "totalaccuracy": self.total_accuracy // self.total_rep,
                    "progress": max(self.rep_accuracy),
                    "calorie_burnt": self.counter * 0.3,  # Calories burned per rep
                    "repaccuracy": []
                }

                for i, accuracy in enumerate(self.rep_accuracy, start=1):
                    high_knees_data["repaccuracy"].append({"reps": i, "accuracy": accuracy})

                try:
                    with open(parent_dir + '/json/highknees.json', 'r') as json_file:
                        data = json.load(json_file)
                except FileNotFoundError:
                    data = {}

                data[self.username] = high_knees_data

                with open(parent_dir + '/json/highknees.json', 'w') as json_file:
                    json.dump(data, json_file, indent=4)

                self.message = generate_feedback(self.total_accuracy / self.counter, "High Knees")
                UPDATE_PROGRESS(self.score, self.counter, self.total_rep, self.message, "completed", self.username)
                audio_thread = threading.Thread(target=play_audio_async, args=(self.message, self.lang,))
                audio_thread.start()
                self.completed = True
            else:
                audio_thread = threading.Thread(target=play_audio_async, args=(self.message, self.lang,))
                audio_thread.start()

            # Reset knee angles for the next rep
            self.min_angle_left_knee = []
            self.min_angle_right_knee = []

        elif self.stage == "left_up":
            self.min_angle_left_knee.append(angle_left_knee)

        elif self.stage == "right_up":
            self.min_angle_right_knee.append(angle_right_knee)

    def analyze_form(self):
        # Analyze form based on the minimum knee angles for both legs
        avg_min_angle_left_knee = np.mean(self.min_angle_left_knee) if self.min_angle_left_knee else 60
        avg_min_angle_right_knee = np.mean(self.min_angle_right_knee) if self.min_angle_right_knee else 60

        score = 100
        ideal_min_knee_angle = 60  # Ideal angle when knee is high up

        # Apply penalties for knees not reaching high enough
        if avg_min_angle_left_knee > ideal_min_knee_angle:
            score -= 20  # Left knee not lifted high enough
        if avg_min_angle_right_knee > ideal_min_knee_angle:
            score -= 20  # Right knee not lifted high enough

        # Symmetry check between knee lifts
        if abs(avg_min_angle_left_knee - avg_min_angle_right_knee) > 10:
            score -= 10  # Penalty for lack of symmetry in knee lifts

        score = max(score, 0)

        # Provide feedback message based on form analysis
        if score < 60:
            self.message = "Lift your knees higher and keep your movements symmetrical."
        else:
            self.message = "Excellent form! Keep pushing!"

        self.rep_accuracy.append(score)
        self.total_accuracy += score