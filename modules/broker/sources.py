# -*- coding: utf-8 -*-

from django.conf import settings

from broker.decorators.decorators import signal, callback
from broker.meta import BaseClassMeta

from .models import Source as SourceModel
from .helpers import get_db_allias_for_source


class BaseClass(object):
    """
        Базовый класс
    """
    __metaclass__ = BaseClassMeta

    # По умолчанию, класс является промежуточным звеном между инстансом и
    # базовым классом. В классе реального источника, нужно установить False
    is_proxy = True


class Source(BaseClass):
    """
        Базовый класс для всех источников
    """
    type_source = None
    source_model = None

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__()
        cls_name = self.__class__.__name__
        try:
            self.source_model = SourceModel.objects.get(source=cls_name)
        except SourceModel.DoesNotExist:
            raise ValueError("Source '{}' not has object of model"
                             .format(cls_name))


class SqlQuery(object):
    """
    Объект Query

    Позволяет сформировать sql строку конкретного типа
    """
    def as_select_sql(self, table, where=[], order_by=[], limit=[]):
        """
        Возвращает sql строку типа "SELECT" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param where: list список условий
        :param order_by: list список сортировки
            например: ['name', '-price']
        :param limit: list список ограничений
            например: [0, 100]
        :return: string
        """
        raise NotImplemented

    def as_update_sql(self, table, value={}, where=[]):
        """
        Возвращает sql строку типа "UPDATE" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param value: словарь значений
        :param where: list список условий
        :return: string
        """
        raise NotImplemented

    def as_insert_sql(self, table, value={}):
        """
        Возвращает sql строку типа "INSERT" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param value: словарь значений
        :return: string
        """
        raise NotImplemented

    def as_delete_sql(self, table, where=[]):
        """
        Возвращает sql строку типа "DELETE" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param where: list список условий
        :return: string
        """
        raise NotImplemented


class MysqlQuery(SqlQuery):
    """
    Объект Query для mysql
    """
    pass


class DataBaseSourse(Source):
    """
        Класс, описывающий тип источника "База данных"
    """
    type_source = "db"
    cursor = None
    query = SqlQuery()

    def __init__(self, *args, **kwargs):
        super(DataBaseSourse, self).__init__(*args, **kwargs)
        # определяем параметры источника - БД
        try:
            db_alias = get_db_allias_for_source(self.source_model.source)
            self.cursor = settings.CONNECTIONS_SOURCES[db_alias].cursor()
        except Exception as e:
            raise DBConnectError(e.message)

    def select(self, *args, **kwargs):
        """
            Выполняет "select" запрос

            В **kwargs передаем:
                table - имя таблицы
                where - условия выборки
                order_by - условия сортировки
                limit - условия ограничения
        """
        self.cursor.execute(self.query.as_select_sql(*args, **kwargs))
        return self.cursor.fetchall()

    def update(self, *args, **kwargs):
        """
            Выполняет "update" запрос

            В **kwargs передаем:
                table - имя таблицы
                value - устанавливаемые значения
                where - условия выборки
        """
        return self.cursor.execute(self.query.as_update_sql(*args, **kwargs))

    def insert(self, *args, **kwargs):
        """
            Выполняет "insert" запрос

            В **kwargs передаем:
                table - имя таблицы
                value - сохраняемые значения
        """
        return self.cursor.execute(self.query.as_insert_sql(*args, **kwargs))

    def delete(self, *args, **kwargs):
        """
            Выполняет "delete" запрос

            В **kwargs передаем:
                table - имя таблицы
                where - условия выборки
        """
        return self.cursor.execute(self.query.as_delete_sql(*args, **kwargs))


class MysqlDBSource(DataBaseSourse):
    """
        Класс mysql источника
    """
    def __init__(self, *args, **kwargs):
        super(MysqlDBSource, self).__init__(*args, **kwargs)
        # определяем параметры источника - mysql БД


""" Инстансы источников """


class Wsdl(Source):
    """
        Класс источника Wsdl
    """
    type_source = "wsdl"

    is_proxy = False

    def __init__(self, *args, **kwargs):
        super(Wsdl, self).__init__(*args, **kwargs)


class KmClient(MysqlDBSource):
    """
        Класс источника KmClient
    """
    is_proxy = False
    query = MysqlQuery()

    def __init__(self, *args, **kwargs):
        super(KmClient, self).__init__(*args, **kwargs)

    @signal()
    def km_signal_1(self):
        pass

    @callback
    def km_callback_1(self, *args, **kwargs):
        pass


class DBConnectError(Exception):
    """
        Исключение при невозможности подключиться к базе данных источника
    """
    pass
