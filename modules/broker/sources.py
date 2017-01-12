# -*- coding: utf-8 -*-

from suds.client import Client, WebFault

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


class DataBaseSourse(Source):
    """
        Класс, описывающий тип источника "База данных"
    """
    type_source = "db"
    cursor = None

    def __init__(self, *args, **kwargs):
        super(DataBaseSourse, self).__init__(*args, **kwargs)
        # определяем параметры источника - БД
        try:
            db_alias = get_db_allias_for_source(self.source_model.source)
            self.cursor = settings.CONNECTIONS_SOURCES[db_alias].cursor()
        except Exception as e:
            raise DBConnectError(e.message)

    def select(self, table, fields=[], order_by=[], where={}):
        """
            Принимает:
                table - имя таблицы
                fields - список имен необходимых полей вида:
                    [field1, (field2, alias2), field3]
                where -
                order_by - список полей для сортировки вида:
                    [field1, -field2)]
                    по умолчанию сортировка по возрастанию

            Формирует sql запрос для select. Возвращает результат выборки
        """
        fields_formated = [
            "{} as {}".format(field[0], field[1])
            if isinstance(field, tuple) and len(field) == 2
            else field for field in fields
        ]

        query = "SELECT {fields} FROM {table}".format(
            fields=", ".join(fields_formated),
            table=table,
        )

        if where:
            query += " WHERE {filter_fields}".format(
                filter_fields=" AND ".join([
                    "{}{}".format(field, value)
                    for field, value in where.iteritems()
                ])
            )

        if order_by:
            order_by_qs = ", ".join([
                "{} DESC".format(field[1:])
                if field[0] == '-' else field for field in order_by
            ])
            query += " ORDER BY {}".format(order_by_qs)

        self.cursor.execute(query)
        return self.cursor.fetchall()


class MysqlDBSource(DataBaseSourse):
    """
        Класс mysql источника
    """
    def __init__(self, *args, **kwargs):
        super(MysqlDBSource, self).__init__(*args, **kwargs)
        # определяем параметры источника - mysql БД


class Wsdl(Source):
    """
        Класс источника Wsdl
    """
    type_source = "wsdl"
    wsdl_client = None

    def __init__(self, *args, **kwargs):
        super(Wsdl, self).__init__(*args, **kwargs)
        init_params = self.source_model.init_params
        try:
            url = init_params.pop('url')
            self.wsdl_client = Client(url, **init_params)
        except KeyError as e:
            raise WsdlConnectError(
                u"В параметрах wsdl источника {} не указан 'url'"
                .format(self.__class__.__name__)
            )

""" Инстансы источников """


class OneSWsdl(Wsdl):
    """
        Доступ к wsdl серверу
    """
    is_proxy = False

    @callback
    def get_report_equipment_repair_status(self, *args, **kwargs):
        """
            Возвращает отчет о статусе ремонта оборудования
            В kwargs должны быть следующие параметры:
            {
                'task_id': <id отчета>
                'uuid': <uuid отчета>,
                'start_date': <дата создания>,
                'end_date': <дата получения>,
                'email': <e-mail>
            }
        """
        result = self.wsdl_client.service.ReportEquipmentRepairStatus2(
            kwargs['task_id'], kwargs['uuid'], kwargs['start_date'],
            kwargs['end_date'], kwargs['email']
        )
        result['return'] = result['return'].decode('hex')
        return dict(result)


class KmClient(MysqlDBSource):
    """
        Класс источника KmClient
    """
    is_proxy = False

    def __init__(self, *args, **kwargs):
        super(KmClient, self).__init__(*args, **kwargs)

    @signal()
    def km_signal_1(self):
        pass

    @signal()
    def km_signal_2(self):
        pass

    def km_signal_3(self):
        pass

    @callback
    def km_callback_1(self, *args, **kwargs):
        pass


class IDA2(MysqlDBSource):
    """
        Класс источника IDA2
    """
    is_proxy = False

    def __init__(self, *args, **kwargs):
        super(IDA2, self).__init__(*args, **kwargs)

    @signal()
    def ida_signal_1(self):
        pass

    def ida_signal_2(self):
        pass

    @callback
    def ida_callback_1(self, *args, **kwargs):
        # Работать с бд источника можно через ее коннектор
        self.select(
            fields=['testcol1', 't3'],
            table="test",
            where={'testcol1': '>40', 't3': '="sven"'},
            order_by=['-testcol1']
        )

        import random
        fortuna = random.randint(0, 100)
        print 'ida_callback_1 - {0}'.format(fortuna)
        if fortuna <= 60:
            raise SpecialException('ha ha ha HA')
        return 'All is well!'

    @callback
    def ida_callback_2(self, *args, **kwargs):
        print 'ida_callback_2'


class SpecialException(Exception):
    pass


class DBConnectError(Exception):
    """
        Исключение при невозможности подключиться к базе данных источника
    """
    pass


class WsdlConnectError(Exception):
    """
        Исключение при невозможности подключиться к wsdl серверу
    """
    pass
