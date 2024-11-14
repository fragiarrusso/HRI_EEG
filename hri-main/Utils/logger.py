import logging
import os
import sys

# Get the directory containing the current file
project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("Current folder:", project_folder)

sys.path.append(project_folder)


logger = logging.getLogger('logger1')
logger.setLevel(logging.INFO)  # Imposta il livello di log a ERROR
handler1 = logging.StreamHandler()  # Invia i log a stdout
formatter1 = logging.Formatter('%(levelname)s: %(message)s')
handler1.setFormatter(formatter1)
logger.addHandler(handler1)

# handler1_2 = logging.FileHandler('logger1.log')  # Salva i log in un file
# logger.addHandler(handler1_2)
