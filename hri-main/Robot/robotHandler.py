import socket
import json
import threading

from robot import *

class RobotHandler():
    def __init__(self):

        self.robot = Robot(port = 35643)
        return
    
    def handle_connection(self, client_socket, addr):
        try:
            while True:
                    received = client_socket.recv(1024)
                    if not received:
                        break

                    received = received.decode('UTF-8')
                    received = json.loads(received)
                    data = {str(k): str(v) for k, v in received.items()}
                    
                    response = self.handle(data)

                    response = json.dumps(response)
                    client_socket.sendall('Done')
        except:
            print("Released ", addr)
            client_socket.close()
        
        return
    
    def startSocket(self):


        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.bind(('0.0.0.0', 12345))  # '0.0.0.0' permette connessioni da qualsiasi indirizzo
        server_socket.bind(('0.0.0.0', 12345))  # '0.0.0.0' permette connessioni da qualsiasi indirizzo
        server_socket.listen(5)

        while True:
            client_socket, addr = server_socket.accept()
            print("Connected by", addr)

            client_handler = threading.Thread(target=self.handle_connection, args=(client_socket, addr,))
            client_handler.start()
            
        return
    
    def handle(self, data):
        print("data: ", data)

        if data['action'] == 'say':
            self.robot.say(data['message'])
            
        if data['action'] == 'shield':
            self.robot.countDown()
            self.robot.shieldPosition()
            self.robot.say(data['action'])

        if data['action'] == 'shoot':
            self.robot.countDown()
            self.robot.shootPosition()
            self.robot.say(data['action'])

        if data['action'] == 'charge':
            self.robot.countDown()
            self.robot.chargePosition()
            self.robot.say(data['action'])

        if data['action'] == 'only_shield':
            self.robot.shieldPosition()

        if data['action'] == 'only_shoot':
            self.robot.shootPosition()

        if data['action'] == 'only_charge':
            self.robot.chargePosition()

        if data['action'] == 'greeting':
            self.robot.greeting()

        if data['action'] == 'login':
            self.robot.login()

        if data['action'] == 'exultation':
            self.robot.exultation()
            self.robot.neutral_position()

        if data['action'] == 'calm_stand':
            self.robot.calm_stand()
            self.robot.neutral_position()

        if data['action'] == 'start_position':
            self.robot.neutral_position()


        time.sleep(1)

        return data




if __name__ == "__main__":

    robotHandler = RobotHandler()
    robotHandler.startSocket()
    robotHandler.robot.say("Hello World")

    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.bind(('0.0.0.0', 12345))  # '0.0.0.0' permette connessioni da qualsiasi indirizzo
    # server_socket.listen(1)

    # while True:
    #     client_socket, addr = server_socket.accept()
    #     print "Connected by", addr
    #     while True:
    #         data = client_socket.recv(1024)
    #         if not data:
    #             break
    #         client_socket.sendall(data)
    #     client_socket.close()

