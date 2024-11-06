#!/usr/bin/env python3

####################################################
#GrowBox main script
#contains the flask server,
#reads the incoming data through a serial connection
#and saves the data to a csv files
####################################################

from flask import Flask, render_template, Response, send_file
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
from io import BytesIO
from time import sleep, strftime, time
import serial
import threading
import numpy as np
import datetime
from makePlot import make_plot
from manageData import header_csv, manageData
import os
import sys
from pathlib import Path
AGB = Path.home() / 'AutoGrowBox'
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
import csv
import ast
from GrowStates import modi_data
import requests

with open(AGB / 'data/session_data.csv', 'w', newline='') as sessionlog:	#empty session_data
	pass

plt.ion()
x = []
y = []

# Setze den GPIO-Modus
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Definiere den GPIO-Pin
pins = {
	26 : {'name' : 'GPIO 26', 'state' : GPIO.HIGH, 'use' : 'Licht'},		#Licht
	19 : {'name' : 'GPIO 19', 'state' : GPIO.HIGH, 'use' : 'Luefter'},		#Lüfter
	13 : {'name' : 'GPIO 13', 'state' : GPIO.HIGH, 'use' : 'Ventilator'},	#Ventiltor
	6 : {'name' : 'GPIO 6', 'state' : GPIO.HIGH, 'use' : 'none'}
	}

# Konfiguriere den Pin als Ausgang
for pin in pins:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)

# read und write-Funktionen, um die current_mode zu speichern
def write_mode_to_file(m):													#Funktion zum hinterlegen der Phase (Modus) in einem Dokument
	if m == "Keimung" or "Wachstum" or "Blüte" or "Trocknung":		#verhindert, dass Scheiße (Faveicon.ico) in Datei gespeichert wird
		with open(AGB / 'currently_selected_mode.txt', 'w') as file:		#schreiben
			file.write(m)
def read_mode_from_file():
	with open(AGB / 'currently_selected_mode.txt', 'r') as file:
		m = file.read().strip()
	return m

# zu Beginn des Codes wird die current_mode aus der letzten Sitzung gelesen:
current_mode = read_mode_from_file()
print(f'current_mode : {current_mode}')

# Kontrolliert die GPIOs basierend auf den Vorgaben in GrowStates.py und den definierten Konstanten (GROßBUCHSTABEN)
def SDcontroller(hour, minute, second, hum, tem, current_mode=current_mode):

	### Lichtkontrolle
	if modi_data[current_mode]['lightON'] == 'OFF':
		GPIO.output(26, GPIO.HIGH)	# Licht aus, wenn Licht off ist (ja genau)
	else:
		turnONhour = modi_data[current_mode]['lightON']		# turnON und turOFF Zeiten von GrowStates.py bekommen
		turnOFFhour = modi_data[current_mode]['lightOFF']	# dann je nachdem an oder aus schalten

		if hour >= int(turnONhour) and hour < int(turnOFFhour):
			GPIO.output(26, GPIO.LOW)
		else:
			GPIO.output(26, GPIO.HIGH)

	### Lüfterkontrolle
	average_hum = (modi_data[current_mode]['minH'] + modi_data[current_mode]['maxH'])/2
	if hum < average_hum:
		GPIO.output(19, GPIO.HIGH)
	elif hum > average_hum:
		GPIO.output(19, GPIO.LOW)

	### Ventilatorkontrolle
	#if GPIO.input(19) == 0:
	#	GPIO.output(13, GPIO.HIGH)
	#else:
	#	GPIO.output(13, GPIO.LOW)
	GPIO.output(13, GPIO.LOW)

	# Update [print alle wichtigen Infos und update pins-Dict]
	print()
	print('-------------------')
	print('   Zeit ',hour,':',minute,':',second)
	print('   ',hum,'%rel   ',tem,'°C')
	print('   MODUS : ' + current_mode)
	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)
		print( '   ' + pins[pin]['name'] + ' - ' + pins[pin]['use'] + ' : ' + str(pins[pin]['state']) )
	print('-------------------')

def write_data(data):
	# Öffne eine Datei im Schreibmodus, um die empfangenen Daten zu speichern
	with open(AGB / 'data/received_data.csv', 'a', newline='') as log, open(AGB / 'data/session_data.csv', 'a', newline='') as sessionlog:
		ses_writer = csv.writer(sessionlog)
		rec_writer = csv.writer(log)
		for element in data:
			timestamp, values = element.split(', ', 1)
			values = ast.literal_eval(values)
			temp = values[0]
			humi = values[1]
			ses_writer.writerow([timestamp, temp, humi])
			rec_writer.writerow([timestamp, temp, humi])

# Funktion zum kontinuierlichen Lesen von Daten aus der seriellen Schnittstelle
def read_serial(current_mode=current_mode):
	last_minute = ''	#muss so

	save_data = []

	while True:
		current_mode = read_mode_from_file()

		sleep(1)

		if ser.in_waiting > 0:
			data = ser.readline().decode().strip()
			print(">>>Received:", str(data))
			if len(data.split()) == 4:
				if ([data.split()[0], data.split()[3]]) == ['START', 'STOP']:
					data_to_write = f'{strftime("%Y-%m-%d %H:%M:%S")}, {data.split()[1:3]}'
					
					save_data.append(data_to_write)					#temporarily save in list

					now_minute = data_to_write[:16]					#get the current minute
					if now_minute != last_minute:					#once a minute
						write_data(save_data)						#write collectei data to file
						save_data = []								#empty list
						last_minute = now_minute

					# Hier kannst du weitere Verarbeitung der empfangenen Daten durchführen
			elif str(data) == 'Sensormodul startklar':
				pass

			try:
				rec_hou = int(data_to_write[11:13])	# erhaltene Stunde
				rec_min = int(data_to_write[14:16])	# "	    Minute
				rec_sec = int(data_to_write[17:19])	# usw
				rec_tem = int(data_to_write[23:25]) + round(int(data_to_write[26:28])/100)
				rec_hum = int(data_to_write[32:34])

				SDcontroller(rec_hou, rec_min, rec_sec, rec_hum, rec_tem)
			except UnboundLocalError as e:
				print('noch keine Daten erhalten (data_to_write noch nicht definiert)')

# Öffne die serielle Schnittstelle, 9600 ist die Baudrate
try:
	ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
	print('serielle Verbindung hergestellt')
except serial.SerialException:
	try:
		ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
		print('serielle Verbindung hergestellt')
	except serial.SerialException:
		print('keine Verbindung über USB0 oder USB1')
		pass

if ser:
	ser.flush()

# Starte den Thread zum Lesen von Daten aus der seriellen Schnittstelle
serial_thread = threading.Thread(target=read_serial)
serial_thread.daemon = True
serial_thread.start()

# Dummy Messdaten
x = np.arange(0, 10, 0.1)
y = np.sin(x)

PLOT_FOLDER = os.path.join('static', 'plots')

app= Flask(__name__, static_url_path= '/static')
app.config['PLOT_FOLDER'] = PLOT_FOLDER

@app.route('/plot')
def plot():
	try:
		plot_path = make_plot(current_mode)
		return send_file(plot_path, mimetype='image/png')
	except KeyError:
		header_csv()    #ersetze die erste Zeile mit den Spaltenbezeichnungen
		plot_path = make_plot(current_mode)
		return send_file(plot_path, mimetype='image/png')

@app.route('/')
@app.route('/index')
def index():
	#full_filename = os.path.join(app.config['PLOT_FOLDER'], 'TempPlot.png')
	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)

	templateData = {
		'pins' : pins,
		'mode' : current_mode
	}
	return render_template('webpage.html', **templateData) #, user_image = full_filename)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def relay(changePin, action):
	# Convert the pin from the URL into an integer:
	changePin = int(changePin)
	# Get the device name for the pin being changed:
	deviceName = pins[changePin]['name']
	# If the action part of the URL is "on," execute the code indented below:
	if action == "on":
		# Set the pin high:
		GPIO.output(changePin, GPIO.LOW)
		# Save the status message to be passed into the template:
		message = "Turned " + deviceName + " on."
	if action == "off":
		GPIO.output(changePin, GPIO.HIGH)
		message = "Turned " + deviceName + " off."

	# For each pin, read the pin state and store it in the pins dictionary:
	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)

	# Along with the pin dictionary, put the message into the template data dictionary:
	templateData = {
		'pins' : pins,
		'mode' : current_mode
	}
	return render_template('webpage.html', **templateData)

@app.route("/<changeMode>")
def modus(changeMode, current_mode=current_mode):
	current_mode = changeMode
	write_mode_to_file(changeMode)
	for pin in pins:
		pins[pin]['state'] = GPIO.input(pin)

	templateData = {
		'pins' : pins,
		'mode' : changeMode
	}
	return render_template('webpage.html', **templateData)

if __name__=="__main__":
	print("Start")
	app.run(debug=True, use_reloader=False, host='0.0.0.0', port=1225)
	try:
		pass

	except KeyboardInterrupt:
		# Setze den GPIO-Status zurück und beende das Programm, wenn Strg+C gedrückt wird
		GPIO.cleanup()
		print("Programm abgebrochen")

	finally:
		# Aufräumen und GPIO zurücksetzen
		#GPIO.cleanup()
		ser.close()
