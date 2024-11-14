import pyaudio
import wave
import keyboard
import os
import sys

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

FORMAT = pyaudio.paInt16  # Formato dei dati audio
CHANNELS = 2
RATE = 44100  # Frequenza di campionamento
CHUNK = 1024  # Frames per buffer
RECORD_SECONDS = 5  # Durata della registrazione
WAVE_OUTPUT_FILENAME = "file_output.wav"

def recordAudio(max_duration, filename="./media/file_output.wav"):
    audio = pyaudio.PyAudio()

    # Inizio registrazione
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print(f"recording {filename} ...")
    frames = []

    for i in range(0, int(RATE / CHUNK * max_duration)):
        data = stream.read(CHUNK)
        frames.append(data)

        # Comment this line if used on linux
        if keyboard.is_pressed('q'):  # Controlla se il tasto 'q' è stato premuto
            print("Registrazione interrotta")
            break

    print("finished recording")

    # Stop registrazione
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Salvataggio del file registrato
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return 

if __name__ == '__main__':
    recordAudio(10)