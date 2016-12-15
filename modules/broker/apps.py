# -*- coding: utf-8 -*-

import inspect

from django.apps import AppConfig


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
        from models import SourceModel
        from broker import sources as broker_sources

        # Получаем список имен источников модуля
        module_sources = set(
            name for name, source in inspect.getmembers(broker_sources)
            if getattr(source, 'is_proxy', None) == False
        )

        # Выбираем источники, которые уже есть в бд
        db_sources = set(
            SourceModel.objects.all().values_list('source', flat=True)
        )

        # Удаляем источники, которых нет в модуле
        SourceModel.objects.filter(source__in=(db_sources - module_sources)) \
            .delete()

        # Добавляем источники, которых нет в бд
        SourceModel.objects.bulk_create([
            SourceModel(source=name_source) for name_source
            in (module_sources - db_sources)
        ])
