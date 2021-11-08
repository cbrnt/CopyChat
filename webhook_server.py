#!/usr/bin/env python3

import socket
import ssl

# use context for SSL
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

HOST = '109.195.230.198'  # Standard loopback interface address (localhost)
PORT = 8070


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	sock.bind((HOST, PORT))
	print('Binded port', PORT)
	sock.listen(5) # limited to 5 connection in qeueue

	with context.wrap_socket(sock, server_side=True) as ssock:
		conn, addr = ssock.accept()
		print('conn: ', conn)
		print('Connected by', addr)

	while True:
		data = conn.recv(1024)
		if not data:
			break
		print('Data: ', data)

#wantt0Know