import json
import uuid

from datetime import datetime
from loggers import logger


def format_time(t_string):
    try:
        dt_object = datetime.strptime(t_string, '%d.%m.%Y')
    except ValueError:
        dt_object = datetime.strptime(t_string, '%Y-%m-%d')
    return dt_object.strftime('%Y-%m-%d')


def get_unique_id():
    """формируем уникальный идентификатор для многопользовательского режима"""
    timer = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    return timer, str(uuid.uuid4())


def save_state(config_dict, filename='state.json'):
    """Сохранить состояние в JSON."""
    state = {
        "dbname": config_dict['dbName'],
        "dbport": config_dict['dbPort'],
        "dbhost": config_dict['dbHost'],
        "dbuser": config_dict['dbUser'],
        "dbpassword": config_dict['dbPassword'], 
        "docPath" : config_dict['docPath']
    }
    with open(filename, 'w') as file:
        json.dump(state, file)


def load_state(filename='state.json'):
    """Загрузить состояние из JSON."""
    config_dict  = {}
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            config_dict['dbName'] = data.get("dbname")
            config_dict['dbPort'] = data.get("dbport")
            config_dict['dbHost'] = data.get("dbhost")
            config_dict['dbUser'] = data.get("dbuser")
            config_dict['dbPassword'] = data.get("dbpassword")
            config_dict['docPath'] = data.get( "docPath")
            return config_dict
    except FileNotFoundError:
        logger.error('State file not found')
        return {}
    

def tuple_to_dict(row, columns):
    """Преобразует кортеж в словарь."""
    return dict(zip(columns, row))


def debug_sql(query, parameters=None):
    if parameters is None:
        return query
    return query % tuple(map(repr, parameters))

