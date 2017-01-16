# -*- coding: utf-8 -*-


class DBConnectError(Exception):
    """
        Исключение при невозможности подключиться к базе данных источника
    """
    pass


class MysqlQueryException(Exception):
    """
    Возникает при формировании Mysql запроса
    """
    pass
