import json
import requests
import os

from datetime import datetime

import pandas as pd



# todo добавь чтение хука из первого аргумента
CHANNEL = 'test-out-hooks'

# получаем список каналов
bot_token = os.environ['SLACK_BOT_TOKEN']

headers = {'Authorization': 'Bearer %s' % bot_token}

channels_list = requests.get(
	'https://slack.com/api/conversations.list',
	headers=headers
)
if channels_list.status_code == 200:
	channels_dict = channels_list.json()

	channels = channels_dict['channels']
	for channel in range(len(channels)):
		if channels[channel]['name'] == CHANNEL:
			channel_id = channels[channel]['id']
			headers = {'Authorization': 'Bearer %s' % bot_token, 'Content-type': 'application/x-www-form-urlencoded'}
			# делаем запрос истории сообщений
			search_date = (datetime.today() - pd.DateOffset(months=2)).strftime("%d-%m-%Y")
			data = {'channel': '%s' % channel_id, 'limit': '1000', 'oldest': '%s' % search_date}
			messages = requests.post('https://slack.com/api/conversations.history', headers=headers, data=data)
			messages = messages.json()
			a = len(messages)
			# for message in range(len(messages.get('messages'))):
			# 	current_date = date.today()
				# last_month_date = current_date.replace(month=current_date.month - 1)
				# unix_time_last_month = time.mktime(last_month_date.timetuple())

# https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#from-timestamps-to-epoch


