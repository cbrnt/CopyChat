import requests
import os

import pandas as pd

import argparse

parser = argparse.ArgumentParser(description=' канал сообщений Slack')
parser.add_argument('--channel', metavar='CHANNEL_NAME',
                    dest='CHANNEL',
                    help='удалит старые сообщения из канала')
args = parser.parse_args()
CHANNEL = args.CHANNEL

# получаем список каналов
bot_token = os.environ['SLACK_BOT_TOKEN']
user_token = os.environ['SLACK_USER_TOKEN']

headers = {'Authorization': 'Bearer %s' % bot_token}

channels_list = requests.get('https://slack.com/api/conversations.list',
                             headers=headers)
if channels_list.status_code == 200:
    channels_dict = channels_list.json()
    if channels_dict['ok']:
        channels = channels_dict['channels']
        for channel in range(len(channels)):
            if channels[channel]['name'] == CHANNEL:
                channel_id = channels[channel]['id']
                headers = {'Authorization': 'Bearer %s' % bot_token, 'Content-type': 'application/x-www-form-urlencoded'}
                # считаем время
                now = pd.Timestamp.today()
                two_months_ago = now - pd.DateOffset(months=1)
                search_date = ((two_months_ago - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s'))
                # search_date = 1638219600
                data_get_history = {'channel': '%s' % channel_id, 'limit': '100', 'latest': '%s' % search_date}
                # делаем запрос истории сообщений
                get_history = requests.post('https://slack.com/api/conversations.history', headers=headers,
                                            data=data_get_history)
                if get_history.status_code == 200:
                    get_history = get_history.json()
                    if get_history['ok']:
                        # todo создай объект Session
                        for message in get_history.get('messages'):
                            ts = message['ts']
                            # todo нужно проверять есть ли thread_ts, если есть, то найти вложенные треды по ts этого сообщения
                            # https://api.slack.com/methods/conversations.replies
                            data_to_del = {'channel': '%s' % channel_id, 'ts': '%s' % ts, 'as_user': 'true'}
                            headers = {
                                'Authorization': 'Bearer %s' % user_token,
                                'Content-type': 'application/x-www-form-urlencoded'
                            }
                        del_messages = requests.post('https://slack.com/api/chat.delete', headers=headers, data=data_to_del)
print()
