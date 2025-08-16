import psycopg2
from loggers import logger


class PSDataBase:

    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
                )
        except Exception as error:
            logger.error("Error to connect db " + str(error))


    def _connect(self):
            """Создание нового соединения"""
            try:
                return psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
            except Exception as error:
                logger.error("Error to connect db: {}".format(str(error)))
                raise


    def get_rows(self, full_query, params=None):
        """
        Универсальная функция для извлечения данных из базы данных.
        Работает как с параметрами (params), так и без них.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                if params is not None:
                    cur.execute(full_query, list(params.values()))
                else:
                    cur.execute(full_query)
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                transformed_rows = [dict(zip(columns, row)) for row in rows]
        except Exception as error:
            logger.error("Error in query: {}, error: {}".format(full_query, str(error)))
            return []
        finally:
            self.close_connection(conn)
        return transformed_rows


    def insert_data(self, table_name: str, field_names: list, data):
            """Записываем данные из словаря в таблицу """
            returning_clause = "RETURNING id"
            if isinstance(data, list):
            # Если передан список, создаем фиктивный ключ и используем этот список
                data_dict = {"_default": data}
            else:
                data_dict = data
            result = None
            for user_id, user_values in data_dict.items():
                fields_str = ", ".join(field_names)
                placeholders = ', '.join(['%s'] * len(user_values))
                query = "INSERT INTO {} ({}) VALUES ({}) {};".format(table_name, fields_str, placeholders, returning_clause)
                try:
                    conn = self._connect()
                    with conn.cursor() as cur:
                        cur.execute(query, tuple(user_values))
                        result = cur.fetchone()
                    self.conn.commit()
                except Exception as error:
                    logger.error("Error to insert data from dict: {}".format(str(error)))
            return result
    

    def insert_list(self, table_name: str, field_names: list, data: list):
        """ Записываем данные из списка в таблицу """
        returning_clause = "RETURNING id"
        fields_str = ", ".join(field_names)
        placeholders = ', '.join(['%s'] * len(data))
        query = "INSERT INTO {} ({}) VALUES ({}) {};".format(table_name, fields_str, placeholders, returning_clause)
        result = None
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(query, tuple(data))
                result = cur.fetchone()
            conn.commit()
        except Exception as error:
            logger.error("Error to insert data from list: {}".format(str(error)))
        finally:
            conn.close()
        return result
    

    def update_comment(self, table_name: str, comment: str, key: str):
        """ Записываем комментарий в таблицу по уникальному ключу документа"""
        query = "UPDATE {} SET comment=%s WHERE document_unique_key=%s;".format(table_name)
        try:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(query, (comment, key))
            conn.commit()
            return True
        except Exception as error:
            logger.error("Error to update comment: {}".format(str(error)))
            return False
        finally:
            conn.close()
        
        
    def close_connection(self, connection):
        """Закрытие текущего соединения"""
        if connection:
            connection.close()


def debug_sql(query, parameters=None):
    if parameters is None:
        return query
    return query % tuple(map(repr, parameters))


def show_full_query(query_template, params):
    values = map(repr, params.values())
    full_query = query_template % tuple(values)
    return full_query