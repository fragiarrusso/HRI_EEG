import os
import sys
import time

sys.path.append(os.getenv('PEPPER_TOOLS_HOME') + '/cmd_server')

import pepper_cmd
from pepper_cmd import *
from robot_comunicator import *

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

# Define states
INITIAL_STATE = "INITIAL_STATE"
PRESENTATION = "PRESENTATION"
states = [INITIAL_STATE, PRESENTATION]
current_state = INITIAL_STATE


'''begin()

pepper_cmd.robot.say('Hello')

i=0
while i<=5:
    result=robotCommunicator.read_EEG_Message_Socket()
    pepper_cmd.robot.say(result)
    i+=1

pepper_cmd.robot.say('Bye')
end()
'''

# Start robot
begin()

# Initialize Pepper's sensors
pepper_cmd.robot.startSensorMonitor()

pepper_cmd.robot.say("Hello, I am ready to start!")

# Function to check for face or hand touch
def detect_trigger():
    # Check for face detection or hand touch
    face_detected = pepper_cmd.robot.got_face  # True if a face is detected
    hand_touched = pepper_cmd.robot.handTouch[0] > 0 or pepper_cmd.robot.handTouch[1] > 0  # True if either hand is touched
    return face_detected or hand_touched

try:
    while True:
        if current_state == INITIAL_STATE:
            pepper_cmd.robot.say("Waiting for interaction...")
            while current_state == INITIAL_STATE:
                if detect_trigger():
                    pepper_cmd.robot.say("Interaction detected! Moving to presentation mode.")
                    current_state = PRESENTATION

        if current_state == PRESENTATION:
            pepper_cmd.robot.say("Starting presentation...")
            for _ in range(5):  # Perform the presentation (e.g., read and speak messages)
                message = pepper_cmd.robot.sensorvaluestring()
                pepper_cmd.robot.say("Processing data: "+ message)
                time.sleep(1)  # Simulate a delay between messages
            pepper_cmd.robot.say("Presentation complete.")
            break  # End the loop after presentation
except KeyboardInterrupt:
    pepper_cmd.robot.say("Exiting program. Goodbye!")
finally:
    pepper_cmd.robot.stopSensorMonitor()
    end()

