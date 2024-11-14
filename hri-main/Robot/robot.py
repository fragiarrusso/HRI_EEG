import qi
import time
import math
import sys

class Robot():
    def __init__(self, port):
        self.session = self.initConnection(port = port)
        self.motion_service = self.session.service("ALMotion")
        self.tts_service = self.session.service("ALTextToSpeech")

        return
    
    def initConnection(self, ip = '127.0.0.1', port=44255):

        try:
            connection_url = "tcp://" + ip + ":" + str(port)
            app = qi.Application(["Move", "--qi-url=" + connection_url ])
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + ip + "\" on port " + str(port) +".\n"
                "Please check your script arguments. Run with -h option for help.")
            sys.exit(1)

        app.start()
        session = app.session

        return session

    def say(self, sentence, language = "English", speed = 1000, volume = 1.0):

        self.tts_service.setLanguage(language)
        self.tts_service.setParameter("speed", speed)
        self.tts_service.setVolume(volume)
        self.tts_service.say(sentence)

        return

    def neutral_position(self):
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand", "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand"]

        neutral_angles = [1.4, 0.15, 1.0, 0.5, 0.3, 0.5, math.radians(101.7), math.radians(5.8), math.radians(-98.5), math.radians(101.7), math.radians(-6.3), math.radians(2.0), 0.69]  # Posizione neutra per il braccio destro
        self.motion_service.angleInterpolation(names, neutral_angles, [1.0]*12, True)

        return

    def startPosition(self):
        

        shoulder_pitch_angle = math.radians(85)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        shoulder_roll_angle = math.radians(-6)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        elbow_roll_angle = math.radians(0.5)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        elbow_yaw_angle = math.radians(87)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        # r_wrist_yaw = math.radians(-1.7)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        # r_hand = 0.70  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", shoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", elbow_yaw_angle, fractionMaxSpeed)
        # self.motion_service.setAngles("RWristYaw", r_wrist_yaw, fractionMaxSpeed)
        # self.motion_service.setAngles("RHand", r_hand, fractionMaxSpeed)

        return

    def shootPosition(self):
        

        shoulder_pitch_angle = math.radians(85)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        shoulder_roll_angle = math.radians(-6)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        elbow_roll_angle = math.radians(80)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        elbow_yaw_angle = math.radians(87)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", shoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", elbow_yaw_angle, fractionMaxSpeed)

        return

    def shieldPosition(self):
        

        shoulder_pitch_angle = math.radians(0)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        shoulder_roll_angle = math.radians(-6)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        elbow_roll_angle = math.radians(73)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        elbow_yaw_angle = math.radians(10)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", shoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", elbow_yaw_angle, fractionMaxSpeed)

        return

    def chargePosition(self):
        

        shoulder_pitch_angle = math.radians(0)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        shoulder_roll_angle = math.radians(-6)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        elbow_roll_angle = math.radians(73)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        elbow_yaw_angle = math.radians(87)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", shoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", elbow_yaw_angle, fractionMaxSpeed)

        return

    def greeting(self):
        
        
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]

        # Primo movimento: alza il braccio per iniziare il saluto
        initial_angles = [math.radians(4.0), math.radians(-21.4), math.radians(69.0), math.radians(48.0), math.radians(-45.0), 0.9]
        # initial_angles = [0.2, -0.3, 1.0, 0.5, 0.3]
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)
        
        # Movimenti ripetuti del braccio
        for i in range(6):  # Numero di scuotimenti
            time.sleep(0.3)
            if i % 2 == 0:
                self.motion_service.setAngles("RElbowYaw", math.radians(50), 1.0)
            else:
                self.motion_service.setAngles("RElbowYaw", math.radians(75), 1.0)

        # # Riporta il braccio nella posizione neutra
        neutral_angles = [1.4, 0.15, 1.0, 0.5, 0.3, 0.5]  # Posizione neutra per il braccio destro
        self.motion_service.angleInterpolation(names, neutral_angles, [1.0]*6, True)

        return

    def exultation_right_arm(self):
        names = ["RElbowRoll","RElbowYaw", "RHand", "RShoulderPitch", "RShoulderRoll", "RWristYaw"]
        initial_angles = [math.radians(68.0), math.radians(70.0), 0.50, math.radians(26.0), math.radians(-2.0),  math.radians(17.2)]
        
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)


        initial_angles = [math.radians(36.0), math.radians(70.0), 0.50, math.radians(-47.0), math.radians(-2.0),  math.radians(17.2)]
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)

        initial_angles = [math.radians(68.0), math.radians(70.0), 0.50, math.radians(26.0), math.radians(-2.0),  math.radians(17.2)]
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)

        initial_angles = [math.radians(36.0), math.radians(70.0), 0.50, math.radians(-47.0), math.radians(-2.0),  math.radians(17.2)]
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)


        return

    def exultation_left_arm(self):
        names = ["LElbowRoll","LElbowYaw", "LHand", "LShoulderPitch", "LShoulderRoll", "LWristYaw"]
        initial_angles = [math.radians(-68.0), math.radians(-80.0), 0.50, math.radians(26.0), math.radians(2.0),  math.radians(17.0)]
        
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)


        initial_angles = [math.radians(-36.0), math.radians(-80.0), 0.50, math.radians(-47.0), math.radians(2.0),  math.radians(17.0)]
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)

        initial_angles = [math.radians(-68.0), math.radians(-80.0), 0.50, math.radians(26.0), math.radians(2.0),  math.radians(17.0)]
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)

        initial_angles = [math.radians(-36.0), math.radians(-80.0), 0.50, math.radians(-47.0), math.radians(2.0),  math.radians(17.0)]
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)


        return

    def exultation(self):
        names = ["RElbowRoll","RElbowYaw", "RHand", "RShoulderPitch", "RShoulderRoll", "RWristYaw", "LElbowRoll","LElbowYaw", "LHand", "LShoulderPitch", "LShoulderRoll", "LWristYaw"]

        initial_angles = [math.radians(68.0), math.radians(70.0), 0.50, math.radians(26.0), math.radians(-2.0),  math.radians(17.2), math.radians(-68.0), math.radians(-80.0), 0.50, math.radians(26.0), math.radians(2.0),  math.radians(17.0)]
        self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        initial_angles = [math.radians(36.0), math.radians(70.0), 0.50, math.radians(-47.0), math.radians(-2.0),  math.radians(17.2), math.radians(-36.0), math.radians(-80.0), 0.50, math.radians(-47.0), math.radians(2.0),  math.radians(17.0)]
        self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        initial_angles = [math.radians(68.0), math.radians(70.0), 0.50, math.radians(26.0), math.radians(-2.0),  math.radians(17.2), math.radians(-68.0), math.radians(-80.0), 0.50, math.radians(26.0), math.radians(2.0),  math.radians(17.0)]
        self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        initial_angles = [math.radians(36.0), math.radians(70.0), 0.50, math.radians(-47.0), math.radians(-2.0),  math.radians(17.2), math.radians(-36.0), math.radians(-80.0), 0.50, math.radians(-47.0), math.radians(2.0),  math.radians(17.0)]
        self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        return

    def calm_stand(self):
        names = ["RElbowRoll","RElbowYaw", "RHand", "RShoulderPitch", "RShoulderRoll", "RWristYaw", "LElbowRoll","LElbowYaw", "LHand", "LShoulderPitch", "LShoulderRoll", "LWristYaw"]

        initial_angles = [math.radians(88.0), math.radians(86.0), 0.97, math.radians(26.0), math.radians(-2.0),  math.radians(-70.0), math.radians(-88.0), math.radians(-86.0), 0.97, math.radians(26.0), math.radians(2.0),  math.radians(70.0)]
        self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        # initial_angles = [math.radians(36.0), math.radians(70.0), 0.50, math.radians(-47.0), math.radians(-2.0),  math.radians(17.2), math.radians(-36.0), math.radians(-80.0), 0.50, math.radians(-47.0), math.radians(2.0),  math.radians(17.0)]
        # self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        # initial_angles = [math.radians(68.0), math.radians(70.0), 0.50, math.radians(26.0), math.radians(-2.0),  math.radians(17.2), math.radians(-68.0), math.radians(-80.0), 0.50, math.radians(26.0), math.radians(2.0),  math.radians(17.0)]
        # self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        # initial_angles = [math.radians(36.0), math.radians(70.0), 0.50, math.radians(-47.0), math.radians(-2.0),  math.radians(17.2), math.radians(-36.0), math.radians(-80.0), 0.50, math.radians(-47.0), math.radians(2.0),  math.radians(17.0)]
        # self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        return

    def login(self):
        
        
        names = ["RElbowRoll","RElbowYaw", "RHand", "RShoulderPitch", "RShoulderRoll", "RWristYaw"]

        # Primo movimento: alza il braccio per iniziare il saluto
        initial_angles = [math.radians(71.0), math.radians(12.0), 0.97, math.radians(57.0), math.radians(-14),  math.radians(104)]
        # initial_angles = [0.2, -0.3, 1.0, 0.5, 0.3]
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)
        
        time.sleep(5)

        # Riporta il braccio nella posizione neutra
        # neutral_angles = [1.4, 0.15, 1.0, 0.5, 0.3, 0.5]  # Posizione neutra per il braccio destro
        # self.motion_service.angleInterpolation(names, neutral_angles, [1.0]*6, True)

        return
    
    def countDown(self):
        self.say("Rest")
        self.startPosition()
        time.sleep(1)
        self.say("3")
        time.sleep(1)
        self.say("2")
        time.sleep(1)
        self.say("1")
        time.sleep(1)

        return


if __name__ == "__main__":

    robot = Robot(40231)
    # robot.startPosition()
    # robot.greeting()
    # robot.login()
    # robot.exultation_right_arm()
    # robot.exultation_left_arm()
    # robot.exultation()
    robot.calm_stand()
    robot.say("Calm down! I will play softer!")
    
    # robot.countDown()
    # robot.shieldPosition()
    # robot.countDown()
    # robot.shootPosition()
    # robot.countDown()
    # robot.chargePosition()

    # print(math.degrees(0.2))
    # print(math.degrees(-0.3))
    # print(math.degrees(1))
    # print(math.degrees(0.5))
    # print(math.degrees(0.3))    