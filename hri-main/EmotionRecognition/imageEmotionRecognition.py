from deepface import DeepFace
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
from fer import FER
import cv2

def getEmotionFromImgFer(path):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB
    # Initialize the detector
    detector = FER(mtcnn=True)

    # Detect emotions
    emotions = detector.detect_emotions(img)
    print(emotions)

    if len(emotions) == 0:
        return 'neutral'
    
    emotions_dict = emotions[0]['emotions']
    dominant_emotion = max(emotions_dict, key=emotions_dict.get)
    return dominant_emotion

def getEmotionFromImg(path):
    #set enforce_detection = True if you want to be sure to get a face!
    result = DeepFace.analyze(img_path=path, actions=['emotion'], enforce_detection=False)
    return result[0]['dominant_emotion']

if __name__ == '__main__':
    result = DeepFace.analyze(img_path="./face.jpg", actions=['emotion'])
    print(result)

    
