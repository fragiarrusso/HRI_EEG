# import torch
# print(torch.cuda.is_available())
import numpy as np
# rng = np.random.default_rng(123)

# print(rng.integers(low=0, high=5))
# print(rng.integers(low=0, high=5))
# print(rng.integers(low=0, high=5))
# # print(rng.random())
# # print(rng.random())


# from fer import FER
# import matplotlib.pyplot as plt
# import cv2
# import time

# # Load your image
# image_path = './face.jpg'
# img = cv2.imread(image_path)
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB

# # Initialize the detector
# detector = FER(mtcnn=True)

# # Detect emotions
# emotions = detector.detect_emotions(img)
# print(emotions)

# # Display the image and the bounding box with emotions
# for result in emotions:
#     (x, y, w, h) = result['box']
#     emotions_dict = result['emotions']
#     dominant_emotion = max(emotions_dict, key=emotions_dict.get)
#     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#     cv2.putText(img, dominant_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

# # Show the result
# plt.figure(figsize=(10, 6))
# plt.imshow(img)
# plt.show()
# time.sleep(5)
print(np.random.uniform(low=8, high=2))