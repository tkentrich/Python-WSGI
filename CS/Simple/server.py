#!/usr/bin/env python

import sys
import os
import sqlite3
import random
from wsgiref.simple_server import make_server
from cgi import parse_qs, escape
from Crypto.Cipher import AES
from Simple import Game

games = {}

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

	function = d['Function'][0]
	deviceId = d['DeviceId'][0]

	# conn = sqlite3.connect('MultiBall.db')
	# curs = conn.cursor()

	response_body = "Default Response"

	if function == 'CheckIn':
		print "Checking In: " + deviceId
		response_body="CheckedIn"

	elif function == 'GetGames': # Get a list of all games (summary for a user to choose from)
		print "Get Games"
		response_body = "Games"
		for x in games:
			response_body += ":" + x.desc()

	elif function == 'CreateGame':
		print "Creating Game: " + deviceId
		creator = deviceId
		# creator = d['Username'][0]
		# Will need to have a "Which game" type of thing here
		# scene = d['Scene'][0]
		scene = "TestScene"
		# games.insert(Game(creator, scene))
		games[creator]=Game(creator, scene)
		response_body="GameCreated"

	elif function == 'JoinGame': # Player wants to join a game
		print "Joining Game"
		creator = d['Creator'][0]
		try:
			games[creator].join(deviceId)
			response_body="GameJoined:"+games[creator]['scene']
		except CannotJoin:
			response_body="CannotJoin"

	elif function == 'GetGame': # Get game details (User has created or joined a game)
		creator = d['Creator'][0]
		print "Get Game Details: " + creator
		response_body = "GameDetails:%s" % (games[creator].getUpdate())

	elif function == 'StartGame':
		try:
			games[deviceId].start()
			response_body="GameStart:"+games[deviceId].scene
		except CannotStart:
			response_body="CannotStart"

	elif function == 'UpdatePosition':
		gameId = d['Creator'][0]
		objectName = d['Object'][0]
		objectPosition = d['Position'][0].split(",")
		games[gameId].updatePosition(objectName, objectPosition)
                response_body = "GameDetails:%s" % (games[creator].getUpdate())

	status = '200 OK'

	response_headers = [
		('Content-Type', 'text/html'),
		('Content-Length', str(len(response_body)))
	]

	start_response(status, response_headers)
	return [response_body]

httpd = make_server('', 8051, application)
httpd.serve_forever()
