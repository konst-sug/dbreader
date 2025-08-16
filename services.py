from funcs import format_time
from datetime import datetime
from loggers import logger


HISTORY_REQUEST = 'SELECT * FROM query_history ORDER BY date DESC LIMIT 10;'
DOCS_HISTORY = 'SELECT * FROM docs_history ORDER BY date DESC LIMIT 10;'

options = {}


def paginator(page, search_results, PAGE_SIZE):
    start_idx = (page - 1) * PAGE_SIZE
    total_items = len(search_results)
    if start_idx >= total_items:
         return {"detail": "Страница вне допустимого диапазона"}
    end_idx = min(start_idx + PAGE_SIZE, total_items)
    result = search_results[start_idx:end_idx]
    return result


def form_query(table: str, query_data: dict):
    base_query = "SELECT * FROM {}".format(table)
    where_conditions = []
    params = {}
    if query_data['SearchNameString']:
            where_conditions.append("publication_number LIKE %s")
            params['SearchNameString'] = "%{}%".format(query_data['SearchNameString'])
    if query_data['DateRangeStartString']:
            start_date_string = query_data['DateRangeStartString']
            where_conditions.append("publication_date >= %s")
            params['DateRangeStartString'] = format_time(start_date_string)
    if query_data['DateRangeEndString']:
            end_date_string = query_data['DateRangeEndString']
            where_conditions.append("publication_date <= %s")
            params['DateRangeEndString'] = format_time(end_date_string)

    if len(query_data['SelectedType']):
        where_conditions.append("doc_kind IN (%s)" % ", ".join(["%s"] * len(query_data['SelectedType'])))
        params.update({'SelectedType_{}'.format(i): val for i, val in enumerate(query_data['SelectedType'])})

    if len(query_data['SelectedRegPeriod']):
        where_conditions.append("doc_kind IN (%s)" % ", ".join(["%s"] * len(query_data['SelectedRegPeriod'])))
        params.update({'SelectedRegPeriod_{}'.format(i): val for i, val in enumerate(query_data['SelectedRegPeriod'])})

    if len(query_data['SelectedReg']):
        where_conditions.append("publishing_country IN (%s)" % ", ".join(["%s"] * len(query_data['SelectedReg'])))
        params.update({'SelectedReg_{}'.format(i): val for i, val in enumerate(query_data['SelectedReg'])})
    
    if len(where_conditions) > 0:
        conditions_sql = " AND ".join(where_conditions)
        full_query = "{} WHERE {}".format(base_query, conditions_sql)
    else:
        full_query = base_query
    return full_query, params


def format_options(data: list, query_history: list):
    """Добавление списка запросов в историю запросов."""
    try:
        for i in range(len(data)):
            opts = {
                "uq_id": data[i]['ur_id'],
                "value": "Запрос {}".format(data[i]['date']),
                "label": "Запрос {}".format(data[i]['date']),
                "query": data[i]['query'],
                "params": data[i]['params']
                    }
            query_history.append(opts)
    except Exception as error:
        logger.error('Error in {}: {} '.format(str(__name__), str(error)))   
    return query_history


def format_docs_options(data: list, docs_history: list):
    """Добавление списка запросов документов в историю запросов документов"""
    try:
        for r in range(len(data)):
            timer = data[r]['date'].strftime('%Y-%m-%d_%H:%M:%S')
            opts = {
                "value": data[r]['document_unique_key'],
                "label": "Документ:{}, Время:{}".format(data[r]['document_unique_key'], timer )}
            docs_history.append(opts)
    except Exception as error:
        logger.error('Error in {}: {} '.format(str(__name__), str(error)))     
    return docs_history


def load_select(database):
    """Загрузка истории запросов и просмотров из базы данных"""
    options['options1'] = []
    options['options2'] = []
    try:
        result = database.get_rows(HISTORY_REQUEST)
        options['options1'].clear()
        options['options1'] = format_options(result, options['options1'])
    except Exception as error:
        logger.error('Error in load select data 1: {}'.format(str(error)))
    try:
        result = database.get_rows(DOCS_HISTORY)
        options['options2'].clear()
        for r in range(len(result)):
            timer = result[r]['date'].strftime('%Y-%m-%d_%H:%M:%S')
            opts = {
                "value": result[r]['document_unique_key'],
                "label": "Документ:{}, Время:{}".format(result[r]['document_unique_key'], timer )}
            options['options2'].append(opts)
    except Exception as error:
        logger.error('Error in load select data 2: {}'.format(str(error)))
    return options
