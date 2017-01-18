#!/usr/bin/env python

import sys
import os
import sqlite3
import random
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
from Crypto.Cipher import AES

game = ()

try:
	key=os.environ['AES_KEY']
except KeyError:
	print "AES_KEY not set!"
	sys.exit(1)

def decrypt(key, cipher_text):
	print "Cipher text length: " + str(len(cipher_text))
        decryptor = AES.new(key, AES.MODE_CBC, cipher_text[0:16])
        return decryptor.decrypt(cipher_text[16:])

def encrypt(key, plain_text):
        iv = ''.join(chr(random.randint(0, 0xff)) for i in range(16))
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        return iv + encryptor.encrypt(plain_text + " " * (16 - len(plain_text) % 16))

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
	deviceId = d['DeviceId'][0]

	conn = sqlite3.connect('MultiBall.db')
	curs = conn.cursor()

	response_body = "Default Response"

	if function == 'CheckIn':
		print "Checking In"
		query = 'SELECT Username FROM Player WHERE Device = ?'
		param = (deviceId ,)
		resultset = curs.execute(query, param).fetchall()
		if len(resultset) == 0: # Register New Device
			query = 'INSERT INTO Player (Device, Username) VALUES (?, ?)'
        		param = (deviceId, 'User-' + deviceId[-4:], )
        		curs.execute(query, param)
			query = 'SELECT Username FROM Player WHERE Device = ?'
			param = (d['DeviceId'][0] ,)
			resultset = curs.execute(query, param).fetchall()
		response_body="Username:"+resultset[0][0]
	elif function == 'NewName':
		print "Changing Username"
		username = d['Username'][0]
		query = 'UPDATE Player SET Username = ? WHERE Device = ?'
		param = (username, deviceId, )
		curs.execute(query, param)
		response_body="Username:"+username
	elif function == 'CreateGame':
		print "Creating Game"
		creator = d['Username'][0]
		# Will need to have a "Which game" type of thing here
		game = {"creator": creator, "status": "initializing"}
		game['player1'] = creator
		# Will need to populate Objects/Switches
		game['objects'] = ['Player1', 'Player2']
		response_body="GameCreated"
	elif function == 'GetGames':
		print "Get Games"
	elif function == 'JoinGame':
		print "Joining Game"
		# creator = d['Creator'][0]
		username = d['Username'][0]
		# Will need a "Which game"
		game['player2'] = username
		game['status'] = "running"
		# Will need a "Which scene to load"
		scene = "Test"
		response_body="GameJoined:"+scene
	elif function == 'UpdatePosition':
		objectName = d['Object'][0]
		objectPosition = d['Position'][0]
		for x in game['objects']:
			if x == objectName:
				game['position:'+objectName]=objectPosition
		response_body=""
		for x in game['objects']:
			response_body += 
	status = '200 OK'

	response_headers = [
		('Content-Type', 'text/html'),
		('Content-Length', str(len(response_body)))
	]

	start_response(status, response_headers)
	return [response_body]

httpd = make_server('', 8051, application)
httpd.serve_forever()
