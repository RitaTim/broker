# -*- coding: utf-8 -*-

"""
    Данная реализация позволяет представить все необходимые Source'ы (источники
    и получатели) в виде моделей в базе данных.

    Естественно, что при запуске initial миграций (deploy проекта), данный код
    будет генерировать SQL ошибки.
"""


import warnings

from django.apps import AppConfig
from django.db.utils import ProgrammingError

from .helpers import get_data_sources


class ModuleSourcesExceptions(Exception):
    """
        Генерируется при ошибке при получении источников модуля
    """
    pass


class BrokerAppConfig(AppConfig):
    """
        Класс, анализирующий классы и параметры брокера при запуске проекта
    """
    name = 'broker'
    verbose_name = u'Анализ параметров брокера'

    def ready(self):
        """
            Находит все источники брокера и
            в соответствии с полученным списком обновляет таблицу бд
        """
        from models import Source
        # Получаем данные по всем источникам в модуле
        module_sources = get_data_sources()
        if not module_sources:
            raise ModuleSourcesExceptions('Sources in module were not found')
        module_sources_names = set(module_sources.keys())
        try:
            # Выбираем источники, которые уже есть в бд
            db_sources_names = set(
                Source.objects.all().values_list('source', flat=True)
            )

            # Удаляем источники, которых нет в модуле
            Source.objects.filter(
                source__in=(db_sources_names - module_sources_names)
            ).delete()

            # Добавляем источники, которых нет в бд
            Source.objects.bulk_create([
                Source(
                    source=source_name,
                    type_source=module_sources[source_name]['type']
                ) for source_name in (module_sources_names - db_sources_names)
            ])
        except ProgrammingError:
            warnings.warn('Only if deployed')
