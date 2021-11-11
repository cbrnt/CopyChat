#!/usr/bin/env python3

import socket
import ssl
import json
import requests
import re
import os



# use context for SSL
#context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

HOST = '109.195.230.198'  # Standard loopback interface address (localhost)
PORT = 8070


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
print('Binded port', PORT)
sock.listen(5) # limited to 5 connection in queue
while True:
	sock = None
	try:
		# поднимаем TCP сокет
		conn, addr = sock.accept()
		print('conn: ', conn)
		print('Connected by', addr)

		#	with context.wrap_socket(sock, server_side=True) as ssock:
		#		conn, addr = ssock.accept()
		#		print('conn: ', conn)
		#		print('Connected by', addr)

		# принимаем данные
		while True:
			data = conn.recv(200)
			print(type(data))

			if not data:
				break
			# здесь бы проверить цельность данных и можно ли их проверить

			data = data.decode()
			headers = data.split('\r\n', -1)
			pattern = re.compile(".*token=.*")
			result = [s for s in headers if pattern.search(s)]
			print(result)
			attrib_list = re.split('&', result[0])
			attrib_dict = dict()

			for i in attrib_list:
				splitted_att = re.split('=', i)
				attrib_dict[splitted_att[0]] = splitted_att[1]
			print(attrib_dict)
			# Проверяю валидность токена из прилетевшего запроса
			got_token = attrib_dict['token']
			print('Token = ', got_token)
			for val in os.environ.values():
				if val == got_token:
					print('True token = ',val, 'Got token', got_token)
	except KeyboardInterrupt:
		if sock:
			sock.close()
		break


# Re-create hooks that were used in non-secured connections



