#!/usr/bin/env python
'''
http_server.py
print the input arguments and set cookies
'''
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from urlparse import urlparse, parse_qs
import random

DEFAULT_HOST = ''
DEFAULT_PORT = 80


class RequestHandler(SimpleHTTPRequestHandler):
	def end_headers(self):
		query_components = parse_qs(urlparse(self.path).query)
		if 't' in query_components.keys():
			v = query_components['t'][0]
			print v
			self.send_header('Content-Type',v)
		SimpleHTTPRequestHandler.end_headers(self)


def run_server():
	try:
		server_address=(DEFAULT_HOST, DEFAULT_PORT)
		server= HTTPServer(server_address,RequestHandler)
		print "Custom HTTP server started on port: %s" % DEFAULT_PORT
		server.serve_forever()
	except Exception, err:
		print "Error:%s" %err
	except KeyboardInterrupt:
		print "Server interrupted and is shutting down..."
		server.socket.close()

if __name__ == "__main__":
	run_server()


