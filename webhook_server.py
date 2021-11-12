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

DEBUG = 1


while True:
	sock = None
	try:
		# поднимаем TCP сокет
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((HOST, PORT))
		if DEBUG:
			print('Binded port', PORT)
		sock.listen(5)  # limited to 5 connection in queue

		#	with context.wrap_socket(sock, server_side=True) as ssock:
		#		conn, addr = ssock.accept()
		#		print('conn: ', conn)
		#		print('Connected by', addr)

		# принимаем данные
		while True:
			conn, addr = sock.accept()
			if DEBUG:
				print('conn: ', conn)
				print('Connected by', addr)

			data = conn.recv(1024)
			# проверь потом с большим текстовым сообщением

			if data:
				data = data.decode()
				headers = data.split('\r\n', -1)
				if DEBUG:
				    print('Headers: ', headers)
				pattern = re.compile(".*token=.*")
				result = [s for s in headers if pattern.search(s)]
				if result:
					if DEBUG:
						print(result)
					attrib_list = re.split('&', result[0])
					attrib_dict = dict()
					for i in attrib_list:
						splitted_att = re.split('=', i)
						attrib_dict[splitted_att[0]] = splitted_att[1]
					if DEBUG:
						print(attrib_dict)
						print(type(attrib_dict))

					# Проверяю валидность токена из прилетевшего запроса
					got_token = attrib_dict['token']
					if DEBUG:
						print('os.environ.values() = ',os.environ.values())
					env_vars = os.environ.values()
					if DEBUG:
					    print('env_vars = ', env_vars)
					token_check_result = list((val for val in iter(env_vars) if val == got_token))
					if DEBUG:
					    print('token_check_result = ',token_check_result)
					if len(token_check_result) == 1:
						if DEBUG:
							valid_token = token_check_result[0]
							print('Got valid token: %s' % valid_token)
						got_channel_name = attrib_dict['channel_name']
						got_text = attrib_dict['text']
						if DEBUG:
							print('got_channel = ', got_channel_name)
							print('got_text = ', got_text)
							
						
					else:
						if DEBUG:
							print('Token is not valid')

				else:
					if DEBUG:
						print( 'So odd. Data received, headers in place, but Result is empty! Breaking loop iteration and going to next')
					break





	except KeyboardInterrupt:
		if sock:
			sock.close()
		break


# Re-create hooks that were used in non-secured connections



