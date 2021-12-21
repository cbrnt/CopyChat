import requests
import os

import pandas as pd

import time



# todo добавь чтение хука из первого аргумента
CHANNEL = 'kpchat'

# получаем список каналов
bot_token = os.environ['SLACK_BOT_TOKEN']
user_token = os.environ['SLACK_USER_TOKEN']

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
			# считаем время
			now = pd.Timestamp.today()
			two_months_ago = now - pd.DateOffset(months=1)
			search_date = ((two_months_ago - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'))
			data_get_history = {'channel': '%s' % channel_id, 'limit': '1000', 'latest': '%s' % search_date}
			# делаем запрос истории сообщений
			get_history = requests.post('https://slack.com/api/conversations.history', headers=headers, data=data_get_history)
			if get_history.status_code == 200:
				get_history = get_history.json()
			for message in get_history.get('messages'):
				ts = message['ts']
				data_to_del = {'channel': '%s' % channel_id, 'ts': '%s' % ts, 'as_user': 'true'}
				headers = {
					'Authorization': 'Bearer %s' % user_token,
					'Content-type': 'application/x-www-form-urlencoded'
				}
				# можно сделать через Sessions, чтобы не поднимать каждый раз TCP соединение
				del_messages = requests.post('https://slack.com/api/chat.delete', headers=headers, data=data_to_del)
				time.sleep(2)





