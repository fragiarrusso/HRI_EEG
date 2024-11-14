import asyncio
import websockets
import json
import os
import sys
import time

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

from Peripherals.audio import *
from Peripherals.camera import *
from Peripherals.media import *
from SpeechRecognition.speechRecognition import SentimentAnalysis
from Utils.constants import *
from Robot.robotCommunicator import robotCommunicator
from Knowledge.shoot import *
from Memory.queries import *



sentimentAnalysis=SentimentAnalysis()


async def handle_connection(websocket, path):

    status="STAND BY"
    human_here=False
    lets_play=False
    selected_game=None
    user=None
    stop_playing=False

    while True:

        if status == "STAND BY":
            recordAudio(3, filename="./media/stand_by.wav")
            response=sentimentAnalysis.speech_to_text("./media/stand_by.wav")
            print(f'transcription stand_by: {response}')

            if response != "": 
                human_here= True
            #Capture video da mettere nel report con funzionalità Pepper ma non fattibile qui

            if human_here:
                status="HAND SHAKING"

        print(f'status: {status}')
        if status == "HAND SHAKING":
            # Rispondi al messaggio
            response = json.dumps({
                "action": "change_page",
                "page": "want_play"
            })
            await websocket.send(response)
            await asyncio.sleep(0)

            robotCommunicator.move("greeting") ##da fare prima questo per attirare l'attenzione
            time.sleep(1)
            robotCommunicator.say("Do you wanna play?")

            recordAudio(3, filename="./media/hand_shaking.wav")
            response=sentimentAnalysis.speech_to_text("./media/hand_shaking.wav")
            print(f'transcription_hand_shake: {response}')

            if response != '':
                rating=sentimentAnalysis.analyze_sentiment(response)
                if SENTIMENT_RATE[rating[0]['label']] >=SENTIMENT_RATE['3 stars']:
                    print(f'lets_play') 
                    lets_play= True
            
            else:
                # prendere da tastiera il yes or no
                # socket listening for screen touch
                # vedi modo per mettere timeout (modo easy - manda mex al fe, e fe fa timer)
                print("Waiting for the user to click on the screen...")

                message = await websocket.recv()  # Aspetta un messaggio dal client
                print(f"Received message: {message}")

                if message['play']:
                    lets_play= True
                else:
                    lets_play= False
            
            if lets_play:
                status="LOGGING"
            else:
                print("See you soon!")

                response = json.dumps({
                    "action": "change_page",
                    "page": "welcome"
                })
                await websocket.send(response)
                await asyncio.sleep(0)

                robotCommunicator.say("See you soon")
                status="STAND BY"
                time.sleep(10)

        if status == "LOGGING":

            if user is None:
                

                robotCommunicator.move("boh qualcosa") ##da fare prima questo per attirare l'attenzione
                time.sleep(1)
                robotCommunicator.say("Insert your name?") #troppo difficile fare riconoscimento facciale
            
            # notify fe to change screen to login
            response = json.dumps({
                    "action": "change_page",
                    "page": "login"
            })
            await websocket.send(response)

            # waiting socket to send username
            message = await websocket.recv()  # Aspetta un messaggio dal client
            message = json.loads(message)
            print(f"Received message: {message}")

            # eseguire funzioni di loginUser in webserver.py
            user=message['username']
            result = createUser(user)

            if result['new_account'] is True:
                robotCommunicator.say("Welcome to the game, "+user)
                robotCommunicator.say("You can play a game of shoot or tic tac toe")
            #ecc...


             #viene chiesto di loggarsi
            # user="io" #viene chiesto di loggarsi
            status="SELECTING GAME"

        if status == "SELECTING GAME":
            #notify fe to change to choose game screen
            response = json.dumps({
                    "action": "change_page",
                    "page": "choose_game"
            })
            robotCommunicator.say("What game do you wanna play?")

            await websocket.send(response)

            # waiting socket to send game choice
            message = await websocket.recv()  # Aspetta un messaggio dal client
            message = json.loads(message)
            print(f"Received message: {message}")

            # selected_game="TRIS" #viene chiesto a cosa vuole giocare
            selected_game = message['game'] #viene chiesto a cosa vuole giocare
            status= "LETS PLAY"
        
        if status == "LETS PLAY":
            if selected_game == "tris":
                # notify fe to change to tris page
                #notify fe to change to choose game screen
                robotCommunicator.say("Let's play tris!")

                response = json.dumps({
                        "action": "change_page",
                        "page": "tris"
                })
                await websocket.send(response)

                # wait for the fe to send winner
                winner = await websocket.recv()  # Aspetta un messaggio dal client
                print(f"Received message: {winner}")

                status="END GAME"

            if selected_game == "shoot":
                robotCommunicator.say("Let's play shoot")

                shootgame=ShootGame(user)
                shootgame.game()
                status="END GAME"
        
        if status == "END GAME":
            ##gestiamo il gioco
            print("Do you want to stop?")

            robotCommunicator.say("Do you wanna stop?")

            recordAudio(3, filename="./media/stop_playing.wav")
            response=sentimentAnalysis.speech_to_text("./media/stop_playing.wav")
            print(f'transcription stop_play: {response}')

            rating=sentimentAnalysis.analyze_sentiment(response)
            if SENTIMENT_RATE[rating[0]['label']] >=SENTIMENT_RATE['3 stars']:
                print("Stop_playing...")
                stop_playing=True
                response = json.dumps({
                    "action": "change_page",
                    "page": "welcome"
                })
                await websocket.send(response)
                await asyncio.sleep(0)

            else:
                status = "SELECTING GAME"

            if stop_playing:

                robotCommunicator.move("salutare") ##da fare prima questo per attirare l'attenzione
                time.sleep(1)
                robotCommunicator.say("See you soon")
                
                status="SALUTANDO"
                lets_play=False

        if status == "SALUTANDO":
            status="STAND BY"
            human_here=False
            selected_game=None
            user=None
            stop_playing=False
            time.sleep(10)   



async def main():
    # 'websockets.serve' gestisce il ciclo di ascolto delle connessioni
    # Ascolta su localhost sulla porta 23456
    async with websockets.serve(handle_connection, "localhost", 23456):
        print("Server started at ws://localhost:23456")
        await asyncio.Future()  # Mantiene il server in esecuzione

if __name__ == "__main__":
    asyncio.run(main())
