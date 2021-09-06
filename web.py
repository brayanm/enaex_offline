from flask import Flask, render_template, request, redirect, url_for, session, json, flash, make_response, send_file, jsonify, Response
#from flask_mysqldb import MySQL
#import MySQLdb.cursors
import re
import numpy as np
import glob	
import os
from math import sin, cos, sqrt, atan2, radians, pi
import csv
from PIL import Image
from PIL import ImageDraw
import io
import base64
from numpy import copy
import pdfkit
from os.path import join
import random
import time
import math
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command, LocationGlobal
from pymavlink import mavutil
import argparse
from random import uniform
from threading import Thread, Event
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from matplotlib.figure import Figure
import datetime
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine
import cv2
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvas
import pandas as pd

# approximate radius of earth in km
R = 6373.0

app = Flask(__name__)

app.secret_key = 'ckpZQrmDFXXEkIfRYh3nxVa61ycYdoP6'


#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = ''
#app.config['MYSQL_DB'] = 'enaex3'
engine = create_engine('sqlite:///C:/Users/Dronia/Documents/enaex_bobina/db/enaex.db')
#engine = create_engine('sqlite:///D:/dronekit/dronia/db/enaex.db')

# Intialize MySQL
#mysql = MySQL(app)


global od_model

od_model = None

global vehicle
vehicle = None

global mode
mode = None

global namedb
namedb = None

global umbral_f
umbral_f = None

global umbral_a
umbral_a = None

global continue_cap
continue_cap = None

global max_frec
max_frec = None

global max_amp
max_amp = None

global max_frec12_7
max_frec12_7 = None

global max_amp12_7
max_amp12_7 = None

global max_frec14
max_frec14 = None

global max_amp14
max_amp14 = None

global max_amp14_25
max_amp14_25 = None

global max_amp13_75
max_amp13_75 = None

global modo
modo = None

global radio
radio = None

global radio2
radio2 = None

global showall
showall = None

global lat_par
lat_par = None

global lon_par
lon_par = None

global the_connection
the_connection = None

global nminimo
nminimo = None

global freqdteted
freqdteted = None


socketio = SocketIO(app, async_mode=None, cors_allowed_origins=[])

#random number Generator Thread
thread_status = Thread()
thread_status_stop_event = Event()

thread_mavlink_msg = Thread()
thread_mavlink_msg_stop_event= Event()

thread_chart = Thread()
thread_chart_stop_event = Event()


radio_db = 2

frecuencias = [0.0, 0.45703125, 0.9140625, 1.3828125, 1.83984375, 2.296875, 2.765625, 3.22265625, 3.69140625, 4.1484375, 4.60546875, 5.07421875, 5.53125, 6.0, 6.45703125, 6.9140625, 7.3828125, 7.83984375, 8.296875, 8.765625, 9.22265625, 9.69140625, 10.1484375, 10.60546875, 11.07421875, 11.53125, 12.0, 12.45703125, 12.7, 12.9140625, 13.3828125, 13.75, 13.83984375, 14, 14.25, 14.296875, 14.765625, 15.22265625, 15.69140625, 16.1484375, 16.60546875, 17.07421875, 17.53125, 18.0, 18.45703125, 18.9140625, 19.3828125, 19.83984375, 20.296875, 20.765625, 21.22265625, 21.69140625, 22.1484375, 22.60546875, 23.07421875, 23.53125, 24.0]

def get_distance(lat1, lon1, lat2, lon2):
	lat1 = radians(lat1)
	lon1 = radians(lon1)
	lat2 = radians(lat2)
	lon2 = radians(lon2)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	distance = R * c

	return distance*1000

def swapPositions(list, pos1, pos2):
    list[pos2] = list[pos1]
    list.pop(pos1)
    return list

def send_data_chart():
	#global namedb, umbral_f, umbral_a, radio2, showall
	global namedb, radio2, nminimo, freqdteted
	while not thread_chart_stop_event.isSet():
		data = []
		if namedb!=None and radio2!=None:
			radio_db = int(radio2)
			#umbral_f2 = float(umbral_f) + float(radio)
			#cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			connection = engine.connect()
			#cursor.execute('SELECT * FROM '+namedb+' WHERE Max_frecuencia >= %s and Max_frecuencia < %s and Max_amplitud > %s', (umbral_f,umbral_f2,umbral_a,))
			#if int(showall)==1:
			#	rows = connection.execute('SELECT * FROM '+namedb+' WHERE Max_amplitud > ? and Latitud!=1', (umbral_a)).fetchall()
				#rows = connection.execute('SELECT * FROM FUNDOBOTELLAV3 WHERE Max_amplitud > ? and Latitud!=1', (umbral_a)).fetchall()
			#else:
			#	rows = connection.execute('SELECT * FROM '+namedb+' WHERE Max_frecuencia >= ? and Max_frecuencia < ? and Max_amplitud > ? and Latitud!=1', (umbral_f,umbral_f2,umbral_a)).fetchall()
				#rows = connection.execute('SELECT * FROM FUNDOBOTELLAV3 WHERE Max_frecuencia >= ? and Max_frecuencia < ? and Max_amplitud > ? and Latitud!=1', (umbral_f,umbral_f2,umbral_a)).fetchall()
			rows = connection.execute('SELECT * FROM '+namedb+' WHERE Latitud!=1').fetchall()
			if freqdteted==None or freqdteted=="all":
				#rows = connection.execute('SELECT * FROM FUNDOBOTELLAV3 WHERE Latitud!=1').fetchall()
				col_f = '5'
			elif freqdteted=="12_7":
				#rows = connection.execute('SELECT * FROM FUNDOBOTELLAV3 WHERE Max_frecuencia == ? and Latitud!=1', (12.7)).fetchall()
				col_f = '6'
			elif freqdteted=="14":
				#rows = connection.execute('SELECT * FROM FUNDOBOTELLAV3 WHERE Max_frecuencia == ? and Latitud!=1', (14.0)).fetchall()
				col_f = '7'
			elif freqdteted=="14_25":
				#rows = connection.execute('SELECT * FROM FUNDOBOTELLAV3 WHERE Max_frecuencia == ? and Latitud!=1', (14.25)).fetchall()
				col_f = '8'
			cant_rows = len(rows)
			if cant_rows>0:
				cant_col = len(rows[0].keys())
				matrix0 = pd.DataFrame(rows)
				if cant_col>=10:
					matrix0.columns = matrix0.columns.map(str)
					matrix = pd.crosstab(index=matrix0['2'], columns=matrix0['3'], values=matrix0[col_f], aggfunc='max')
					matrix.columns = matrix.columns.map(str)
					matrix2 = matrix.stack().reset_index().rename(columns={'2':'2','3':'3', 0:col_f})
					m_a = col_f
					lt = '2'
					ln = '3'
				else:
					matrix0.columns = matrix0.columns.map(str)
					matrix = pd.crosstab(index=matrix0['1'], columns=matrix0['2'], values=matrix0['4'], aggfunc='max')
					matrix.columns = matrix.columns.map(str)
					matrix2 = matrix.stack().reset_index().rename(columns={'1':'1','2':'2', 0:'4'})
					m_a = '4'
					lt = '1'
					ln = '2'
				column = matrix0[m_a]
				if nminimo==None:
					nminimo = -90
				else:
					nminimo = float(nminimo)
				max_value1 = nminimo-radio_db
				max_value2 = nminimo-radio_db*2
				max_value3 = nminimo-radio_db*3
				matrix2[ln] = matrix2[ln].astype(float)
				mark1 = matrix2.loc[(matrix2[m_a] <= nminimo) & (matrix2[m_a] >= max_value1)]
				mark1_lat = mark1[lt].tolist()
				mark1_lon = mark1[ln].tolist()
				text_mark1 = []
				for index, row in mark1.iterrows():
					new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
					text_mark1.append(new_txt)
				mark2 = matrix2.loc[(matrix2[m_a] < max_value1) & (matrix2[m_a] >= max_value2)]
				mark2_lat = mark2[lt].tolist()
				mark2_lon = mark2[ln].tolist()
				text_mark2 = []
				for index, row in mark2.iterrows():
					new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
					text_mark2.append(new_txt)
				mark3 = matrix2.loc[(matrix2[m_a] < max_value2) & (matrix2[m_a] >= max_value3)]
				mark3_lat = mark3[lt].tolist()
				mark3_lon = mark3[ln].tolist()
				text_mark3 = []
				for index, row in mark3.iterrows():
					new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
					text_mark3.append(new_txt)
				mark4 = matrix2.loc[(matrix2[m_a] > nminimo) | (matrix2[m_a] < max_value3)]
				mark4_lat = mark4[lt].tolist()
				mark4_lon = mark4[ln].tolist()
				text_mark4 = []
				for index, row in mark4.iterrows():
					new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
					text_mark4.append(new_txt)
				for x in range(len(mark1[lt])):
					trace = {'x': [mark1_lat[x]],'y': [mark1_lon[x]],'text':[text_mark1[x]],'mode': 'markers','name': "Intensidad 1 (Mayor)",'type': 'scatter','marker': {'color': 'rgba(150, 0, 0, 0.9)'}}
					data.append(trace)
				for x in range(len(mark2[lt])):
					trace = {'x': [mark2_lat[x]],'y': [mark2_lon[x]],'text':[text_mark2[x]],'mode': 'markers','name': "Intensidad 2",'type': 'scatter','marker': {'color': 'rgba(255, 136, 0, 0.9)'}}
					data.append(trace)
				for x in range(len(mark3[lt])):
					trace = {'x': [mark3_lat[x]],'y': [mark3_lon[x]],'text':[text_mark3[x]],'mode': 'markers','name': "Intensidad 3",'type': 'scatter','marker': {'color': 'rgba(255, 235, 59, 0.9)'}}
					data.append(trace)
				for x in range(len(mark4[lt])):
					trace = {'x': [mark4_lat[x]],'y': [mark4_lon[x]],'text':[text_mark4[x]],'mode': 'markers','name': "Intensidad 4 (Menor)",'type': 'scatter','marker': {'color': 'rgba(59, 89, 152, 0.9)'}}
					data.append(trace)
		socketio.emit('newdatachart', {'data': data}, namespace='/test')
		socketio.sleep(1)


def send_status():
	global 	vehicle, modo, namedb, max_frec, max_amp, lat_par, lon_par, the_connection, max_frec12_7, max_amp12_7, max_frec14, max_amp14, max_amp14_25, max_amp13_75
	while not thread_status_stop_event.isSet():
		altura = None
		lat = None
		lon = None
		asl = None
		vel = None
		if vehicle==None:
			modo="no_conectado"
		elif modo=="fin":
			modo="fin"
		#elif vehicle!=None and vehicle.location.global_relative_frame.alt > 5 and namedb!=None:
		elif vehicle!=None and vehicle.location.global_relative_frame.alt > -3 and namedb!=None:
			modo="vuelo_captura"
		elif vehicle!=None and vehicle.location.global_relative_frame.alt > 1 and namedb==None:
			modo="vuelo"
		elif vehicle!=None and vehicle.location.global_relative_frame.alt < 1:
			modo = 'suelo'
		else:
			modo="Nada"
		if vehicle!=None:
			msg = the_connection.recv_match(type='GLOBAL_POSITION_INT',blocking=False)
			idx_f = 0
			if msg:
				if msg.get_type() == "BAD_DATA":
					if mavutil.all_printable(msg.data):
						sys.stdout.write(msg.data)
						sys.stdout.flush()
				else:
					asl = float(msg.alt)/1000
			#asl = 584.92+float(vehicle.location.global_relative_frame.alt)
			altura = vehicle.location.global_relative_frame.alt
			lat = vehicle.location.global_relative_frame.lat
			lon = vehicle.location.global_relative_frame.lon
			vel = vehicle.groundspeed
		socketio.emit('newstatus', {'modo': modo, 'asl': asl, 'altura': altura, 'lat': lat, 'lon': lon, 'amplitud': max_amp, 'frecuencia': max_frec, 'vel': vel}, namespace='/test')
		socketio.sleep(0.2)


def receive_mgs_frec_amp():
	global max_frec, max_amp, lat_par, lon_par, the_connection, max_frec12_7, max_amp12_7, max_frec14, max_amp14, max_amp14_25, max_amp13_75
	while not thread_mavlink_msg_stop_event.isSet():
		fig = Figure()
		ax = fig.subplots()
		msg = the_connection.recv_match(type='DATA_BOBINA',blocking=False)
		if msg:
			if msg.get_type() == "BAD_DATA":
				if mavutil.all_printable(msg.data):
					sys.stdout.write(msg.data)
					sys.stdout.flush()
			else:
				if msg:
					if msg.get_type() == "BAD_DATA":
						if mavutil.all_printable(msg.data):
							sys.stdout.write(msg.data)
							sys.stdout.flush()
					else:
						amplitud = msg.amplitud
						lat_par = msg.lat
						lon_par = msg.lon
						if (float(amplitud[57-1]) > float(amplitud[56-1])) and (float(amplitud[57-1]) > float(amplitud[55-1])) and (float(amplitud[57-1]) > float(amplitud[54-1])):
							max_frec = 13.75
							max_amp = amplitud[57-1]
						elif (float(amplitud[56-1]) > float(amplitud[57-1])) and (float(amplitud[56-1]) > float(amplitud[55-1])) and (float(amplitud[56-1]) > float(amplitud[54-1])):
							max_frec = 14.25
							max_amp = amplitud[56-1]
						elif (float(amplitud[55-1]) > float(amplitud[57-1])) and (float(amplitud[55-1]) > float(amplitud[56-1])) and (float(amplitud[55-1]) > float(amplitud[54-1])):
							max_frec = 14
							max_amp = amplitud[55-1]
						else:
							max_frec = 12.7
							max_amp = amplitud[54-1]
						max_frec12_7 = 12.7
						max_frec14 = 14
						max_amp12_7 = amplitud[54-1]
						max_amp14 = amplitud[55-1]
						max_amp14_25 = amplitud[56-1]
						max_amp13_75 = amplitud[57-1]
				amplitud.insert(30, amplitud[56])
				amplitud.pop(57)
				amplitud.insert(32, amplitud[56])
				amplitud.pop(57)
				amplitud.insert(32, amplitud[56])
				amplitud.pop(57)
				amplitud.insert(28, amplitud[56])
				amplitud.pop(57)
				#print(amplitud)
				#print(len(amplitud))
				#print(len(frecuencias))
				#print(len(msg.amplitud))
		else:
			lat_par = 0
			lon_par = 0
			max_frec12_7 = 0
			max_amp12_7 = 0
			max_frec14 = 0
			max_amp14 = 0
			max_amp14_25 = 0
			max_amp13_75 = 0
			max_amp = 0
		isplot = False 
		buf = BytesIO()
		try:  
			ax.plot(frecuencias,amplitud)
			ax.set(xlabel="Freq [kHz]", ylabel="Amplitud [dBFS]")
			ax.set_ylim([-120,0])
			#ax.xticks(np.arange(0, 24, 1.0))
			ax.xaxis.set_ticks(np.arange(0, 25, 1))
			ax.grid(True)
			# Save it to a temporary buffer.
			fig.savefig(buf, format="png")
			isplot = True
		except:
			print("no plot")
		# Embed the result in the html output.
		response = base64.b64encode(buf.getbuffer()).decode("ascii")
		#return jsonify(response=response, isplot=isplot)
		socketio.emit('newchart', {'response': response, 'isplot': isplot}, namespace='/test')
		socketio.sleep(0.1)


def receive_mgs_frec_ampv2():
	global vehicle, namedb, max_frec, max_amp, lat_par, lon_par, the_connection, max_frec12_7, max_amp12_7, max_frec14, max_amp14, max_amp14_25, max_amp13_75
	while not thread_mavlink_msg_stop_event.isSet():
		msg = the_connection.recv_match(type='DATA_BOBINA',blocking=True)
		if msg:
			if msg.get_type() == "BAD_DATA":
				if mavutil.all_printable(msg.data):
					sys.stdout.write(msg.data)
					sys.stdout.flush()
			else:
				if msg:
					if msg.get_type() == "BAD_DATA":
						if mavutil.all_printable(msg.data):
							sys.stdout.write(msg.data)
							sys.stdout.flush()
					else:
						amp1 = msg.amp1
						amp2 = msg.amp2
						amp3 = msg.amp3
						amp4 = msg.amp4
						lat_par = msg.lat
						lon_par = msg.lon
						if (float(amp1) > float(amp2)) and (float(amp1) > float(amp3)):
							max_frec = 12.7
							max_amp = amp1
						elif (float(amp2) > float(amp1)) and (float(amp2) > float(amp3)):
							max_frec = 14
							max_amp = amp2
						else:
							max_frec = 14.25
							max_amp = amp3
						max_frec12_7 = 12.7
						max_frec14 = 14
						max_amp12_7 = amp1
						max_amp14 = amp2
						max_amp14_25 = amp3
						max_amp13_75 = amp4
						if vehicle!=None and vehicle.location.global_relative_frame.alt > -3 and namedb!=None:
							now = datetime.datetime.now()
							now2 = now.strftime("%Y-%m-%d %H:%M:%S")
							roll_deg = 0
							pitch_deg = 0
							velocidad = vehicle.groundspeed
							msg_grados = the_connection.recv_match(type='ATTITUDE',blocking=False)
							if msg_grados:
								if msg_grados.get_type() == "BAD_DATA":
									if mavutil.all_printable(msg_grados.data):
										sys.stdout.write(msg_grados.data)
										sys.stdout.flush()
								else:
									roll_deg = math.degrees(msg_grados.roll)
									pitch_deg = math.degrees(msg_grados.pitch)
							connection = engine.connect()
							connection.execute("INSERT INTO "+namedb+" (Tiempo, Latitud, Longitud, Max_frecuencia, Max_amplitud, Amplitud_12_7khz, Amplitud_14khz, Amplitud_14_25khz, Pitch_Angulo, Roll_Angulo, Velocidad) VALUES (?, ?, ?,?,?,?,?,?,?,?,?)", (str(now2), str(lat_par), str(lon_par), max_frec, max_amp, max_amp12_7, max_amp14, max_amp14_25, pitch_deg, roll_deg, velocidad))
		socketio.emit('markers', {'max_amp12_7': max_amp12_7, 'max_amp14': max_amp14, 'max_amp14_25': max_amp14_25}, namespace='/test')
		socketio.sleep(0.1)

'''
#the_connection = mavutil.mavlink_connection('com4', dialect='common')
the_connection = mavutil.mavlink_connection('udp:127.0.0.1:14550')
#the_connection = mavutil.mavlink_connection('tcp:127.0.0.1:5763')
the_connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" % (the_connection.target_system, the_connection.target_system))
vehicle = connect('udp:127.0.0.1:14551')
#vehicle = connect('tcp:127.0.0.1:5762')
'''
'''
@app.route("/")
def index():
	#global modo, namedb, umbral_f, umbral_a, radio, showall
	global modo, namedb,radio2
	fig = Figure()
	ax = fig.subplots()
	y = [0]
	x =[0]
	print(len(x))
	print(len(y))	    
	ax.plot(x,y)
	ax.set(xlabel="Freq [kHz]", ylabel="Amplitud [dBFS]")
	# Save it to a temporary buffer.
	buf = BytesIO()
	fig.savefig(buf, format="png")
	# Embed the result in the html output.
	plot_url = base64.b64encode(buf.getbuffer()).decode("ascii")
	return render_template('index.html', plot_url=plot_url, namedb=namedb, radio2=radio2)
'''

@app.route('/graph_feed')
def graph_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_plots(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/get_data", methods=['GET'])
def get_data():
    global 	vehicle
    if vehicle!=None:
    	lat = vehicle.location.global_relative_frame.lat
    	lon = vehicle.location.global_relative_frame.lon
    	#lat, lon = uniform(-180,180), uniform(-90, 90)
    	coord = {"geometry": {"type": "Point", "coordinates": [lon, lat]}, "type": "Feature", "properties": {}}
    	return jsonify(coord)

@app.route('/init_connection', methods=['GET', 'POST'])
def init_connection():
	global the_connection
	#ok = connection()
	ok = True
	the_connection.close()
	the_connection = mavutil.mavlink_connection('udp:127.0.0.1:14550')
	the_connection.wait_heartbeat()
	return json.dumps({'status':ok})

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        #cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        connection = engine.connect()
        #cursor.execute('SELECT * FROM usuario WHERE nombre = %s AND password = %s', (username, password,))
        account = connection.execute('SELECT * FROM users WHERE email = "'+username+'" AND password = "'+password+'"').fetchone()
        # Fetch one record and return result
        #account = cursor.fetchone()
        # If account exists in usuario table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['email']
            # Redirect to home page
            flash('Has iniciado sesión correctamente')
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Nombre de Usuario/Contraseña Incorrectos'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


@app.route("/init_capture_data", methods=['POST'])
def init_capture_data():
    #global 	vehicle, modo, namedb, umbral_f, umbral_a, radio
    global 	vehicle, modo, namedb, radio2
    namedb2 =  request.form['namedb']
    #umbral_f =  request.form['umbral']
    umbral_f =  12
    #umbral_a =  request.form['umbral2']
    umbral_a = -85
    #radio =  request.form['radio']
    radio2 = 2
    if namedb is None:
    	namedb = namedb2
    	connection = engine.connect()
    	connection.execute("CREATE TABLE "+namedb2+" (id INTEGER PRIMARY KEY AUTOINCREMENT,Tiempo TEXT,Latitud double,Longitud double,Max_frecuencia double, Max_amplitud double, Amplitud_12_7khz double, Amplitud_14khz double, Amplitud_14_25khz double, Pitch_Angulo double, Roll_Angulo double, Velocidad double)")
    	connection.execute("INSERT INTO lista (reporte, umbral1, umbral2, radio, estado) VALUES (?, ?, ?, ?, ?)", (namedb2, umbral_f, umbral_a, radio2, "vuelo_captura"))
    	modo = "vuelo_captura"
    return json.dumps({'status':'OK'})


@app.route("/status_data", methods=['GET'])
def status_data():
	global 	vehicle, mode,namedb, max_frec, max_amp
	altura = None
	lat = None
	lon = None
	asl = None
	modo = ""
	if vehicle!=None and vehicle.location.global_relative_frame.alt > 5 and namedb!=None:
		#medicion = random.randint(0,100)
		#cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		#sql = "INSERT INTO "+namedb+" (Latitud, Longitud, Max_frecuencia, Max_amplitud) VALUES (%s, %s,%s,%s)"
		#sql = "INSERT INTO sadasd (Latitud, Longitud, Medicion) VALUES (%s, %s,%s)"
		#val = (str(vehicle.location.global_relative_frame.lat), str(vehicle.location.global_relative_frame.lon), max_frec, max_amp)
		#cur.execute(sql, val)
		#mysql.connection.commit()
		#print("insertando")
		modo="vuelo"
	elif vehicle!=None and vehicle.location.global_relative_frame.alt > 1:
		modo="vuelo"
	elif vehicle!=None and vehicle.location.global_relative_frame.alt < 1:
		modo = 'Suelo'
	else:
		modo="Nada"
	if vehicle!=None:
		altura = vehicle.location.global_relative_frame.alt
		lat = vehicle.location.global_relative_frame.lat
		lon = vehicle.location.global_relative_frame.lon
	return jsonify(modo=modo, altura=altura, lat=lat, lon=lon, amplitud=max_amp)


@app.route('/', methods=['GET', 'POST'])
def report():
	global showall
	connection = engine.connect()
	lista = connection.execute("SELECT * FROM lista").fetchall()
	return render_template('realworld2.html', lista=lista)	


@app.route("/update_chart", methods=['GET', 'POST'])
def update_chart():
	print("llega")
	opt_param = request.args.get("reporte")
	frec_param = request.args.get("frecuencia_m")
	radio_param = request.args.get("radio_m")
	amp_param = request.args.get("amplitud_m")
	radio_db_param = request.args.get("radio2")
	connection = engine.connect()
	data = None
	data = []
	if opt_param is not None:
		if frec_param is not None and amp_param is not None and radio_db_param is not None:
			radio_db = int(radio_db_param)
			get_lista = [opt_param, frec_param, amp_param, "", radio_db]
			if frec_param=="all":
				rows = connection.execute('SELECT * FROM '+opt_param+' WHERE Latitud!=1').fetchall()
				cant_rows = len(rows)
				if cant_rows>0:
					cant_col = len(rows[0].keys())
					matrix0 = pd.DataFrame(rows)
					if cant_col>=10:
						matrix0.columns = matrix0.columns.map(str)
						matrix = pd.crosstab(index=matrix0['2'], columns=matrix0['3'], values=matrix0['5'], aggfunc='max')
						matrix.columns = matrix.columns.map(str)
						matrix2 = matrix.stack().reset_index().rename(columns={'2':'2','3':'3', 0:'5'})
						m_a = '5'
						lt = '2'
						ln = '3'
					else:
						matrix0.columns = matrix0.columns.map(str)
						matrix = pd.crosstab(index=matrix0['1'], columns=matrix0['2'], values=matrix0['4'], aggfunc='max')
						matrix.columns = matrix.columns.map(str)
						matrix2 = matrix.stack().reset_index().rename(columns={'1':'1','2':'2', 0:'4'})
						m_a = '4'
						lt = '1'
						ln = '2'
					column = matrix0[m_a]
					nminimo = float(amp_param)
					max_value1 = nminimo-radio_db
					max_value2 = nminimo-radio_db*2
					max_value3 = nminimo-radio_db*3
					matrix2[ln] = matrix2[ln].astype(float)
					mark1 = matrix2.loc[(matrix2[m_a] <= nminimo) & (matrix2[m_a] >= max_value1)]
					mark1_lat = mark1[lt].tolist()
					mark1_lon = mark1[ln].tolist()
					text_mark1 = []
					for index, row in mark1.iterrows():
						new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
						text_mark1.append(new_txt)
					mark2 = matrix2.loc[(matrix2[m_a] < max_value1) & (matrix2[m_a] >= max_value2)]
					mark2_lat = mark2[lt].tolist()
					mark2_lon = mark2[ln].tolist()
					text_mark2 = []
					for index, row in mark2.iterrows():
						new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
						text_mark2.append(new_txt)
					mark3 = matrix2.loc[(matrix2[m_a] < max_value2) & (matrix2[m_a] >= max_value3)]
					mark3_lat = mark3[lt].tolist()
					mark3_lon = mark3[ln].tolist()
					text_mark3 = []
					for index, row in mark3.iterrows():
						new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
						text_mark3.append(new_txt)
					mark4 = matrix2.loc[(matrix2[m_a] > nminimo) | (matrix2[m_a] < max_value3)]
					mark4_lat = mark4[lt].tolist()
					mark4_lon = mark4[ln].tolist()
					text_mark4 = []
					for index, row in mark4.iterrows():
						new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
						text_mark4.append(new_txt)
					for x in range(len(mark1[lt])):
						trace = {'x': [mark1_lat[x]],'y': [mark1_lon[x]],'text':[text_mark1[x]],'mode': 'markers','name': "Intensidad 1 (Mayor)",'type': 'scatter','marker': {'color': 'rgba(150, 0, 0, 0.9)'}}
						data.append(trace)
					for x in range(len(mark2[lt])):
						trace = {'x': [mark2_lat[x]],'y': [mark2_lon[x]],'text':[text_mark2[x]],'mode': 'markers','name': "Intensidad 2",'type': 'scatter','marker': {'color': 'rgba(255, 136, 0, 0.9)'}}
						data.append(trace)
					for x in range(len(mark3[lt])):
						trace = {'x': [mark3_lat[x]],'y': [mark3_lon[x]],'text':[text_mark3[x]],'mode': 'markers','name': "Intensidad 3",'type': 'scatter','marker': {'color': 'rgba(255, 235, 59, 0.9)'}}
						data.append(trace)
					for x in range(len(mark4[lt])):
						trace = {'x': [mark4_lat[x]],'y': [mark4_lon[x]],'text':[text_mark4[x]],'mode': 'markers','name': "Intensidad 4 (Menor)",'type': 'scatter','marker': {'color': 'rgba(59, 89, 152, 0.9)'}}
						data.append(trace)
			else:
				if frec_param!="":
					rows = connection.execute('SELECT * FROM '+opt_param+' WHERE Latitud!=1').fetchall()
					if frec_param=="12_7":
						col_f = '6'
					elif frec_param=="14":
						col_f = '7'
					elif frec_param=="14_25":
						col_f = '8'
					cant_rows = len(rows)
					if cant_rows>0:
						cant_col = len(rows[0].keys())
						matrix0 = pd.DataFrame(rows)
						if cant_col>=10:
							matrix0.columns = matrix0.columns.map(str)
							matrix = pd.crosstab(index=matrix0['2'], columns=matrix0['3'], values=matrix0[col_f], aggfunc='max')
							matrix.columns = matrix.columns.map(str)
							matrix2 = matrix.stack().reset_index().rename(columns={'2':'2','3':'3', 0:col_f})
							m_a = col_f
							lt = '2'
							ln = '3'
						else:
							matrix0.columns = matrix0.columns.map(str)
							matrix = pd.crosstab(index=matrix0['1'], columns=matrix0['2'], values=matrix0['4'], aggfunc='max')
							matrix.columns = matrix.columns.map(str)
							matrix2 = matrix.stack().reset_index().rename(columns={'1':'1','2':'2', 0:'4'})
							m_a = '4'
							lt = '1'
							ln = '2'
						column = matrix0[m_a]
						nminimo = float(amp_param)
						max_value1 = nminimo-radio_db
						max_value2 = nminimo-radio_db*2
						max_value3 = nminimo-radio_db*3
						matrix2[ln] = matrix2[ln].astype(float)
						mark1 = matrix2.loc[(matrix2[m_a] <= nminimo) & (matrix2[m_a] >= max_value1)]
						mark1_lat = mark1[lt].tolist()
						mark1_lon = mark1[ln].tolist()
						text_mark1 = []
						for index, row in mark1.iterrows():
							new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
							text_mark1.append(new_txt)
						mark2 = matrix2.loc[(matrix2[m_a] < max_value1) & (matrix2[m_a] >= max_value2)]
						mark2_lat = mark2[lt].tolist()
						mark2_lon = mark2[ln].tolist()
						text_mark2 = []
						for index, row in mark2.iterrows():
							new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
							text_mark2.append(new_txt)
						mark3 = matrix2.loc[(matrix2[m_a] < max_value2) & (matrix2[m_a] >= max_value3)]
						mark3_lat = mark3[lt].tolist()
						mark3_lon = mark3[ln].tolist()
						text_mark3 = []
						for index, row in mark3.iterrows():
							new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
							text_mark3.append(new_txt)
						mark4 = matrix2.loc[(matrix2[m_a] > nminimo) | (matrix2[m_a] < max_value3)]
						mark4_lat = mark4[lt].tolist()
						mark4_lon = mark4[ln].tolist()
						text_mark4 = []
						for index, row in mark4.iterrows():
							new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
							text_mark4.append(new_txt)
						for x in range(len(mark1[lt])):
							trace = {'x': [mark1_lat[x]],'y': [mark1_lon[x]],'text':[text_mark1[x]],'mode': 'markers','name': "Intensidad 1 (Mayor)",'type': 'scatter','marker': {'color': 'rgba(150, 0, 0, 0.9)'}}
							data.append(trace)
						for x in range(len(mark2[lt])):
							trace = {'x': [mark2_lat[x]],'y': [mark2_lon[x]],'text':[text_mark2[x]],'mode': 'markers','name': "Intensidad 2",'type': 'scatter','marker': {'color': 'rgba(255, 136, 0, 0.9)'}}
							data.append(trace)
						for x in range(len(mark3[lt])):
							trace = {'x': [mark3_lat[x]],'y': [mark3_lon[x]],'text':[text_mark3[x]],'mode': 'markers','name': "Intensidad 3",'type': 'scatter','marker': {'color': 'rgba(255, 235, 59, 0.9)'}}
							data.append(trace)
						for x in range(len(mark4[lt])):
							trace = {'x': [mark4_lat[x]],'y': [mark4_lon[x]],'text':[text_mark4[x]],'mode': 'markers','name': "Intensidad 4 (Menor)",'type': 'scatter','marker': {'color': 'rgba(59, 89, 152, 0.9)'}}
							data.append(trace)
		else:
			lista2 = connection.execute("SELECT * FROM lista where reporte = ?", (opt_param)).fetchone()
			get_lista = [lista2['reporte'], "", "", "", lista2['radio']]
			radio_db = 2
			#radio = float(lista2['umbral1'])+float(lista2['radio'])
			#rows = connection.execute('SELECT * FROM '+opt_param+' WHERE Max_frecuencia >= ? and Max_frecuencia < ? and Max_amplitud > ? and Latitud!=1', (lista2['umbral1'], radio, lista2['umbral2'])).fetchall()
			rows = connection.execute('SELECT * FROM '+opt_param+' WHERE Latitud!=1').fetchall()
			cant_rows = len(rows)
			if cant_rows>0:
				cant_col = len(rows[0].keys())
				matrix0 = pd.DataFrame(rows)
				if cant_col>=10:
					matrix0.columns = matrix0.columns.map(str)
					matrix = pd.crosstab(index=matrix0['2'], columns=matrix0['3'], values=matrix0['5'], aggfunc='max')
					matrix.columns = matrix.columns.map(str)
					matrix2 = matrix.stack().reset_index().rename(columns={'2':'2','3':'3', 0:'5'})
					m_a = '5'
					lt = '2'
					ln = '3'
				else:
					matrix0.columns = matrix0.columns.map(str)
					matrix = pd.crosstab(index=matrix0['1'], columns=matrix0['2'], values=matrix0['4'], aggfunc='max')
					matrix.columns = matrix.columns.map(str)
					matrix2 = matrix.stack().reset_index().rename(columns={'1':'1','2':'2', 0:'4'})
					m_a = '4'
					lt = '1'
					ln = '2'
				column = matrix0[m_a]
				nminimo = -90
				max_value1 = nminimo-radio_db
				max_value2 = nminimo-radio_db*2
				max_value3 = nminimo-radio_db*3
				matrix2[ln] = matrix2[ln].astype(float)
				mark1 = matrix2.loc[(matrix2[m_a] <= nminimo) & (matrix2[m_a] >= max_value1)]
				mark1_lat = mark1[lt].tolist()
				mark1_lon = mark1[ln].tolist()
				text_mark1 = []
				for index, row in mark1.iterrows():
					new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
					text_mark1.append(new_txt)
				mark2 = matrix2.loc[(matrix2[m_a] < max_value1) & (matrix2[m_a] >= max_value2)]
				mark2_lat = mark2[lt].tolist()
				mark2_lon = mark2[ln].tolist()
				text_mark2 = []
				for index, row in mark2.iterrows():
					new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
					text_mark2.append(new_txt)
				mark3 = matrix2.loc[(matrix2[m_a] < max_value2) & (matrix2[m_a] >= max_value3)]
				mark3_lat = mark3[lt].tolist()
				mark3_lon = mark3[ln].tolist()
				text_mark3 = []
				for index, row in mark3.iterrows():
					new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
					text_mark3.append(new_txt)
				mark4 = matrix2.loc[(matrix2[m_a] > nminimo) | (matrix2[m_a] < max_value3)]
				mark4_lat = mark4[lt].tolist()
				mark4_lon = mark4[ln].tolist()
				text_mark4 = []
				for index, row in mark4.iterrows():
					new_txt = "Amplitud: "+str(round(row[m_a],2))+"<br />"+"Latitud: "+str(row[lt])+"<br />"+"Longitud: "+str(row[ln])
					text_mark4.append(new_txt)
				for x in range(len(mark1[lt])):
					trace = {'x': [mark1_lat[x]],'y': [mark1_lon[x]],'text':[text_mark1[x]],'mode': 'markers','name': "Intensidad 1 (Mayor)",'type': 'scatter','marker': {'color': 'rgba(150, 0, 0, 0.9)'}}
					data.append(trace)
				for x in range(len(mark2[lt])):
					trace = {'x': [mark2_lat[x]],'y': [mark2_lon[x]],'text':[text_mark2[x]],'mode': 'markers','name': "Intensidad 2",'type': 'scatter','marker': {'color': 'rgba(255, 136, 0, 0.9)'}}
					data.append(trace)
				for x in range(len(mark3[lt])):
					trace = {'x': [mark3_lat[x]],'y': [mark3_lon[x]],'text':[text_mark3[x]],'mode': 'markers','name': "Intensidad 3",'type': 'scatter','marker': {'color': 'rgba(255, 235, 59, 0.9)'}}
					data.append(trace)
				for x in range(len(mark4[lt])):
					trace = {'x': [mark4_lat[x]],'y': [mark4_lon[x]],'text':[text_mark4[x]],'mode': 'markers','name': "Intensidad 4 (Menor)",'type': 'scatter','marker': {'color': 'rgba(59, 89, 152, 0.9)'}}
					data.append(trace)
	return jsonify(data=data, get_lista=get_lista)

@app.route("/get_data2", methods=['GET'])
def get_data2():
	global namedb, umbral_f, umbral_a, radio, showall
	print("get data 2")
	features = []
	if namedb!=None and umbral_f!=None and umbral_a!=None and showall!=None:
		umbral_f2 = float(umbral_f) + float(radio)
		#cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		connection = engine.connect()
		#cursor.execute('SELECT * FROM '+namedb+' WHERE Max_frecuencia >= %s and Max_frecuencia < %s and Max_amplitud > %s', (umbral_f,umbral_f2,umbral_a,))
		if int(showall)==1:
			data = connection.execute('SELECT * FROM '+namedb+' WHERE Max_amplitud > ?', (umbral_a)).fetchall()
		else:
			data = connection.execute('SELECT * FROM '+namedb+' WHERE Max_frecuencia >= ? and Max_frecuencia < ? and Max_amplitud > ?', (umbral_f,umbral_f2,umbral_a)).fetchall()
		#data = cursor.fetchall()
		#features = [{"type":"Feature","properties":{"medicion":4.7, "id": 1},"geometry":{"type":"Point","coordinates":[58.235,34.3382]},"id":"us7000dhxs"}]
		for a in data:
			#print(a)
			feature = {"type":"Feature","properties":{"frecuencia":a['Max_frecuencia'], "amplitud":a['Max_amplitud'], "id": a['id']},"geometry":{"type":"Point","coordinates":[a['Longitud'],a['Latitud']]},"id":"us7000dhxs"}
			features.append(feature)
	coord = {"type":"FeatureCollection","metadata":{"generated":1615411384000,"url":"https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson","title":"USGS Magnitude 2.5+ Earthquakes, Past Day","status":200,"api":"1.10.3","count":35},"features":features}
	return jsonify(coord)

@app.route('/stop_data', methods=['GET', 'POST'])
def stop_data():
	#global modo, namedb, umbral_f, umbral_a, radio
	global modo, namedb, radio2
	modo = 'fin'
	connection = engine.connect()
	connection.execute("UPDATE lista SET estado = ? where reporte = ?", (modo, namedb))
	namedb = None
	#umbral_f = None
	#umbral_a = None
	radio2 = None
	return json.dumps({'status':'OK'})

@app.route('/update_frecuencia', methods=['GET', 'POST'])
def update_frecuencia():
    global namedb, umbral_f
    umbral_f =  request.form['frecuencia']
    connection = engine.connect()
    connection.execute("UPDATE lista SET umbral1 = ? where reporte = ?", (umbral_f, namedb))
    return json.dumps({'status':'OK'})

@app.route('/update_amplitud', methods=['GET', 'POST'])
def update_amplitud():
    global namedb, umbral_a
    umbral_a =  request.form['amplitud']
    connection = engine.connect()
    connection.execute("UPDATE lista SET umbral2 = ? where reporte = ?", (umbral_a, namedb))
    return json.dumps({'status':'OK'})

@app.route('/update_radio', methods=['GET', 'POST'])
def update_radio():
    global namedb, radio
    radio =  request.form['radio']
    connection = engine.connect()
    connection.execute("UPDATE lista SET radio = ? where reporte = ?", (radio, namedb))
    return json.dumps({'status':'OK'})

@app.route('/update_radio2', methods=['GET', 'POST'])
def update_radio2():
    global namedb, radio2
    radio2 =  request.form['radio']
    connection = engine.connect()
    connection.execute("UPDATE lista SET radio = ? where reporte = ?", (radio2, namedb))
    return json.dumps({'status':'OK'})


@app.route('/update_showall', methods=['GET', 'POST'])
def update_showall():
    global namedb, showall
    showall =  request.form['showall']
    print("showall")
    print(showall)
    return json.dumps({'status':'OK'})

@app.route('/changeminvalueamp', methods=['GET', 'POST'])
def changeminvalueamp():
    global nminimo
    nminimo =  request.form['valueamp']
    print("nminimo")
    print(nminimo)
    return json.dumps({'status':'OK'})

@app.route('/changefreqd', methods=['GET', 'POST'])
def changefreqd():
    global freqdteted
    freqdteted =  request.form['valuefreq']
    print("freqdteted")
    print(freqdteted)
    return json.dumps({'status':'OK'})


@app.route("/download_csv", methods=['GET', 'POST'])
def download_csv():
	table =  request.form['table']
	connection = engine.connect()
	rows = connection.execute("SELECT * FROM "+table).fetchall()
	cant_col = len(rows[0].keys())
	#csv = '1,2,3\n4,5,6\n'
	if cant_col==12:
		csv = "id;Tiempo;Latitud;Longitud;Max_frecuencia;Max_amplitud;Amplitud_12_7khz;Amplitud_14khz;Amplitud_14_25khz;Pitch_Angulo;Roll_Angulo;Velocidad"+"\n"
		for row in rows:
			csv += str(row['id'])+";"+str(row['Tiempo'])+";"+str(row['Latitud'])+";"+str(row['Longitud'])+";"+str(row['Max_frecuencia'])+";"+str(row['Max_amplitud'])+";"+str(row['Amplitud_12_7khz'])+";"+str(row['Amplitud_14khz'])+";"+str(row['Amplitud_14_25khz'])+";"+str(row['Pitch_Angulo'])+";"+str(row['Roll_Angulo'])+";"+str(row['Velocidad'])+"\n"
	elif cant_col==10:
		csv = "id;Tiempo;Latitud;Longitud;Max_frecuencia;Max_amplitud;Amplitud_12_7khz;Amplitud_14khz;Pitch_Angulo;Roll_Angulo"+"\n"
		for row in rows:
			csv += str(row['id'])+";"+str(row['Tiempo'])+";"+str(row['Latitud'])+";"+str(row['Longitud'])+";"+str(row['Max_frecuencia'])+";"+str(row['Max_amplitud'])+";"+str(row['Amplitud_12_7khz'])+";"+str(row['Amplitud_14khz'])+";"+str(row['Pitch_Angulo'])+";"+str(row['Roll_Angulo'])+"\n"
	else:
		csv = "id;Latitud;Longitud;Max_frecuencia;Max_amplitud;Amplitud_12_7khz;Amplitud_14khz"+"\n"
		for row in rows:
			csv += str(row['id'])+";"+str(row['Latitud'])+";"+str(row['Longitud'])+";"+str(row['Max_frecuencia'])+";"+str(row['Max_amplitud'])+";"+str(row['Amplitud_12_7khz'])+";"+str(row['Amplitud_14khz'])+"\n"
	return Response(
	    csv,
	    mimetype="text/csv",
	    headers={"Content-disposition":
	             "attachment; filename="+table+".csv"})

@app.route("/download_csv_baliza", methods=['GET', 'POST'])
def download_csv_baliza():
	table =  request.form['tableb']
	nfile = request.form['nfile']
	freqbaliza = request.form['freqbaliza']
	latlongb = request.form['latlongb']
	radio_d = request.form['radio_d']
	porcentaje = request.form['porcentaje']
	latlongb2 = latlongb.replace('<br />',' ')
	latlongb3 = latlongb2.split()
	print(latlongb3)
	lat = float(latlongb3[3])
	lon = float(latlongb3[5])
	connection = engine.connect()
	rows = connection.execute("SELECT * FROM "+table).fetchall()
	cant_col = len(rows[0].keys())
	if freqbaliza=="12_7":
		col_f = '6'
	elif freqbaliza=="14":
		col_f = '7'
	elif freqbaliza=="14_25":
		col_f = '8'
	if cant_col>0:
		matrix0 = pd.DataFrame(rows)
		matrix0.columns = matrix0.columns.map(str)
		matrix = pd.crosstab(index=matrix0['2'], columns=matrix0['3'], values=matrix0[col_f], aggfunc='max')
		matrix.columns = matrix.columns.map(str)
		matrix2 = matrix.stack().reset_index().rename(columns={'2':'2','3':'3', 0:col_f})
		#mark1 = matrix2.loc[(matrix2['2'] == lat) & (matrix2['3'] == lon)]
		distancia = []
		for index, row in matrix2.iterrows():
			new_distance = get_distance(lat, lon, float(row['2']), float(row['3']))
			distancia.append(new_distance)
		matrix2['distancia'] = distancia
		mark1 = matrix2.loc[(matrix2['distancia'] <= float(radio_d))]
		mark1.sort_values('distancia')
		final_df = mark1.sort_values(by=[col_f], ascending=False)
		final_df['2'] = final_df['2'].astype(float)
		final_df['3'] = final_df['3'].astype(float)
		cant_tot_rows = final_df.shape[0]
		cant_final = int((cant_tot_rows*float(porcentaje))/100)
		if cant_final==0:
			cant_final = 1
		final_df2 = final_df.head(cant_final)
		print(final_df)
		lat_prom = final_df2["2"].mean()
		lon_prom = final_df2["3"].mean()
		amp_prom = final_df2[col_f].mean()
	if freqbaliza=="12_7":
		csv = "Latitud;Longitud;Amplitud_12_7khz"+"\n"
		csv += str(lat_prom)+";"+str(lon_prom)+";"+str(amp_prom)+"\n"
	elif freqbaliza=="14":
		csv = "Latitud;Longitud;Amplitud_14khz"+"\n"
		csv += str(lat_prom)+";"+str(lon_prom)+";"+str(amp_prom)+"\n"
	elif freqbaliza=="14_25":
		csv = "Latitud;Longitud;Amplitud_14_25khz"+"\n"
		csv += str(lat_prom)+";"+str(lon_prom)+";"+str(amp_prom)+"\n"
	return Response(
	    csv,
	    mimetype="text/csv",
	    headers={"Content-disposition":
	             "attachment; filename="+nfile+".csv"})

'''
@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread_status, thread_mavlink_msg, thread_chart
    print('Client connected')

    #Start thread send status msg
    if not thread_status.isAlive():
        print("Starting Thread send status")
        thread_status = socketio.start_background_task(send_status)
    if not thread_mavlink_msg.isAlive():
    	thread_mavlink_msg = socketio.start_background_task(receive_mgs_frec_ampv2)
    if not thread_chart.isAlive():
    	thread_chart = socketio.start_background_task(send_data_chart)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
'''

if __name__ == "__main__":
	#app.run("0.0.0.0", port="8080")
	socketio.run(app)
