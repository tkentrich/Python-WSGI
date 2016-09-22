#!/usr/bin/env python

from httplib import HTTPConnection

conn = HTTPConnection("192.168.56.102",8051)
conn.request("post", "/", "function=SendMessage&amp;user=1&amp;recipient=2&amp;message=You%20are%20everything%20to%20me")
x = conn.getresponse()
resp = x.read()
print(resp)

