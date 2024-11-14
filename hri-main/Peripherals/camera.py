import cv2
import time
import os
import sys

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

def captureVideo(max_duration=None, filename='./media/output.avi'):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Definisci il codec
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        out.write(frame)  # Salva il frame nel file
        cv2.imshow('frame', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        if max_duration is not None and (time.time() - start_time) > max_duration:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    return

def captureSingleImage():
    cap = cv2.VideoCapture(0)
    counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow('frame', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('s'):  # Premi 's' per salvare
            cv2.imwrite(f'captured_image{counter}.jpg', frame)
            print(f"Immagine {counter} salvata!")
            counter+=1

        elif cv2.waitKey(1) & 0xFF == ord('q'):  # Premi 'q' per uscire
            break

    cap.release()
    cv2.destroyAllWindows()

    return

def getInstantShot(path):
    cap = cv2.VideoCapture(0)

    counter = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        counter += 1
        if counter < 2:
            continue

        cv2.imwrite(path, frame)
        break
            
    cap.release()
    cv2.destroyAllWindows()

    return


def captureMultipleImages():
    cap = cv2.VideoCapture(0)
    frame_counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow('frame', frame)
        
        if frame_counter % 60 == 0:  # Salva un'immagine ogni 60 frame
            cv2.imwrite(f'captured_frame_{frame_counter}.jpg', frame)
            print(f"Immagine {frame_counter} salvata!")

        frame_counter += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return

if __name__ == '__main__':
    # captureVideo(10)
    # captureSingleImage()
    getInstantShot()