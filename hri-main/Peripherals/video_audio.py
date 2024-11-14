import cv2
import pyaudio
import wave
import threading
import numpy as np
import os
import sys

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

# Parametri di registrazione
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
VIDEO_FOURCC = cv2.VideoWriter_fourcc(*'XVID')
VIDEO_OUT = "output.avi"
AUDIO_OUT = "output.wav"
RECORD_SECONDS = 5
FRAME_SIZE = CHUNK * CHANNELS
NUM_FRAMES = int(RATE / CHUNK * RECORD_SECONDS)

# Inizializza l'audio
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
frames = []

# Funzione per catturare l'audio
def capture_audio():
    print("Recording audio...")
    for _ in range(0, NUM_FRAMES):
        data = stream.read(CHUNK)
        frames.append(data)

# Inizializza il video
cap = cv2.VideoCapture(0)
video_writer = cv2.VideoWriter(VIDEO_OUT, VIDEO_FOURCC, 20.0, (640, 480))

# Funzione per catturare il video
def capture_video():
    print("Recording video...")
    start_time = cv2.getTickCount()
    while (cv2.getTickCount() - start_time)/cv2.getTickFrequency() < RECORD_SECONDS:
        ret, frame = cap.read()
        if not ret:
            break
        video_writer.write(frame)
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Crea e avvia i thread per audio e video
audio_thread = threading.Thread(target=capture_audio)
video_thread = threading.Thread(target=capture_video)
audio_thread.start()
video_thread.start()

# Attendi il completamento dei thread
audio_thread.join()
video_thread.join()

# Salva e chiude i file di audio e video
stream.stop_stream()
stream.close()
audio.terminate()

wf = wave.open(AUDIO_OUT, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

video_writer.release()
cv2.destroyAllWindows()
