# -*- coding: utf-8 -*-

import MySQLdb

from django.template import loader
from django.db.models import Q

from broker.decorators.decorators import signal, callback
from broker.meta import BaseClassMeta
from .models import Source as SourceModel


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

    def as_sql(self, template_name, params={}):
        """
        Возращает sql строку по ее типу
        :param template: string тип запроса
        :param params: dict параметры запроса
        :return: string
        """
        tmpl = loader.get_template(template_name)
        return tmpl.render(params)

    def __convert_q_object_to_list(self, q_object):
        """
        Преобразует Q объект к кортежу

        Объект Q(field1__gt=10, field2__lte=20) преобразуем в кортеж вида
        ('field1', 'gt', 10), 'AND', ('field2', 'lt', 20), а
        Q(Q(field1__gt=10) | Q(field2__lte=20)) & Q(field3=0) соответственно в

        (('field1', 'gt', 10), 'OR', ('field2', 'lt', 20)), 'AND', ('field3', '', 0)

        :param q_object: Q
        :return: tuple
        """

        # элемент Q(Q(field1__gt=10) | Q(field2__lte=20)) & Q(field3=0)
        # представляется в виде
        # {
        #   'children': [<Q: (OR: ('field1__gt', 10), ('field2__lte', 20))>, ('field3', 0)],
        #   'connector': u'AND',
        #   'negated': False
        # }
        items = []
        separator = '__'
        for child in q_object.children:
            if isinstance(child, Q):
                items.append(self.__convert_q_object_to_list(child))
            else:
                if items:
                    items.append(q_object.connector)
                lsh, rsh = child[0], child[1]
                if lsh.count(separator) != 1:
                    items.append((lsh, '', rsh))
                else:
                    items.append(tuple(lsh.split(separator)) + (rsh,))
        return items

    def prepare_condition(self, where):
        """
        Преобразует where в набор условий

        :param where: Q object or dict
            словарь будет преобразован в Q объект по умолчанию, например:
            словарь вида {'field1__gt': 10, 'field2__lte': 20} будет
            представлен Q(field1__gt=10, field2__lte=20)
        :return: tuple
        """
        condition = tuple()
        if where:
            # {
            #   'children': [<Q: (OR: ('field1__gt', 10), ('field2__lte', 20))>, ('field3', 0)],
            #   'connector': u'AND',
            #   'negated': False
            # }
            # Просматриваем элементы children, соединяя между собой
            # connector'ом. Если встречаемый элемент Q объект, анализируем по
            # рекурсии.
            condition = self.__convert_q_object_to_list(
                Q(**where) if isinstance(where, dict) else where
            )
        return condition

    def as_select_sql(self, table=None, fields=[], where=[], order_by=[],
                      limit=[]):
        """
        Возвращает sql строку типа "SELECT" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param fields: list список полей
        :param where: list список условий
        :param order_by: list список сортировки
            например: ['name', '-price']
        :param limit: list список ограничений
            например: [0, 100]
        :return: string
        """
        raise NotImplemented

    def as_update_sql(self, table=None, values={}, where=[]):
        """
        Возвращает sql строку типа "UPDATE" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param value: словарь значений
        :param where: list список условий
        :return: string
        """
        raise NotImplemented

    def as_insert_sql(self, table=None, values={}):
        """
        Возвращает sql строку типа "INSERT" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param value: словарь значений
        :return: string
        """
        raise NotImplemented

    def as_delete_sql(self, table=None, where=[]):
        """
        Возвращает sql строку типа "DELETE" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param where: list список условий
        :return: string
        """
        raise NotImplemented


class MysqlQueryException(Exception):
    """
    Возникает при формировании Mysql запроса
    """
    pass


class MysqlQuery(SqlQuery):
    """
    Объект Query для mysql
    """
    # SQL операции сравнения
    lookups = {
        '': '=',
        'gt': '>',
        'gte': '>=',
        'lt': '<',
        'lte': '<=',
    }
    # SQL шаблоны под каждый тип запроса
    select_template = "broker/sql/mysql/mysql_select.html"
    update_template = "broker/sql/mysql/mysql_update.html"
    insert_template = "broker/sql/mysql/mysql_insert.html"

    def __condition_as_sql(self, conditions):
        """
        Преобразует кортеж условий в строку sql

        кортеж (('field1', 'gt', 10), 'OR', ('field2', 'lt', 20)), 'AND', ('field3', '', 0)
        будет преобразован в ((`field1` > 10) OR (`field2` < 20)) AND (field3 = 0)

        :param conditions: tuple условий
        :return: string
        """
        connectors = set(['OR', 'AND'])
        sql = ''
        for condition in conditions:
            if isinstance(condition, (list, tuple)):
                if connectors & set(condition):
                    sql += u' ( {0} ) '.format(self.__condition_as_sql(condition))
                else:
                    try:
                        sql += u' (`{0}` {1} "{2}") '.format(
                            condition[0],
                            self.lookups[condition[1]],
                            condition[2]
                        )
                    except KeyError:
                        raise MysqlQueryException(
                            u'Операция "{0}" не предусмотрена'.format(
                                condition[1]
                            )
                        )
            elif isinstance(condition, (str, unicode)):
                sql += u' {0} '.format(condition)
        return sql

    def as_select_sql(self, *args, **kwargs):
        """
        Возвращает sql строку типа "SELECT"

        :param table: string имя таблицы
        :param fields: list список полей
        :param where: Q object or dict
            допускается передача в виде объектов Q или словаря, который будет
            преобразован в соответствующий Q(...)
        :param order_by: list список сортировки
            например: ['name', '-price']
        :param limit: list список ограничений
            например: [0, 100]
        :return: string
        """
        params = {
            'conditions': self.__condition_as_sql(
                self.prepare_condition(kwargs.pop('where', None))
            )
        }
        params.update(kwargs)
        return self.as_sql(self.select_template, params)

    def as_update_sql(self, *args, **kwargs):
        """
        Возвращает sql строку типа "UPDATE"

        :param table: string имя таблицы
        :param values: dict обновляемых полей типа:
            {'field1': 'value1', 'field2': 'value2'}
        :param where: Q object or dict
            допускается передача в виде объектов Q или словаря, который будет
            преобразован в соответствующий Q(...)
        """
        params = {
            'conditions': self.__condition_as_sql(
                self.prepare_condition(kwargs.pop('where', None))
            )
        }
        params.update(kwargs)
        return self.as_sql(self.update_template, params)

    def as_insert_sql(self, *args, **kwargs):
        """
        Возвращает sql строку типа "INSERT"

        :param table: string имя таблицы
        :param data: dict добавляемых полей типа:
            {'field1': 'value1', 'field2': 'value2'}
        """
        data = kwargs.pop('data', {})
        params = {
            'fields': data.keys(),
            'values': data.values()
        }
        params.update(kwargs)
        return self.as_sql(self.insert_template, params)


class DataBaseSourse(Source):
    """
        Класс, описывающий тип источника "База данных"
    """
    type_source = "db"
    connector = None
    cursor = None
    query = SqlQuery()

    def __init__(self, *args, **kwargs):
        super(DataBaseSourse, self).__init__(*args, **kwargs)
        # определяем параметры источника - БД
        try:
            # Инициализируем connector для работы с бд
            self.connector = self.get_connector(
                self.source_model.get_init_params()
            )
            self.cursor = self.connector.cursor()
        except Exception as e:
            raise DBConnectError(e.message)

    def get_connector(self, params={}):
        """
        Возвращает connector к бд
        :return: Connection
        """
        raise NotImplemented

    def select(self, *args, **kwargs):
        """
            Выполняет "select" запрос

            В **kwargs передаем:
                table - имя таблицы
                fields - список полей
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
        self.cursor.execute(self.query.as_update_sql(*args, **kwargs))
        self.connector.commit()

    def insert(self, *args, **kwargs):
        """
            Выполняет "insert" запрос

            В **kwargs передаем:
                table - имя таблицы
                value - сохраняемые значения
        """
        self.cursor.execute(self.query.as_insert_sql(*args, **kwargs))
        self.connector.commit()

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

    def get_connector(self, params={}):
        """
        Возвращает коннектор к бд MySQL
        :param params: параметры бд для подключения
        :return: Connection
        """
        return MySQLdb.connect(**params)


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
