#!/usr/bin/env python3

import socket
import ssl
import json
import requests
import re
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


# use context for SSL
#context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

HOST = '109.195.230.198'  # Standard loopback interface address (localhost)
PORT = 8070


def get_value(raw_list, parameter):
	re_obj = re.compile('%s=*' % parameter)
	print('re_obj = ', re_obj)
	value = list(filter(re_obj.match, raw_list))
	print('%s: ' % parameter, value)
	return value

try:
	app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
	if __name__ == "__main__":
		SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

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
				# add token verification!!!

	# Create Slack API connection



# TEST_OUT_WEBHOOK_TOKEN


# Re-create hooks that were used in non-secured connections

except KeyboardInterrupt:
	sock.close()

