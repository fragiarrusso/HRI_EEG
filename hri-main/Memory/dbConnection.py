import mysql.connector
import os
import sys

project_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_folder)

from Memory.config import dbConfig

# Stabilire la connessione
dbConnection = mysql.connector.connect(**dbConfig)

# Creare un cursore
cursor = dbConnection.cursor(dictionary=True)



