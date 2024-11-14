import cv2
from deepface import DeepFace

# Funzione per avviare la webcam e riconoscere le emozioni
def detect_emotion():
    # Inizializza la webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Errore: Impossibile accedere alla webcam.")
        return

    while True:
        # Legge un frame dalla webcam
        ret, frame = cap.read()

        if not ret:
            print("Errore: Impossibile leggere il frame.")
            break

        try:
            # Analizza l'emozione nel frame corrente
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            print(f'result: {result}')
            emotion = result[0]['dominant_emotion']

            # Mostra l'emozione rilevata nel frame
            cv2.putText(frame, emotion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        except Exception as e:
            print(f"Errore durante l'analisi dell'emozione: {e}")

        # Mostra il frame con l'emozione
        cv2.imshow('Webcam Emotion Detection', frame)

        # Premere 'q' per uscire
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Rilascia la cattura e chiude le finestre
    cap.release()
    cv2.destroyAllWindows()

# Avvia la funzione di rilevamento
detect_emotion()
