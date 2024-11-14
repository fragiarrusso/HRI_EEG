from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, pipeline
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import librosa
import os
import sys

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

from Utils.constants import *
from Peripherals.audio import recordAudio

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

if os.path.exists(PATH_SANALYSIS_WEIGHTS):
    # Carica il tokenizer e il modello dalla directory locale
    tokenizer = AutoTokenizer.from_pretrained(PATH_SANALYSIS_WEIGHTS)
    model_sentiment = AutoModelForSequenceClassification.from_pretrained(PATH_SANALYSIS_WEIGHTS)
else:
    os.makedirs(PATH_SANALYSIS_WEIGHTS)

    model_name = 'nlptown/bert-base-multilingual-uncased-sentiment'

    # Carica il tokenizer e il modello
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model_sentiment = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Salva il tokenizer e il modello in locale
    tokenizer.save_pretrained(PATH_SANALYSIS_WEIGHTS)
    model_sentiment.save_pretrained(PATH_SANALYSIS_WEIGHTS)


class SentimentAnalysis():
    def __init__(self) -> None:
        pass



    # # # # Funzione per convertire l'audio in testo
    def speech_to_text(self, audio_path):
        # Carica l'audio
        audio, rate = librosa.load(audio_path, sr=16000)
        input_values = processor_stt(audio, return_tensors="pt", padding="longest").input_values  # Trasforma l'audio per il modello

        # Usa il modello per la predizione
        with torch.no_grad():
            logits = model_stt(input_values).logits

        # Decodifica i logits per ottenere il testo trascritto
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor_stt.decode(predicted_ids[0])
        return transcription

    def analyze_sentiment(self, text):
        """Analizza il sentiment del testo utilizzando Hugging Face Transformers."""
        sentiment_analyzer = pipeline('sentiment-analysis', model=model_sentiment, tokenizer=tokenizer)
        return sentiment_analyzer(text)


if __name__ == '__main__':
    sentimentAnalysis = SentimentAnalysis()

    # recordAudio(5, PATH_AUDIO)

    # Esegui la conversione
    transcription = sentimentAnalysis.speech_to_text(PATH_AUDIO)
    print("Transcription:", transcription)

    # transcription = "shit!"
    # transcription = "Great you are a piece of shit!"
    # transcription = "Noo, this is not possible!"
    # transcription = "This is a good product, but sometimes it breaks, could be better!"
    # transcription = ""

    # Analizza il sentiment del testo trascritto
    sentiment = sentimentAnalysis.analyze_sentiment(transcription)
    print(f"Sentiment: {sentiment}")

    # from transformers import AutoModelForSequenceClassification

    # # Carica il modello, assicurati di avere il percorso giusto o il nome del modello
    # model = AutoModelForSequenceClassification.from_pretrained(PATH_SANALYSIS_WEIGHTS)

    # # Accedi alle etichette dal modello
    # labels = model.config.id2label
    # print("Labels available in the model:", labels)
