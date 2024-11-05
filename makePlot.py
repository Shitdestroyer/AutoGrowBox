import matplotlib.pyplot as plt
import csv
import numpy as np
from datetime import datetime
from io import BytesIO
from GrowStates import modi_data

def make_plot(modus):

	# Listen für die x- und y-Werte initialisieren
	time_values = []
	temp_values = []
	hum_values = []

	# Datei öffnen und Daten lesen
	with open('session_data.csv', 'r') as file:
		# CSV-Datei lesen
		csv_reader = csv.DictReader(file)

		# Überprüfen, ob die CSV-Datei Daten enthält
		if not csv_reader.fieldnames:
			print("Die CSV-Datei enthält keine Daten.")
		else:
			# Spaltenüberschriften ausgeben
			#print("Spaltenüberschriften:", csv_reader.fieldnames)
			pass

		for row in csv_reader:
			try:
				date_time = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
				time_values.append(date_time)
				temp_values.append(row['temp'])
				hum_values.append(row['humidity'])
			except ValueError:
				try:
					next(csv_reader)
				except StopIteration:
					print('Es sind (noch?) keine Werte vorhanden min. 2-3 nötig')

	if time_values:
		# Bereinige die temp1-Werte und wandele sie in Fließkommazahlen um
		temp_values = [float(value.strip(" ['")) for value in temp_values]
		hum_values = [float(e.replace("'", "").replace("[", "").replace("]", "")) for e in hum_values]

		#Werte auf die letzten 1200 beschränken (5s * 1200 = 60min)
		plotlaenge = -720
		temp_values = temp_values[plotlaenge:]
		time_values = time_values[plotlaenge:]
		hum_values = hum_values[plotlaenge:]

		lastest_time_value = time_values[-1]
		time_steps = []
		for tv in time_values:
			#time_step = time_values[i+10] - time_values[i]
			#print(time_step)
			time_steps.append(str(lastest_time_value - tv))


		minT_array = [modi_data[modus]['minT']] * len(time_steps)
		maxT_array = [modi_data[modus]['maxT']] * len(time_steps)
		minH_array = [modi_data[modus]['minH']] * len(time_steps)
		maxH_array = [modi_data[modus]['maxH']] * len(time_steps)


		#Plot für temp1 erstellen
		plt.figure(figsize=(15, 6))  # Breite, Höhe

		plt.plot([0,0], [15,90], color='black')

		plt.plot(time_steps, minT_array, color='#F5A9A9', linestyle = '--')
		plt.plot(time_steps, maxT_array, color='#610B0B', linestyle = '--')
		plt.plot(time_steps, minH_array, color='#A9A9F5', linestyle = '--')
		plt.plot(time_steps, maxH_array, color='#08088A', linestyle = '--')

		plt.plot(time_steps, temp_values, color='red')
		plt.plot(time_steps, hum_values, color='blue')
		x_ticks = time_steps[::100]
		plt.xticks(x_ticks)
		plt.xlabel('Zeit')
		plt.ylabel('Temperatur[°C]     relative Feuchtigkeit[%]')
		plt.title('Sensorwerte' + ' [' + modus + ']')
		plt.grid(True)
		plt.savefig('static/plots/TempPlot.png', format='png')
		plt.close()

	return 'static/plots/TempPlot.png'




if __name__ == "__main__":
	make_plot()
