#!/usr/bin/env python

import sqlite3
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

def application(environ, start_response):

	# the environment variable CONTENT_LENGTH may be empty or missing
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0

	# When the method is POST the variable will be sent
	# in the HTTP request body which is passed by the WSGI server
	# in the file like wsgi.input environment variable.
	request_body = environ['wsgi.input'].read(request_body_size)
	d = parse_qs(request_body)

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
			response_body='Device Nickname: ' + str(resultset[0][0])
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
			response_body='Device Nickname: ' + str(resultset[0][0])
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
