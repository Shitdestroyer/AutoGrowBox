import time
import os
import csv
from datetime import datetime

def manageSessionData():
	prin('hier ist nix')
	pass

def header_csv():
        print('giving head...')
        # Neue Zeile, die in die CSV-Datei geschrieben werden soll
        new_first_line = 'timestamp,temp,humidity'

        # Dateipfad zur CSV-Datei
        received_file_path = 'received_data.csv'
        session_file_path = 'session_data.csv'

        # Öffne die CSV-Datei im Schreibmodus
        with open(received_file_path, 'r+') as file1, open(session_file_path, 'r+') as file2:

                # Lese den Inhalt der Datei
                content1 = file1.readlines()
                content2 = file2.readlines()

                # Setze den Dateizeiger an den Anfang der Datei
                file1.seek(0)
                file2.seek(0)

                # Schreibe die neue erste Zeile in die Datei
                file1.write(new_first_line + '\n')
                file2.write(new_first_line + '\n')

                # Schreibe den übrigen Inhalt der Datei zurück
                for line1 in content1[1:]:
                        file1.write(line1)
                for line2 in content2[1:]:
                        file2.write(line2)
