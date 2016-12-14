# -*- coding: utf-8 -*-

import json

from django.db import models
from django.contrib.postgres.fields import JSONField


class SourceModel(models.Model):
    """
        Модель для хранения информации об источниках
    """
    source = models.CharField("Тип источника", max_length=128)
    init_params = JSONField(default=json.dumps({}), null=True, blank=True)
