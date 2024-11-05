from flask import Flask
from flask import render_template
import RPi.GPIO as rpi
import time

app= Flask(__name__)

led1,led2,led3= 26, 16, 6

rpi.setwarnings(False)
rpi.setmode(rpi.BCM)
rpi.setup(led1, rpi.OUT)
rpi.setup(led2, rpi.OUT)
rpi.setup(led3, rpi.OUT)
rpi.output(led1, 0)
rpi.output(led2, 0)
rpi.output(led3, 0)
print("Done")

@app.route('/')
def index():
    return render_template('webpage.html')

@app.route('/A')
def led1on():
    rpi.output(led1,1)
    return render_template('webpage.html')

@app.route('/a')
def led1off():
    rpi.output(led1,0)
    return render_template('webpage.html')

@app.route('/B')
def led2on():
    rpi.output(led2,1)
    return render_template('webpage.html')

@app.route('/b')
def led2off():
    rpi.output(led2,0)
    return render_template('webpage.html')

@app.route('/C')
def led3on():
    rpi.output(led3,1)
    return render_template('webpage.html')

@app.route('/c')
def led3off():
    rpi.output(led3,0)
    return render_template('webpage.html')

if __name__=="__main__":
    print("Start")
    app.run(debug=True, host='0.0.0.0', port=5001)
