import qi # type: ignore
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

    def say(self, sentence, language = "English", speed = 200, volume = 1.0):

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

        shoulder_pitch_angle = math.radians(90)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Rshoulder_roll_angle = math.radians(-8.5)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_roll_angle = math.radians(8.5)
        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        Relbow_roll_angle = math.radians(2)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_roll_angle = math.radians(-2)
        Relbow_yaw_angle = math.radians(70)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_yaw_angle = math.radians(-70)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", Rshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", Relbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", Relbow_yaw_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderRoll", Lshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowRoll", Lelbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowYaw", Lelbow_yaw_angle, fractionMaxSpeed)

        return

    def backSmallCirclePosition(self):
        
        Rshoulder_pitch_angle = math.radians(119)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_pitch_angle = math.radians(0)
        Rshoulder_roll_angle = math.radians(-89)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_roll_angle = math.radians(89)
        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        elbow_roll_angle = math.radians(27)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Relbow_yaw_angle = math.radians(119)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_yaw_angle = math.radians(0)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", Rshoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", Rshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", Relbow_yaw_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderPitch", Lshoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderRoll", Lshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowYaw", Lelbow_yaw_angle, fractionMaxSpeed)
        return
        
    def topSmallCirclePosition(self):
        

        Rshoulder_pitch_angle = math.radians(119)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_pitch_angle = math.radians(0)
        Rshoulder_roll_angle = math.radians(-89)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_roll_angle = math.radians(89)
        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        elbow_roll_angle = math.radians(27)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Relbow_yaw_angle = math.radians(119)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_yaw_angle = math.radians(0)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", Rshoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", Rshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", Relbow_yaw_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderPitch", Lshoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderRoll", Lshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowYaw", Lelbow_yaw_angle, fractionMaxSpeed)

        return
        
    def frontSmallCirclePosition(self):
        

        shoulder_pitch_angle = math.radians(119)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Rshoulder_roll_angle = math.radians(-85)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_roll_angle = math.radians(85)
        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        elbow_roll_angle = math.radians(27)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        elbow_yaw_angle = math.radians(75)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", Rshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", elbow_yaw_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderRoll", Lshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowYaw", elbow_yaw_angle, fractionMaxSpeed)

        return
    
    def bottomSmallCirclePosition(self):
        

        shoulder_pitch_angle = math.radians(0)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Rshoulder_roll_angle = math.radians(-85)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_roll_angle = math.radians(85)
        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        elbow_roll_angle = math.radians(27)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        elbow_yaw_angle = math.radians(75)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", Rshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", elbow_yaw_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderRoll", Lshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowRoll", elbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowYaw", elbow_yaw_angle, fractionMaxSpeed)

        return

    def smallcircle(self):
        self.topSmallCirclePosition()
        time.sleep(1)
        self.frontSmallCirclePosition()
        time.sleep(1)
        self.bottomSmallCirclePosition()
        time.sleep(1)
        self.backSmallCirclePosition()

        return

    def armsinfrontPosition(self):

        shoulder_pitch_angle = math.radians(0)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Rshoulder_roll_angle = math.radians(-8.5)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_roll_angle = math.radians(8.5)
        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        Relbow_roll_angle = math.radians(2)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_roll_angle = math.radians(-2)
        Relbow_yaw_angle = math.radians(70)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_yaw_angle = math.radians(-70)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", Rshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", Relbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", Relbow_yaw_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderRoll", Lshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowRoll", Lelbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowYaw", Lelbow_yaw_angle, fractionMaxSpeed)

        return

    def armsupPosition(self):
        
        shoulder_pitch_angle = math.radians(-90)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Rshoulder_roll_angle = math.radians(-8.5)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_roll_angle = math.radians(8.5)
        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        Relbow_roll_angle = math.radians(2)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_roll_angle = math.radians(-2)
        Relbow_yaw_angle = math.radians(70)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_yaw_angle = math.radians(-70)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", Rshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", Relbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", Relbow_yaw_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderRoll", Lshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowRoll", Lelbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowYaw", Lelbow_yaw_angle, fractionMaxSpeed)

        return

    def armsoutPosition(self):
        
        shoulder_pitch_angle = math.radians(0)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Rshoulder_roll_angle = math.radians(-90)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_roll_angle = math.radians(90)
        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        Relbow_roll_angle = math.radians(2)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_roll_angle = math.radians(-2)
        Relbow_yaw_angle = math.radians(70)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_yaw_angle = math.radians(-70)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", Rshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", Relbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", Relbow_yaw_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderRoll", Lshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowRoll", Lelbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowYaw", Lelbow_yaw_angle, fractionMaxSpeed)

        return

    def bigcircle(self, speed):

        self.startPosition()
        time.sleep(speed)
        self.armsinfrontPosition()
        time.sleep(speed)
        self.armsupPosition()
        time.sleep(speed)
        self.armsoutPosition()
        time.sleep(speed)
        self.startPosition()
        time.sleep(speed)

        return

    def armsoutfrontPosition(self):
        
        shoulder_pitch_angle = math.radians(0)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Rshoulder_roll_angle = math.radians(-60)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lshoulder_roll_angle = math.radians(60)
        # Impostare l'angolo del giunto RElbowRoll per fare in modo che il braccio punti verso il basso
        Relbow_roll_angle = math.radians(2)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_roll_angle = math.radians(-2)
        Relbow_yaw_angle = math.radians(70)  # Angolo in radianti (esempio di angolo, sperimenta con valori diversi)
        Lelbow_yaw_angle = math.radians(-70)

        fractionMaxSpeed = 0.5  # Velocita massima del movimento (da 0.0 a 1.0)

        # Settare gli angoli dei giunti
        self.motion_service.setAngles("RShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RShoulderRoll", Rshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowRoll", Relbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("RElbowYaw", Relbow_yaw_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderPitch", shoulder_pitch_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LShoulderRoll", Lshoulder_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowRoll", Lelbow_roll_angle, fractionMaxSpeed)
        self.motion_service.setAngles("LElbowYaw", Lelbow_yaw_angle, fractionMaxSpeed)

        return

    def pushout(self,speed):

        self.armsoutPosition()
        time.sleep(speed)
        self.armsoutfrontPosition()
        time.sleep(speed)
        self.startPosition()
        time.sleep(speed)

        return



    def greeting(self):
        
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]

        # Primo movimento: alza il braccio per iniziare il saluto
        initial_angles = [math.radians(20.0), math.radians(-21.4), math.radians(69.0), math.radians(48.0), math.radians(-45.0), 0.9]
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

    def saymove(self):
        
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]

        # Primo movimento: alza il braccio per iniziare il saluto
        initial_angles = [math.radians(20.0), math.radians(-20), math.radians(74.0), math.radians(48.0), math.radians(100.0), 0.9]
        # initial_angles = [0.2, -0.3, 1.0, 0.5, 0.3]
        self.motion_service.angleInterpolation(names, initial_angles, [1.0]*6, True)
        
        # Movimenti ripetuti del braccio
        for i in range(6):  # Numero di scuotimenti
            time.sleep(0.5)
            if i % 2 == 0:
                self.motion_service.setAngles("RShoulderRoll", math.radians(-20), 1.0)
            else:
                self.motion_service.setAngles("RShoulderRoll", math.radians(-30), 1.0)

        # # Riporta il braccio nella posizione neutra
        neutral_angles = [1.4, 0.15, 1.0, 0.5, 0.3, 0.5]  # Posizione neutra per il braccio destro
        self.motion_service.angleInterpolation(names, neutral_angles, [1.0]*6, True)

        return


    def calm_stand(self):
        names = ["RElbowRoll","RElbowYaw", "RHand", "RShoulderPitch", "RShoulderRoll", "RWristYaw", "LElbowRoll","LElbowYaw", "LHand", "LShoulderPitch", "LShoulderRoll", "LWristYaw"]

        initial_angles = [math.radians(88.0), math.radians(86.0), 0.97, math.radians(50.0), math.radians(-2.0),  math.radians(-70.0), math.radians(-88.0), math.radians(-86.0), 0.97, math.radians(26.0), math.radians(2.0),  math.radians(70.0)]
        self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        # initial_angles = [math.radians(36.0), math.radians(70.0), 0.50, math.radians(-47.0), math.radians(-2.0),  math.radians(17.2), math.radians(-36.0), math.radians(-80.0), 0.50, math.radians(-47.0), math.radians(2.0),  math.radians(17.0)]
        # self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        # initial_angles = [math.radians(68.0), math.radians(70.0), 0.50, math.radians(26.0), math.radians(-2.0),  math.radians(17.2), math.radians(-68.0), math.radians(-80.0), 0.50, math.radians(26.0), math.radians(2.0),  math.radians(17.0)]
        # self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        # initial_angles = [math.radians(36.0), math.radians(70.0), 0.50, math.radians(-47.0), math.radians(-2.0),  math.radians(17.2), math.radians(-36.0), math.radians(-80.0), 0.50, math.radians(-47.0), math.radians(2.0),  math.radians(17.0)]
        # self.motion_service.angleInterpolation(names, initial_angles, [0.7]*12, True)

        return
    
    def wrong_log_in_stand(self):
        names = ["LElbowRoll","LElbowYaw", "LHand", "LShoulderPitch", "LShoulderRoll", "LWristYaw"]

        initial_angles = [math.radians(88.0), math.radians(86.0), 0.97, math.radians(50.0), math.radians(-2.0),  math.radians(-70.0), math.radians(-88.0), math.radians(-86.0), 0.97, math.radians(26.0), math.radians(2.0),  math.radians(70.0)]
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
    


