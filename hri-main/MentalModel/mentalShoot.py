import os
import sys
import time
import socket
import json

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

from Utils.constants import *
from Robot.say import *
from Peripherals.camera import getInstantShot
from EmotionRecognition.imageEmotionRecognition import getEmotionFromImgFer
from SpeechRecognition.speechRecognition import SentimentAnalysis

from Robot.robotCommunicator import robotCommunicator
from Peripherals.audio import recordAudio

class ShootInteractionHandler():

    def __init__(self) -> None:
        # self.initSocket()
        self.sentimentAnalysis = SentimentAnalysis()
        
        pass


    def levelChange(self, curr_level, new_level):
        
        message = ''
        if LEVELS[curr_level] < LEVELS[new_level]:
            message = "Great you are improving a lot! \n I will try to be better!"
        elif LEVELS[curr_level] > LEVELS[new_level]:
            message = "It seems like you still have to learn a lot... \n I will try to be softer!"
        else:
            # message = "Still a draw... Let's do another match!"
            message = ""

        robotCommunicator.say(message)
        print(message)
        return
    
    def endMatch(self, winner): 
        emotion_from_sentiment = self.handleSentiment()
        emotion = self.handleEmotion()

        emotion_avg = (EMOTION_RATE[emotion] + EMOTION_RATE[emotion_from_sentiment]) / 2

        print(f'emotion: {emotion}, avg: {emotion_avg}')

        # message = ''
        # if emotion == 'sad':
        #     message = "Oh no my friend, don't be sad, we can do a re-match!"
        #     #decreaseLevel(username)
        # elif emotion == 'happy':
        #     message = "Are you fooling me?! let's see if you are able to beat me now!"
        #     #increaseLevel(username)
        # elif emotion == 'angry':
        #     message = "Don't be angry, we can still play!"
        # else: #could be neutral, fear, surprise, disgust
        #     message = ""

        message = ''
        if emotion_avg > 3.5:
            #happy
            message = "Are you fooling me?! let's see if you are able to beat me now!"
        elif emotion_avg > 2.5 and emotion_avg <= 3.5:
            #neutral
            message = ""
        elif emotion_avg > 1.5 and emotion_avg <= 2.5:
            #angry
            if message == '':
                message = "Don't be angry, we can still play!"
        elif emotion_avg <= 1.5:
            #sad
            message = "Oh no my friend, don't be sad, we can do a re-match! I will be softer."
            
        action = ''
        if emotion_avg > 3.5 and winner == 'AI':
            #happy
            action = "strong_exultation"
        elif emotion_avg > 2.5 and emotion_avg <= 3.5 and winner == 'AI':
            #neutral
            action = "exultation"
        elif emotion_avg > 1.5 and emotion_avg <= 2.5 and winner == 'AI':
            #angry
            action = 'raise_hands'

        if message == '':
            if winner == 'ai':
                message = "I won!"
            elif winner == 'human':
                message = "Oh no i lost!"
            else:
                message = "Another Draw..."

        robotCommunicator.say(message)
        robotCommunicator.move(action)
        print(message)
        return
    
    def newUser(self, username):
        message_to_send = f"""
                {username}, these are the rules of the game: ...
            """

        robotCommunicator.say(message_to_send)
        return
    
    def handleEmotion(self):
        
        getInstantShot(PATH_FACE)
        emotion = getEmotionFromImgFer(PATH_FACE)
        return emotion

    def handleMove(self):
        return
    
    def handleSentiment(self):
        recordAudio(5, PATH_AUDIO)
        transcription = self.sentimentAnalysis.speech_to_text(PATH_AUDIO)
        rating = self.sentimentAnalysis.analyze_sentiment(transcription)

        rate = rating[0]['label']
        print(f'rate: {rate}')

        sentiment = ''
        if SENTIMENT_RATE[rate] == 1:
            sentiment = 'angry'
        elif SENTIMENT_RATE[rate] == 2:
            sentiment = 'sad'
        elif SENTIMENT_RATE[rate] == 4:
            sentiment = 'happy'
        elif SENTIMENT_RATE[rate] == 5:
            sentiment = 'happy'
        else: # rate == 3
            sentiment = 'neutral'
        return sentiment
    
if __name__ == '__main__':
    #main
    print()