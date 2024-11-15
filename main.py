import os
import sys
import socket
import json

sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *
from robot_comunicator import *

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

robotCommunicator = RobotCommunicator() 

begin()

pepper_cmd.robot.say('Hello')

i=0
while i<=5:
    result=robotCommunicator.read_EEG_Message_Socket()
    pepper_cmd.robot.say(result)
    i+=1

pepper_cmd.robot.say('Bye')
end()
