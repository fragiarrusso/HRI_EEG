##accensione del robot
import os
import sys
project_folder = os.path.dirname(os.path.abspath(__file__))
print("Current folder:", project_folder)
sys.path.append(project_folder)
from Peripherals.video_audio import *
from Peripherals.audio import *
from Peripherals.camera import *
from Peripherals.media import *
from SpeechRecognition.speechRecognition import SentimentAnalysis
from Utils.constants import *
from Robot.robotCommunicator import robotCommunicator
from Knowledge.shoot import *
import time
status="STAND BY"
human_here=False
lets_play=False
selected_game=None
user=None
stop_playing=False
sentimentAnalysis=SentimentAnalysis()
while True:
    if status is "STAND BY":
        recordAudio(3, filename="./media/stand_by.wav")
        response=sentimentAnalysis.speech_to_text("./media/stand_by.wav")
        if response is not "": 
            human_here= True
        #captureVideo(3, filename='./media/stand_by.avi')
        #oppure toccare lo shermo
        # mando questi audio e video da qualche parte per capire se c'è qualcuno
        if human_here:
            status="HAND SHAKING"
    
    if status is "HAND SHAKING":
        robotCommunicator.move("shield") ##da fare prima questo per attirare l'attenzione
        time.sleep(1)
        robotCommunicator.say("Do you wanna play?")
        recordAudio(3, filename="./media/hand_shaking.wav")
        response=sentimentAnalysis.speech_to_text("./media/hand_shaking.wav")
        if response != '':
            rating=sentimentAnalysis.analyze_sentiment(response)
            if rating[0]['label'] >=SENTIMENT_RATE['3 stars']: 
                lets_play= True
        
        else:
            # socket listening for screen touch
            # vedi modo per mettere timeout (modo easy - manda mex al fe, e fe fa timer)
            print()

        # prendere da tastiera il yes or no
        if lets_play:
            status="LOGGING"
        else:
            robotCommunicator.say("See you soon")
            status="STAND BY"
            time.sleep(10)

    if status is "LOGGING":
        if user is None:
            robotCommunicator.move("boh qualcosa") ##da fare prima questo per attirare l'attenzione
            time.sleep(1)
            robotCommunicator.say("Insert your name?") #troppo difficile fare riconoscimento facciale
        # notify fe to change screen to login
        # waiting socket to send username
        # eseguire funzioni di loginUser in webserver.py

        user="io" #viene chiesto di loggarsi
        status="SELECTING GAME"

    if status is "SELECTING GAME":
        #notify fe to change to choose game screen
        # waiting socket to send game choice

        robotCommunicator.say("What's game do you wanna play?")
        selected_game="TRIS" #viene chiesto a cosa vuole giocare
        status= "LETS PLAY"
    
    if status is "LETS PLAY":
        if selected_game is "TRIS":
            # notify fe to change to tris page
            # wait for the fe to send winner
            status="END GAME"
            #qua cosa ci mettiamo?
        if selected_game is "SHOOT":
            shootgame=ShootGame(user)
            shootgame.game()
            status="END GAME"
    
    if status is "END GAME":
        ##gestiamo il gioco
        robotCommunicator.say("Do you wanna stop?")
        recordAudio(3, filename="./media/stop_playing.wav")
        response=sentimentAnalysis.speech_to_text("./media/stop_playing.wav")
        rating=sentimentAnalysis.analyze_sentiment(response)
        if rating[0]['label'] >=SENTIMENT_RATE['3 stars']:
            stop_playing=True
        else:
            status = "SELECTING GAME"
        if stop_playing:
            robotCommunicator.move("salutare") ##da fare prima questo per attirare l'attenzione
            time.sleep(1)
            robotCommunicator.say("See you soon")
            status="SALUTANDO"
            lets_play=False
    if status is "SALUTANDO":
        status="STAND BY"
        human_here=False
        selected_game=None
        user=None
        stop_playing=False
        time.sleep(10)    