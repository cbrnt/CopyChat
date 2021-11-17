#!/usr/bin/env python3

import socket
import ssl
import json
import requests
import re
import os
import urllib.parse

HOST = '109.195.230.198'
PORT = 8070
DEBUG = 1
CERT = '/etc/letsencrypt/live/gate.tochkak.ru/fullchain.pem'
PRIVATE_CERT = '/etc/letsencrypt/live/gate.tochkak.ru/privkey.pem'


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT, PRIVATE_CERT)

while True:
	sock = None
	try:
		# поднимаем TCP сокет
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind((HOST, PORT))
		if DEBUG:
			print('Binded port', PORT)
		sock.listen(5)  # limited to 5 connection in queue
		# оборачиваем в SSL и принимаем дату для каждого нового соежинения
		ssock = context.wrap_socket(sock, server_side=True)

		while True:
			conn, addr = ssock.accept()
			data = conn.recv(1024)
			if DEBUG:
				print('conn: ', conn)
				print('Connected by', addr)
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
					env_vars = os.environ.values()
					token_check_result = list((val for val in iter(env_vars) if val == got_token))
					if DEBUG:
						print('token_check_result = ',token_check_result)
					if len(token_check_result) == 1:
						if DEBUG:
							valid_token = token_check_result[0]
							print('Got valid token: %s' % valid_token)
					# токен нормальный, извлекаем данные
						got_channel_name = attrib_dict['channel_name']
						got_text = attrib_dict['text']
						got_text = urllib.parse.unquote(got_text)
						got_text = urllib.parse.unquote_plus(got_text)
						thread_ts = attrib_dict['thread_ts']

						if DEBUG:
							print('got_channel = ', got_channel_name)
							print('got_text = ', got_text)

						# получаем список каналов другого спейса
						bot_token = os.environ['SLACK_BOT_TOKEN']
						if DEBUG:
							print('bot_token = ', bot_token)
						headers = { 'Authorization': 'Bearer %s' %bot_token}
						if DEBUG:
							print('Headers for send request:', headers)
						channels_list = requests.get('https://slack.com/api/conversations.list',
													 headers=headers)
						if channels_list.status_code == 200:
							if DEBUG:
								print('channel_list status code: ', channels_list.status_code)
								print('channel_list text: ', channels_list.text)
								print('channel_list headers: ', channels_list.headers)
							channels_dict = channels_list.json()
							print('Type channels_dict: ', type(channels_dict))
							print('channels_dict = ', channels_dict)
							print('id = ', channels_dict['channels'])
							channels = channels_dict['channels']
							username = attrib_dict['user_name']
							timestamp = attrib_dict['timestamp']
							for channel in range(len(channels)):
								print(channels[channel]['id'],channels[channel]['name'])
								if channels[channel]['name'] == got_channel_name:
									channel_id = channels[channel]['id']
									if DEBUG:
										print('channel_id = ', channel_id)
									headers = {'Authorization': 'Bearer %s' % bot_token, 'Content-type': 'application/json'}
									if DEBUG:
										print('Headers for send request:', headers)
									json = {"channel": "%s" % channel_id,
											"text": "%s" % got_text,
											"username": "%s" % username,
											"thread_ts": "%s" % thread_ts, "timestamp": "%s" % timestamp}
									if DEBUG:
										print('json = ', json)
									channels_list = requests.post('https://slack.com/api/chat.postMessage', headers=headers, json=json)


					else:
						if DEBUG:
							print('Token is not valid')
					# токена нет в окружении, значит не пересылаем сообщение, ждем следуюшего

				else:
					if DEBUG:
						print( 'Data received but "result" is empty... Going next loop iteration!')






	except KeyboardInterrupt:
		if ssock:
			ssock.close()
			if sock:
				sock.close()
		break


# Re-create hooks that were used in non-secured connections



