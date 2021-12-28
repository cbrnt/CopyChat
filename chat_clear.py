import logging
import time

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


def get_threads(messages_dict, channel_id_func):
    """получает словарь с сообщениями из канала и ищет для них треды.
    Возвращает словать вида 'ts: thread_ts1, thread_ts2, ...'"""
    ts_dict = {}
    get_tds = requests.Session()
    get_tds.headers = {'Authorization': 'Bearer %s' % bot_token,
                       'Content-type': 'application/x-www-form-urlencoded'}
    for message in messages_dict.get('messages'):
        if message.get('thread_ts'):
            data = {'channel': '%s' % channel_id_func, 'ts': '%s' % message['thread_ts']}
            request = requests.post('https://slack.com/api/conversations.replies',
                                    headers=headers,
                                    data=data)
            get_ts_messages_json = request.json()
            if request.status_code == 200 and get_ts_messages_json['ok']:
                for msg in get_ts_messages_json['messages']:
                    if msg.get('client_msg_id'):
                        if not ts_dict.get(message['ts']):
                            ts_dict[message['ts']] = list()
                        ts_dict[message['ts']].append(msg['ts'])
            else:
                logging.warning('Ошибка: %s' % request.text)
                return False
        else:
            ts_dict[message['ts']] = []
    return ts_dict


def remove_messages(message_dict):
    """принимает словарь с ts сообщений и ts потомков. Удаляет снала треды, затем их родителей"""
    slack_session = requests.Session()
    # готовим токены
    slack_session.headers = {
        'Authorization': 'Bearer %s' % user_token,
        'Content-type': 'application/x-www-form-urlencoded'
    }
    for iter_ts in message_dict.values():
        for tts in iter_ts:
            time.sleep(5)
            data = {'channel': '%s' % channel_id, 'ts': '%s' % tts, 'as_user': 'true'}
            remove = slack_session.post('https://slack.com/api/chat.delete', data=data)
            remove_json = remove.json()
            if remove.status_code != 200 and not remove_json['ok']:
                logging.warning('Ошибка: %s' % remove.text)
                return False
    for ts in message_dict.keys():
        time.sleep(5)  # нельзя слишком быстро делать запросы к API
        # print('keys:', 'ts', ts)
        data = {'channel': '%s' % channel_id, 'ts': '%s' % ts, 'as_user': 'true'}
        # print('tts', ts)
        remove_ts = slack_session.post('https://slack.com/api/chat.delete', data=data)
        remove_json = remove_ts.json()
        if remove_ts.status_code != 200 and not remove_json['ok']:
            logging.warning('Ошибка: %s' % remove_ts.text)
            return False
    return True


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
                data_get_history = {'channel': '%s' % channel_id, 'limit': '100', 'latest': '%s' % search_date}
                # делаем запрос истории сообщений
                get_history = requests.post('https://slack.com/api/conversations.history', headers=headers,
                                            data=data_get_history)
                if get_history.status_code == 200:
                    get_history = get_history.json()
                    if get_history['ok']:
                        get_ts_dict = get_threads(get_history, channel_id)
                        result = remove_messages(get_ts_dict)
                        if not remove_messages(get_ts_dict):
                            logging.warning('Часть сообщений не были удалены')
                    else:
                        logging.warning('Ошибка при получении истории сообщений')
