#!/usr/bin/env python

import sqlite3
import random
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
from Crypto.Cipher import AES

key = 'RichKent&Anabel!'

def decrypt(key, cipher_text):
	print "Cipher text length: " + str(len(cipher_text))
        decryptor = AES.new(key, AES.MODE_CBC, cipher_text[0:16])
        return decryptor.decrypt(cipher_text[16:])

def encrypt(key, plain_text):
        iv = ''.join(chr(random.randint(0, 0xff)) for i in range(16))
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        return iv + encryptor.encrypt(plain_text + " " * (16 - len(plain_text) % 16))

def playerNames(curs, deviceId):
	print "Getting players for " + str(deviceId)
	query = 'SELECT Name from Player p INNER JOIN PlayerDeviceRegistration r ON r.Player = p.rowid WHERE r.Device = ?'
	param = (deviceId, )
	resultset = curs.execute(query, param).fetchall()
	response_body="Players:"
	for row in resultset:
		response_body += row[0]
	return response_body

def application(environ, start_response):
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0

	request_body = environ['wsgi.input'].read(request_body_size)
	
	d = parse_qs(decrypt(key, request_body))

	for x in d:
		for xi in d[x]:
			print "{0}: {1}".format(x, xi)

	function = d['Function'][0]

	conn = sqlite3.connect('MP.db')
	curs = conn.cursor()

	response_body = "Default Response"

	if function == 'CheckIn':
		print "Checking In"
		query = 'SELECT Nickname FROM Device WHERE UniqueIdentifier = ?'
		param = (d['DeviceID'][0] ,)
		resultset = curs.execute(query, param).fetchall()
		if len(resultset) == 0: # Register New Device
			response_body='Unrecognized Device'
		else:
			response_body=playerNames(curs, d['DeviceID'][0])
	elif function == 'NewDevice':
		print "Registering New Device"
		query = 'INSERT INTO Device (UniqueIdentifier, Nickname) VALUES (?, ?)'
		param = (d['DeviceID'][0], d['Nickname'][0], )
		curs.execute(query, param)
		conn.commit()

		query = 'SELECT Nickname FROM Device WHERE UniqueIdentifier = ?'
		param = (d['DeviceID'][0] ,)
		resultset = curs.execute(query, param).fetchall()
		if len(resultset) == 0: # Something went wrong...
			response_body='Device not registered'
		else:
			# response_body='Device Nickname: ' + str(resultset[0][0])
			response_body=playerNames(curs, d['DeviceID'][0])
	elif function == 'CreatePlayer':
		query = 'INSERT INTO Player (Name) VALUES ("'+d.get('PlayerName')+'")'
		curs.execute(query)
		conn.commit()
		
	status = '200 OK'

	response_headers = [
		('Content-Type', 'text/html'),
		('Content-Length', str(len(response_body)))
	]

	start_response(status, response_headers)
	return [response_body]

httpd = make_server('', 8051, application)
httpd.serve_forever()
