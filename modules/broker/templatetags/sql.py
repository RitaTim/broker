# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter(name='prepare_fields')
def prepare_fields(fields):
    return [field if isinstance(field, (list, tuple)) else (field, field)
            for field in fields]
