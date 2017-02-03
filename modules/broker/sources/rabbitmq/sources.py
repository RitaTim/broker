# -*- coding: utf-8 -*-

from celery import signature

from broker.sources.rabbitmq import RabbitMQ
from broker.decorators.decorators import callback, signal


class MailerRabbitMq(RabbitMQ):
    """
        Источник для взаимодействия с проектом mailer через RabbitMq
    """
    @signal()
    def locked_domain(self):
        """
            Заблокировать домен
        """
        pass

    @callback()
    def update_user_status(self, *args, **kwargs):
        """
            Вызвать таск на блокировку домена
        """
        signature_task = signature('update_users_status', app=self.app)
        self.celery_settings.update(kwargs)
        signature_task.apply_async("", **self.celery_settings)


class MailerSNRRabbitMq(MailerRabbitMq):
    """
        Источник для взаимодействия с проектом mailer-snr через RabbitMq
    """
    pass


class MailerMebelRabbitMq(MailerRabbitMq):
    """
        Источник для взаимодействия с проектом mailer-mebel через RabbitMq
    """
    pass
