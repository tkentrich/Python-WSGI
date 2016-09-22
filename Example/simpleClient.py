#!/usr/bin/env python

from httplib import HTTPConnection

conn = HTTPConnection("192.168.56.102",8051)
conn.request("post", "/", "")
x = conn.getresponse()
resp = x.read()
print(resp)

