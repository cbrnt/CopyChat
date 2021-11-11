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



while True:
	sock = None
	try:
		# поднимаем TCP сокет
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((HOST, PORT))
		print('Binded port', PORT)
		sock.listen(5)  # limited to 5 connection in queue
		conn, addr = sock.accept()
		print('conn: ', conn)
		print('Connected by', addr)

		#	with context.wrap_socket(sock, server_side=True) as ssock:
		#		conn, addr = ssock.accept()
		#		print('conn: ', conn)
		#		print('Connected by', addr)

		# принимаем данные
		while True:
			data = conn.recv(1024)
			# проверь потом с большим текстовым сообщением
			print(type(data))


			if not data:
				print('No data received. Data = ', data)
				print('Going to next loop iteration')
				break
			# здесь бы проверить цельность данных и можно ли их проверить
			else:
				data = data.decode()
				headers = data.split('\r\n', -1)
				print('Headers: ', headers)
				pattern = re.compile(".*token=.*")
				result = [s for s in headers if pattern.search(s)]
				if result:
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
					#true_token = os.environ.values()
					true_token = 'npgVipKxFSz1iRdQoDorDuM6'
					for val in os.environ.values():
						if true_token == got_token:
							print('True token = ', val, 'Got token', got_token)
						else:
							print('Token is not valid. Hacker?')
				else:
					print( 'So odd. Data received, headers in place, but Result is empty! Breaking loop iteration and going to next')
					break





	except KeyboardInterrupt:
		if sock:
			sock.close()
		break


# Re-create hooks that were used in non-secured connections



