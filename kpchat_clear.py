#!/usr/bin/env python3

import socket
import ssl
import json
import requests
import re
import os
import urllib.parse
import datetime
import time

DEBUG = True


# получаем список каналов
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
			headers = {'Authorization': 'Bearer %s' % bot_token, 'Content-type': 'application/x-www-form-urlencoded'}
			if DEBUG:
				print('Headers for send request:', headers)
			# делаем запрос истории сообщений
			data = 'channel=%s' % channel_id
			if DEBUG:
				print('json = ', json)
			messages = requests.post('https://slack.com/api/conversations.history', headers=headers, data=data)
			if DEBUG:
				print('Messages:')
				print(messages.headers)
				print(messages.text)
			messages = messages.json()
			for message in range(len(messages.get('messages'))):
				print(messages.get('messages')[message].get('ts'))
				current_time = datetime.now
				if DEBUG:
					print('current_time', current_time)
				last_month = datetime.now[1] - 1
				if DEBUG:
					print('last_month= ', last_month)
				unix_time = time.mktime(last_month)
				if DEBUG:
					print('unix_time= ', unix_time)
				unix_time_turple = time.mktime(last_month.timetuple())
				if DEBUG:
					print('unix_time_turple= ', unix_time_turple)



