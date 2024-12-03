import pyaudio
import wave
import os
import sys
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch
import librosa

FORMAT = pyaudio.paInt16  # Formato dei dati audio
CHANNELS = 2
RATE = 16000  # Frequenza di campionamento
CHUNK = 1024  # Frames per buffer
RECORD_SECONDS = 5  # Durata della registrazione
WAVE_OUTPUT_FILENAME = "file_output.wav"
PATH_STT_WEIGHTS = './STTModelWeights'

if os.path.exists(PATH_STT_WEIGHTS):
    processor_stt = Wav2Vec2Processor.from_pretrained(PATH_STT_WEIGHTS)
    model_stt = Wav2Vec2ForCTC.from_pretrained(PATH_STT_WEIGHTS)
else:
    os.makedirs(PATH_STT_WEIGHTS)

    processor_stt = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model_stt = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

    #Alternative also for italian language: facebook/wav2vec2-large-xlsr-53-italian
    
    model_stt.save_pretrained('./STTModelWeights')
    processor_stt.save_pretrained('./STTModelWeights')

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

# # # # Funzione per convertire l'audio in testo
def speech_to_text(audio_path):
    # Carica l'audio
    audio, _ = librosa.load(audio_path, sr=16000)
    input_values = processor_stt(audio, return_tensors="pt", padding="longest", sampling_rate=16000).input_values  # Trasforma l'audio per il modello

    # Usa il modello per la predizione
    with torch.no_grad():
        logits = model_stt(input_values).logits

    # Decodifica i logits per ottenere il testo trascritto
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor_stt.decode(predicted_ids[0])
    return transcription

def get_response(duration=3):
    recordAudio(duration, filename="./media/test.wav")
    response=speech_to_text("./media/test.wav")
    return response

if __name__ == '__main__':
    while True:
        print('nel while')
        response = get_response()
        print('response: '+response)
        if 'STOP' in response or 'FERMA' in response:
            print('stopped')
            break