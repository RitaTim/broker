# -*- coding: utf-8 -*-

from copy import deepcopy

from celery import Celery
from broker.sources import Source


class RabbitMQ(Source):
    """
        Класс источника RabbitMQ

        В init_params источников данного типа необходимо указывать параметры:
        {
            'app_name': <имя приложения>
            'broker_url': <BROKER_URL проекта>
        }
    """
    type_source = "rabbitmq"
    celery_settings = {
        "queue": "default",
        "serializer": "json",
    }

    def __init__(self, *args, **kwargs):
        super(RabbitMQ, self).__init__(*args, **kwargs)
        init_params = self.source_model.init_params
        self.app = Celery(
            init_params.get('app_name'), broker=init_params.get('broker_url')
        )

    def get_default_celery_settings(self, custom_celery_settings=None):
        """
            Возвращает конфигурацию для app.Celery
            :param custom_celery_settings: дополнительные параметры
        """
        result = deepcopy(self.celery_settings)
        if custom_celery_settings:
            result.update(custom_celery_settings)
        return result
