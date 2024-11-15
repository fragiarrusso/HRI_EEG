import os
import sys
import socket
import json

sys.path.append(os.getenv('PEPPER_TOOLS_HOME')+'/cmd_server')

import pepper_cmd
from pepper_cmd import *

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)


class RobotCommunicator():
    def __init__(self, ip = '172.17.0.1', port = 9000):
        self.initSocket(ip, port)
        return
    
    def initSocket(self, ip, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip, port))  # Assicurati che la porta 12345 sia esposta dal Docker
        return

    def closeSocketConnection(self):
        self.client_socket.close()
        return

    def sendMessageSocket(self, message):
        self.client_socket.sendall(bytes(json.dumps(message).encode('UTF-8')))
        return
    
    def readMessageSocket(self):
        response = self.client_socket.recv(1024)
        return response.decode()


    def read_EEG_Message_Socket(self):
        response = self.client_socket.recv(1024)
        return response.decode('utf-8')

    
    def say(self, message):
        socketMessage = {
            'action': 'say',
            'message': message
        }

        self.sendMessageSocket(socketMessage)
        self.readMessageSocket()

        return
    
    def move(self, action):
        socketMessage = {
            'action': action
        }

        self.sendMessageSocket(socketMessage)
        self.readMessageSocket()

    
        return
    
robotCommunicator = RobotCommunicator() 

begin()

pepper_cmd.robot.say('Hello')

i=0
while i<=5:
    result=robotCommunicator.read_EEG_MessageSocket()
    pepper_cmd.robot.say(result)
    i+=1

pepper_cmd.robot.say('Bye')
end()