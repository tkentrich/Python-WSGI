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

    function = d.get('function', [''])[0]
    if function == 'SendMessage' :
        user = d.get('user', [''])[0]
        recipient = d.get('recipient', [''])[0]
        message = d.get('message', [''])[0]

        # Always escape user input to avoid script injection
        user = escape(user)
        recipient = escape(recipient)
        message = escape(message)

        conn = sqlite3.connect('Chat.db')
        curs = conn.cursor()
        query = 'INSERT INTO Message (Sender, Recipient, Content) VALUES ("{sender}", "{recipient}", "{content}")'.format(sender=user,recipient=recipient,content=message)
	print query
        curs.execute(query)
	conn.commit()
	conn.close()
        response_body="MessageSent"

    # response_body = html % { # Fill the above html template in
        # 'age': age or 'Empty',
    # }

    status = '200 OK'

    response_headers = [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body]

httpd = make_server('192.168.56.102', 8051, application)
httpd.serve_forever()
