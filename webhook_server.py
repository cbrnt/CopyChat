#!/usr/bin/env python3

import socket
import ssl
import json
import requests
import re


# use context for SSL
#context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

HOST = '109.195.230.198'  # Standard loopback interface address (localhost)
PORT = 8070


def get_value(raw_list, parameter):
	re_obj = re.compile(".*%s.*" % parameter)
	value = list(filter(re_obj.match, raw_list))
	print('%s: ' % parameter, value)
	return value

try:

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		sock.bind((HOST, PORT))
		print('Binded port', PORT)
		sock.listen(5) # limited to 5 connection in qeueue
		while True:
			conn, addr = sock.accept()
			print('conn: ', conn)
			print('Connected by', addr)



		#	with context.wrap_socket(sock, server_side=True) as ssock:
		#		conn, addr = ssock.accept()
		#		print('conn: ', conn)
		#		print('Connected by', addr)

			while True:
				data = conn.recv(1024)
				print(type(data))

				if not data:
					break
				print('Data: ', data)
				data = data.decode()
				headers = data.split('\r\n', -1)
				print(type(headers))
				print('Headers: ', headers)
				regexped_obj = re.compile(".*POST.*")
				print('Regexp object: ', regexped_obj)
				regexped_response = list(filter(regexped_obj.match, headers))
				print('Regexped response: ')
				needed_data = headers[len(headers)-1]
				print('Needed data: ',needed_data)
				get_values = needed_data.split('&', -1)
				print('Got values: ', get_values)
				channel_name = get_values(needed_data, 'channel_name')
				print('channel_name: ', channel_name)



except KeyboardInterrupt:
	sock.close()

