import time
import os
import csv
from pathlib import Path
received_path = Path.home() / 'AutoGrowBox/data/received_data.csv'      #Dateipfad zu received_data, welche alle empfangenen Werte aufzeichnet. Also echt alle
session_path = Path.home() / 'AutoGrowBox/data/session_data.csv'        #speichiert nur die Werte der letzten Stunde

def header_csv(rp=received_path, sp=session_path):
        print('giving head...')
        # Neue Zeile, die in die CSV-Datei geschrieben werden soll
        new_first_line = 'timestamp,temp,humidity'
        
        print(rp, '     ', sp)
        
        # Öffne die CSV-Datei im Schreibmodus
        with open(rp, 'r+') as file1, open(sp, 'r+') as file2:

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

def manageSessionData(sp=session_path):
        #delete all data points which years start with a different number than '20' (needs to get fixed in 76 years)
        filtered_data = []
        with open(sp, 'r+') as sfile:
                sreader = csv.reader(sfile)
                for row in sreader:
                        if row[0].startswith('20') or row[0] == 'timestamp':
                                filtered_data.append(row)
        with open(sp, 'w', newline='') as sfile:
                swriter = csv.writer(sfile)
                swriter.writerows(filtered_data)
                
        #session_data auf 1 Stunde verkürzen
        
               
manageSessionData()
