# -*- coding: utf-8 -*-

from django.db.models import Q
from django.template import loader

from broker.decorators.decorators_helpers import transaction_atomic
from broker.sources import Source
from broker.sources.exceptions import DBConnectError


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

        (('field1', 'gt', 10), 'OR', ('field2', 'lt', 20)), 'AND',
        ('field3', '', 0)

        :param q_object: Q
        :return: tuple
        """

        # элемент Q(Q(field1__gt=10) | Q(field2__lte=20)) & Q(field3=0)
        # представляется в виде
        # {
        #   'children': [<Q: (OR: ('field1__gt', 10),
        #                ('field2__lte', 20))>, ('field3', 0)],
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
            #   'children': [<Q: (OR: ('field1__gt', 10),
            #                ('field2__lte', 20))>, ('field3', 0)],
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
                      limit=[], for_update=False):
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
        :param for_update: использовать FOR UPDATE (по умолчанию False)
        :return: string
        """
        raise NotImplemented

    def as_update_sql(self, table=None, values={}, where=[]):
        """
        Возвращает sql строку типа "UPDATE" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param values: словарь значений
        :param where: list список условий
        :return: string
        """
        raise NotImplemented

    def as_insert_sql(self, table=None, values={}):
        """
        Возвращает sql строку типа "INSERT" для дальнейшего использования
        (execute метод)

        :param table: string имя таблицы
        :param values: словарь значений
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


class DataBaseSourse(Source):
    """
        Класс, описывающий тип источника "База данных"
    """
    type_source = "db"
    query = SqlQuery()

    def __init__(self, *args, **kwargs):
        super(DataBaseSourse, self).__init__(*args, **kwargs)
        # определяем параметры источника - БД
        try:
            # Инициализируем connector для работы с бд
            self.connector = self.get_connector(
                self.source_model.init_params
            )
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

            Возвращает данные в виде списка словарей:
            [
                {'id': 1, 'state':'N', ...},
                {'id': 2, 'state':'N', ...},
                ...
            ]
        """
        cursor = self.connector.cursor()
        cursor.execute(
            self.query.as_select_sql(*args, **kwargs)
        )
        return [
            dict(zip([col[0] for col in cursor.description], row))
            for row in cursor.fetchall()
        ]

    @transaction_atomic
    def update(self, *args, **kwargs):
        """
            Выполняет "update" запрос

            В **kwargs передаем:
                table - имя таблицы
                values - устанавливаемые значения
                where - условия выборки
        """
        self.connector.cursor().execute(
            self.query.as_update_sql(*args, **kwargs)
        )

    @transaction_atomic
    def insert(self, *args, **kwargs):
        """
            Выполняет "insert" запрос

            В **kwargs передаем:
                table - имя таблицы
                values - сохраняемые значения
        """
        self.connector.cursor().execute(
            self.query.as_insert_sql(*args, **kwargs)
        )

    def delete(self, *args, **kwargs):
        """
            Выполняет "delete" запрос

            В **kwargs передаем:
                table - имя таблицы
                where - условия выборки
        """
        return self.connector.cursor().execute(
            self.query.as_delete_sql(*args, **kwargs)
        )
