#!/usr/bin/env python3

import socket
import ssl
import json
import requests
import re
import os
import urllib.parse

DEBUG = True


while True:
	# получаем список каналов другого спейса
	bot_token = os.environ['SLACK_BOT_TOKEN']
	if DEBUG:
		print('bot_token = ', bot_token)
	headers = {'Authorization': 'Bearer %s' %bot_token}
	if DEBUG:
		print('Headers for send request:', headers)
	channels_list = requests.get(
		'https://slack.com/api/conversations.list',
		headers=headers
	)
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
		for channel in range(len(channels)):
			if DEBUG:
				print(channels[channel]['id'], channels[channel]['name'])
			if channels[channel]['name'] == 'kpchat':
				channel_id = channels[channel]['id']
				if DEBUG:
					print('channel_id = ', channel_id)
				headers = {'Authorization': 'Bearer %s' % bot_token, 'Content-type': 'application/json'}
				if DEBUG:
					print('Headers for send request:', headers)
				json = {
					"channel": channel_id
				}
				if DEBUG:
					print('json = ', json)
				channels_list = requests.get('https://slack.com/api/conversations.history', headers=headers, json=json)
				if DEBUG:
					print(channels_list)
