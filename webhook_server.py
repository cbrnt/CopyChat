#!/usr/bin/env python3

import socket
import ssl
import requests
import re
import os
import urllib.parse

SLACK_TOCHKAK_BOT_TOKEN = os.environ['SLACK_TOCHKAK_BOT_TOKEN']
HOST = '0.0.0.0'
PORT = 8070
DEBUG = 1
CERT = '/etc/letsencrypt/live/gate.tochkak.ru/fullchain.pem'
PRIVATE_CERT = '/etc/letsencrypt/live/gate.tochkak.ru/privkey.pem'

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT, PRIVATE_CERT)


def get_name(user_id_list, slack_token=SLACK_TOCHKAK_BOT_TOKEN):
    """Получаает slack user id и возвращает список из кортежей"""
    headers_func = {'Authorization': 'Bearer %s' % slack_token,
                    'Content-type': 'application/x-www-form-urlencoded'
                    }
    get_list = requests.post('https://slack.com/api/users.list', headers=headers_func, timeout=10)
    if get_list.status_code == 200:
        users_list = get_list.json()
        name_list = []
        if users_list.get('ok'):
            for user_id in user_id_list:
                for user in users_list['members']:
                    if user.get('id') == user_id:
                        name_list.append((user.get('id'), user.get('real_name')))
            return name_list
    return False


def find_id(text):
    """Находит и возвращает список ID slack"""
    # pattern_func = re.compile(r'<@U\w+>')
    pattern_func = re.compile(r"<@U\w+>")
    result_func = pattern_func.findall(text)
    for itr in range(len(result_func)):
        result_func[itr] = result_func[itr].replace('<@', '')
        result_func[itr] = result_func[itr].replace('>', '')
    return result_func


def id_to_name_text(text):
    """Заменяет slack ID на нормальные имена"""
    get_id_list = find_id(text)
    get_name_list = get_name(get_id_list)
    for id_name in get_name_list:
        final_text = text.replace('<@' + id_name[0] + '>', id_name[1])
    return final_text

while True:
    sock = None
    try:
        # поднимаем TCP сокет
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        if DEBUG:
            print('Bound port: ', PORT)
        sock.listen(5)  # limited to 5 connection in queue
        # оборачиваем в SSL и принимаем дату для каждого нового соежинения
        ssock = context.wrap_socket(sock, server_side=True)

        while True:
            conn, addr = ssock.accept()
            data = conn.recv(30000)
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
                    for itr in attrib_list:
                        splitted_att = re.split('=', itr)
                        attrib_dict[splitted_att[0]] = splitted_att[1]
                    if DEBUG:
                        print(attrib_dict)
                        print(type(attrib_dict))

                    # Проверяю валидность токена из прилетевшего запроса
                    got_token = attrib_dict['token']
                    env_vars = os.environ.values()
                    token_check_result = list((val for val in iter(env_vars) if val == got_token))
                    if DEBUG:
                        print('token_check_result = ', token_check_result)
                    if len(token_check_result) == 1:
                        valid_token = token_check_result[0]
                        if DEBUG:
                            print('Got valid token: %s' % valid_token)

                        # токен нормальный, извлекаем данные
                        got_channel_name = attrib_dict['channel_name']
                        got_text = attrib_dict['text']
                        got_text = urllib.parse.unquote(got_text)
                        got_text = urllib.parse.unquote_plus(got_text)

                        if DEBUG:
                            print('got_channel = ', got_channel_name)
                            print('got_text = ', got_text)

                        # парсим из текста slack user id и подставляем имя


                        # получаем список каналов другого спейса
                        bot_token = os.environ['SLACK_BOT_TOKEN']
                        if DEBUG:
                            print('bot_token = ', bot_token)
                        headers = {'Authorization': 'Bearer %s' % bot_token}
                        if DEBUG:
                            print('Headers for send request:', headers)
                        channels_list = requests.get('https://slack.com/api/conversations.list',
                                                     headers=headers, timeout=10)
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
                            for channel in range(len(channels)):
                                print(channels[channel]['id'], channels[channel]['name'])
                                if channels[channel]['name'] == got_channel_name:
                                    channel_id = channels[channel]['id']
                                    if DEBUG:
                                        print('channel_id = ', channel_id)
                                    headers = {'Authorization': 'Bearer %s' % bot_token,
                                               'Content-type': 'application/json'}
                                    if DEBUG:
                                        print('Headers for send request:', headers)
                                    text_to_slack = id_to_name_text(got_text)
                                    json = {"channel": "%s" % channel_id,
                                            "text": "%s" % text_to_slack,
                                            "username": "%s" % username}
                                    if DEBUG:
                                        print('json = ', json)
                                    channels_list = requests.post('https://slack.com/api/chat.postMessage',
                                                                  headers=headers, json=json, timeout=10)

                    else:
                        if DEBUG:
                            print('Token is not valid')
                # токена нет в окружении, значит не пересылаем сообщение, ждем следуюшего

                else:
                    if DEBUG:
                        print('Data received but "result" is empty... Going next loop iteration!')

    except KeyboardInterrupt:
        if ssock:
            ssock.close()
            if sock:
                sock.close()
        break
