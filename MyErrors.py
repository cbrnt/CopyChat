import logging


class DateMissError(Exception):
    def __init__(self, *args):
        if args:
            logging.warning('Не указан параметры --days или --months.'
                            ' Не могу выбрать дату, до которой нужно удалять сообщения')


class TeamMissError(Exception):
    def __init__(self, *args):
        if args:
            print('Укажи команду, где чистить канал')
