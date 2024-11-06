import time
import os
import csv
from datetime import datetime
from pathlib import Path
received_path = Path.home() / 'AutoGrowBox/data/received_data.csv'      #Dateipfad zu received_data, welche alle empfangenen Werte aufzeichnet. Also echt alle
session_path = Path.home() / 'AutoGrowBox/data/session_data.csv'        #speichiert nur die Werte der letzten Stunde

def header_csv(sp=session_path, rp=received_path):
        # Neue Zeile, die in die CSV-Datei geschrieben werden soll
        new_first_line = 'timestamp,temp,humidity'

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

def manageData(sp=session_path, rp=received_path):
        filtered_s = []
        filtered_r = []
        with open(sp, 'r') as sfile, open(rp, 'r') as rfile:
                sreader = csv.reader(sfile)
                rreader = csv.reader(rfile)
                
                try:
                        #delete all data points which years start with a different number than '20' (needs to get fixed in 76 years)
                        #fixing bad code with more code should be avoided
                        for row in sreader:
                                row_length = 0
                                for cell in row:
                                        row_length += len(cell)
                                print(row_length)
                                if (row[0].startswith('20') and row_length == 37) or (row[0] == 'timestamp' and row_length == 21):
                                        filtered_s.append(row)
                        for row in rreader:
                                if row[0].startswith('20') or row[0] == 'timestamp':
                                        filtered_r.append(row)
                
                        #compare the first and last data point in session_data 
                        format = '%Y-%m-%d %H:%M:%S'
                        s_beg = datetime.strptime(filtered_s[1][0], format)     #first data point gets stored
                        for ss in range(1, len(filtered_s)):                             #iterating through the data, until 
                                print(filtered_s[ss][0], '   ', ss)                      
                                s_end = datetime.strptime(filtered_s[ss][0], format)
                                s_diff = s_end - s_beg                                  #time difference is 
                                print(s_diff)
                                if round(s_diff.total_seconds() / 3600, 2) >= 1:        #greater than 1 hour
                                        filtered_s = filtered_s[:ss]                    #cut off the rest of the list
                                        break
                except IndexError:
                        print('manageData: session_data or received_data is still empty')
                        pass
                
        with open(sp, 'w', newline='') as sfile, open(rp, 'w', newline='') as rfile:
                swriter = csv.writer(sfile)
                swriter.writerows(filtered_s)
                rwriter = csv.writer(rfile)
                rwriter.writerows(filtered_r)
                
        return('session_data and received_data cleaned')

if __name__ == '__main__':
        #header_csv()
        manageData()
